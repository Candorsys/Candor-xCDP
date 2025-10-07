"""
GitHub Version Notifier for Candor Coding Platform (CDP)
Automatically checks for new releases on GitHub and notifies users
"""

import requests
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging

# PyQt6 imports for GUI notifications
try:
    from PyQt6.QtWidgets import (QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, 
                                 QLabel, QPushButton, QCheckBox, QTextEdit,
                                 QDialog, QApplication, QSystemTrayIcon)
    from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QUrl
    from PyQt6.QtGui import QIcon, QFont, QPixmap
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("PyQt6 not available - GUI notifications disabled")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ReleaseInfo:
    """Data class for release information"""
    version: str
    tag_name: str
    name: str
    body: str
    published_at: str
    download_url: str
    is_prerelease: bool
    is_draft: bool

@dataclass
class NotificationSettings:
    """Configuration for notification behavior"""
    check_interval_hours: int = 24
    notify_on_prerelease: bool = False
    notify_on_draft: bool = False
    auto_download: bool = False
    show_changelog: bool = True
    github_token: Optional[str] = None
    repository_owner: str = ""
    repository_name: str = ""

class GitHubVersionChecker(QThread if PYQT_AVAILABLE else object):
    """Thread-safe GitHub version checker"""
    
    # Signals for PyQt integration
    if PYQT_AVAILABLE:
        version_found = pyqtSignal(object)  # ReleaseInfo
        check_completed = pyqtSignal(bool, str)  # success, message
        error_occurred = pyqtSignal(str)
    
    def __init__(self, settings: NotificationSettings):
        if PYQT_AVAILABLE:
            super().__init__()
        self.settings = settings
        self.current_version = self._get_current_version()
        self.last_check_file = Path("last_version_check.json")
        
    def _get_current_version(self) -> str:
        """Get current application version"""
        try:
            # Try to read from version file
            version_file = Path("version.txt")
            if version_file.exists():
                return version_file.read_text().strip()
            
            # Try to read from package.json if it exists
            package_json = Path("package.json")
            if package_json.exists():
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    return data.get("version", "1.0.0")
            
            # Default version
            return "1.0.0"
        except Exception as e:
            logger.warning(f"Could not determine current version: {e}")
            return "1.0.0"
    
    def _should_check_for_updates(self) -> bool:
        """Check if enough time has passed since last check"""
        if not self.last_check_file.exists():
            return True
            
        try:
            with open(self.last_check_file, 'r') as f:
                data = json.load(f)
                last_check = datetime.fromisoformat(data.get('last_check', '2000-01-01'))
                check_interval = timedelta(hours=self.settings.check_interval_hours)
                return datetime.now() - last_check > check_interval
        except Exception as e:
            logger.warning(f"Error reading last check file: {e}")
            return True
    
    def _update_last_check_time(self):
        """Update the last check timestamp"""
        try:
            data = {
                'last_check': datetime.now().isoformat(),
                'current_version': self.current_version
            }
            with open(self.last_check_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error updating last check time: {e}")
    
    def _make_github_request(self, url: str) -> Optional[Dict]:
        """Make authenticated request to GitHub API"""
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Candor-CDP-Version-Checker/1.0'
        }
        
        if self.settings.github_token:
            headers['Authorization'] = f'token {self.settings.github_token}'
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed: {e}")
            if PYQT_AVAILABLE:
                self.error_occurred.emit(f"Failed to connect to GitHub: {e}")
            return None
    
    def _parse_release_info(self, release_data: Dict) -> ReleaseInfo:
        """Parse GitHub release data into ReleaseInfo object"""
        return ReleaseInfo(
            version=release_data.get('tag_name', '').lstrip('v'),
            tag_name=release_data.get('tag_name', ''),
            name=release_data.get('name', ''),
            body=release_data.get('body', ''),
            published_at=release_data.get('published_at', ''),
            download_url=release_data.get('html_url', ''),
            is_prerelease=release_data.get('prerelease', False),
            is_draft=release_data.get('draft', False)
        )
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compare two version strings. Returns -1, 0, or 1"""
        def version_tuple(v):
            return tuple(map(int, v.split('.')))
        
        try:
            v1_tuple = version_tuple(version1)
            v2_tuple = version_tuple(version2)
            
            if v1_tuple < v2_tuple:
                return -1
            elif v1_tuple > v2_tuple:
                return 1
            else:
                return 0
        except ValueError:
            # Fallback to string comparison
            if version1 < version2:
                return -1
            elif version1 > version2:
                return 1
            else:
                return 0
    
    def check_for_updates(self) -> Optional[ReleaseInfo]:
        """Check for new releases on GitHub"""
        if not self.settings.repository_owner or not self.settings.repository_name:
            logger.error("Repository owner and name must be configured")
            if PYQT_AVAILABLE:
                self.error_occurred.emit("Repository configuration missing")
            return None
        
        if not self._should_check_for_updates():
            logger.info("Skipping update check - too soon since last check")
            return None
        
        logger.info(f"Checking for updates in {self.settings.repository_owner}/{self.settings.repository_name}")
        
        # GitHub API endpoint for releases
        url = f"https://api.github.com/repos/{self.settings.repository_owner}/{self.settings.repository_name}/releases"
        
        releases_data = self._make_github_request(url)
        if not releases_data:
            return None
        
        # Find the latest release that meets our criteria
        for release_data in releases_data:
            release_info = self._parse_release_info(release_data)
            
            # Skip prereleases and drafts based on settings
            if release_info.is_prerelease and not self.settings.notify_on_prerelease:
                continue
            if release_info.is_draft and not self.settings.notify_on_draft:
                continue
            
            # Compare versions
            if self._compare_versions(self.current_version, release_info.version) < 0:
                logger.info(f"New version found: {release_info.version} (current: {self.current_version})")
                self._update_last_check_time()
                return release_info
        
        logger.info("No new versions found")
        self._update_last_check_time()
        return None
    
    def run(self):
        """Thread run method for PyQt integration"""
        if not PYQT_AVAILABLE:
            return
        
        try:
            release_info = self.check_for_updates()
            if release_info:
                self.version_found.emit(release_info)
                self.check_completed.emit(True, f"New version {release_info.version} available")
            else:
                self.check_completed.emit(True, "No updates available")
        except Exception as e:
            logger.error(f"Error in version check thread: {e}")
            self.error_occurred.emit(str(e))
            self.check_completed.emit(False, str(e))

class VersionNotificationDialog(QDialog if PYQT_AVAILABLE else object):
    """Dialog for displaying version update notifications"""
    
    def __init__(self, release_info: ReleaseInfo, settings: NotificationSettings):
        if not PYQT_AVAILABLE:
            return
        super().__init__()
        self.release_info = release_info
        self.settings = settings
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the notification dialog UI"""
        self.setWindowTitle("New Version Available")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("🚀 New Version Available!")
        header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Version info
        version_label = QLabel(f"Version {self.release_info.version} is now available")
        version_label.setFont(QFont("Arial", 12))
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        # Release name
        if self.release_info.name:
            name_label = QLabel(f"'{self.release_info.name}'")
            name_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(name_label)
        
        # Changelog
        if self.settings.show_changelog and self.release_info.body:
            changelog_label = QLabel("What's New:")
            changelog_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            layout.addWidget(changelog_label)
            
            changelog_text = QTextEdit()
            changelog_text.setPlainText(self.release_info.body)
            changelog_text.setMaximumHeight(150)
            changelog_text.setReadOnly(True)
            layout.addWidget(changelog_text)
        
        # Options
        self.dont_notify_checkbox = QCheckBox("Don't notify me about this version again")
        layout.addWidget(self.dont_notify_checkbox)
        
        self.auto_check_checkbox = QCheckBox("Check for updates automatically")
        self.auto_check_checkbox.setChecked(True)
        layout.addWidget(self.auto_check_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.download_button = QPushButton("Download Now")
        self.download_button.setStyleSheet("QPushButton { background-color: #007ACC; color: white; font-weight: bold; }")
        self.download_button.clicked.connect(self.download_release)
        
        self.later_button = QPushButton("Remind Me Later")
        self.later_button.clicked.connect(self.accept)
        
        self.skip_button = QPushButton("Skip This Version")
        self.skip_button.clicked.connect(self.skip_version)
        
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.later_button)
        button_layout.addWidget(self.skip_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def download_release(self):
        """Open download URL in browser"""
        try:
            import webbrowser
            webbrowser.open(self.release_info.download_url)
            self.accept()
        except Exception as e:
            logger.error(f"Error opening download URL: {e}")
    
    def skip_version(self):
        """Skip this version and don't notify again"""
        # Add version to skip list
        skip_file = Path("skipped_versions.json")
        skipped_versions = []
        
        if skip_file.exists():
            try:
                with open(skip_file, 'r') as f:
                    skipped_versions = json.load(f)
            except Exception:
                pass
        
        if self.release_info.version not in skipped_versions:
            skipped_versions.append(self.release_info.version)
            
            try:
                with open(skip_file, 'w') as f:
                    json.dump(skipped_versions, f, indent=2)
            except Exception as e:
                logger.error(f"Error saving skipped versions: {e}")
        
        self.accept()

class GitHubVersionNotifier:
    """Main class for GitHub version notification system"""
    
    def __init__(self, settings: NotificationSettings):
        self.settings = settings
        self.checker_thread = None
        self.timer = None
        self.parent_widget = None
        
        if PYQT_AVAILABLE:
            self._setup_timer()
    
    def _setup_timer(self):
        """Setup periodic check timer"""
        if not PYQT_AVAILABLE:
            return
            
        self.timer = QTimer()
        self.timer.timeout.connect(self.start_version_check)
        # Convert hours to milliseconds
        interval_ms = self.settings.check_interval_hours * 60 * 60 * 1000
        self.timer.start(interval_ms)
    
    def set_parent_widget(self, parent_widget):
        """Set parent widget for dialogs"""
        self.parent_widget = parent_widget
    
    def start_version_check(self):
        """Start version check in background thread"""
        if not PYQT_AVAILABLE:
            # Fallback for non-PyQt environments
            release_info = self.checker_thread.check_for_updates()
            if release_info:
                self._handle_new_version(release_info)
            return
        
        if self.checker_thread and self.checker_thread.isRunning():
            return
        
        self.checker_thread = GitHubVersionChecker(self.settings)
        self.checker_thread.version_found.connect(self._handle_new_version)
        self.checker_thread.check_completed.connect(self._handle_check_completed)
        self.checker_thread.error_occurred.connect(self._handle_error)
        self.checker_thread.start()
    
    def _handle_new_version(self, release_info: ReleaseInfo):
        """Handle new version found"""
        logger.info(f"New version notification: {release_info.version}")
        
        if not PYQT_AVAILABLE:
            print(f"New version {release_info.version} available: {release_info.download_url}")
            return
        
        # Check if this version was skipped
        skip_file = Path("skipped_versions.json")
        skipped_versions = []
        
        if skip_file.exists():
            try:
                with open(skip_file, 'r') as f:
                    skipped_versions = json.load(f)
            except Exception:
                pass
        
        if release_info.version in skipped_versions:
            logger.info(f"Skipping notification for version {release_info.version}")
            return
        
        # Show notification dialog
        dialog = VersionNotificationDialog(release_info, self.settings)
        if self.parent_widget:
            dialog.setParent(self.parent_widget)
        dialog.exec()
    
    def _handle_check_completed(self, success: bool, message: str):
        """Handle version check completion"""
        logger.info(f"Version check completed: {message}")
    
    def _handle_error(self, error_message: str):
        """Handle version check error"""
        logger.error(f"Version check error: {error_message}")
        
        if not PYQT_AVAILABLE:
            return
        
        # Show error message box
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Version Check Error")
        msg_box.setText("Failed to check for updates")
        msg_box.setDetailedText(error_message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        if self.parent_widget:
            msg_box.setParent(self.parent_widget)
        msg_box.exec()
    
    def stop(self):
        """Stop the version notifier"""
        if self.timer:
            self.timer.stop()
        
        if self.checker_thread and self.checker_thread.isRunning():
            self.checker_thread.quit()
            self.checker_thread.wait()

def create_default_settings() -> NotificationSettings:
    """Create default notification settings"""
    return NotificationSettings(
        check_interval_hours=24,
        notify_on_prerelease=False,
        notify_on_draft=False,
        auto_download=False,
        show_changelog=True,
        github_token=None,
        repository_owner="your-username",  # Update this
        repository_name="your-repo"        # Update this
    )

def load_settings_from_file(file_path: str = "version_notifier_settings.json") -> NotificationSettings:
    """Load settings from JSON file"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                return NotificationSettings(**data)
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
    
    return create_default_settings()

def save_settings_to_file(settings: NotificationSettings, file_path: str = "version_notifier_settings.json"):
    """Save settings to JSON file"""
    try:
        data = {
            'check_interval_hours': settings.check_interval_hours,
            'notify_on_prerelease': settings.notify_on_prerelease,
            'notify_on_draft': settings.notify_on_draft,
            'auto_download': settings.auto_download,
            'show_changelog': settings.show_changelog,
            'github_token': settings.github_token,
            'repository_owner': settings.repository_owner,
            'repository_name': settings.repository_name
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving settings: {e}")

# Example usage and integration
if __name__ == "__main__":
    # Example usage
    settings = create_default_settings()
    settings.repository_owner = "your-github-username"
    settings.repository_name = "your-repository-name"
    
    # Save settings
    save_settings_to_file(settings)
    
    # Create notifier
    notifier = GitHubVersionNotifier(settings)
    
    # Start checking
    notifier.start_version_check()
    
    if PYQT_AVAILABLE:
        # Keep the application running
        app = QApplication(sys.argv)
        app.exec()
