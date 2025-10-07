"""
Integration module for GitHub Version Notifier with Candor Coding Platform
This module shows how to integrate the version notifier with the main CDP application
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from github_version_notifier import (
        GitHubVersionNotifier, 
        NotificationSettings, 
        create_default_settings,
        load_settings_from_file,
        save_settings_to_file,
        PYQT_AVAILABLE
    )
except ImportError as e:
    print(f"Error importing GitHub version notifier: {e}")
    PYQT_AVAILABLE = False

class CDPVersionNotifierIntegration:
    """Integration class for CDP main application"""
    
    def __init__(self, main_window=None):
        self.main_window = main_window
        self.version_notifier = None
        self.settings = None
        self._load_settings()
        self._setup_notifier()
    
    def _load_settings(self):
        """Load version notifier settings"""
        try:
            # Try to load from config directory
            config_dir = Path("config")
            if config_dir.exists():
                settings_file = config_dir / "version_notifier_settings.json"
                self.settings = load_settings_from_file(str(settings_file))
            else:
                # Fallback to default settings
                self.settings = create_default_settings()
                
            # Update with CDP-specific defaults if not configured
            if not self.settings.repository_owner or self.settings.repository_owner == "your-username":
                self.settings.repository_owner = "candor-cdp"  # Update with actual repo owner
                self.settings.repository_name = "candor-coding-platform"  # Update with actual repo name
                
        except Exception as e:
            print(f"Error loading version notifier settings: {e}")
            self.settings = create_default_settings()
    
    def _setup_notifier(self):
        """Setup the version notifier"""
        if not PYQT_AVAILABLE:
            print("PyQt6 not available - version notifier disabled")
            return
        
        try:
            self.version_notifier = GitHubVersionNotifier(self.settings)
            
            # Set parent widget for dialogs
            if self.main_window:
                self.version_notifier.set_parent_widget(self.main_window)
                
            print("GitHub version notifier initialized successfully")
            
        except Exception as e:
            print(f"Error setting up version notifier: {e}")
    
    def start_version_checking(self):
        """Start automatic version checking"""
        if self.version_notifier:
            self.version_notifier.start_version_check()
            print("Version checking started")
        else:
            print("Version notifier not available")
    
    def stop_version_checking(self):
        """Stop automatic version checking"""
        if self.version_notifier:
            self.version_notifier.stop()
            print("Version checking stopped")
    
    def check_now(self):
        """Manually trigger a version check"""
        if self.version_notifier:
            self.version_notifier.start_version_check()
            print("Manual version check triggered")
        else:
            print("Version notifier not available")
    
    def update_settings(self, **kwargs):
        """Update notifier settings"""
        if not self.settings:
            return
        
        for key, value in kwargs.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
        
        # Save updated settings
        try:
            config_dir = Path("config")
            config_dir.mkdir(exist_ok=True)
            settings_file = config_dir / "version_notifier_settings.json"
            save_settings_to_file(self.settings, str(settings_file))
            print("Settings updated and saved")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get_current_settings(self) -> dict:
        """Get current settings as dictionary"""
        if not self.settings:
            return {}
        
        return {
            'check_interval_hours': self.settings.check_interval_hours,
            'notify_on_prerelease': self.settings.notify_on_prerelease,
            'notify_on_draft': self.settings.notify_on_draft,
            'auto_download': self.settings.auto_download,
            'show_changelog': self.settings.show_changelog,
            'repository_owner': self.settings.repository_owner,
            'repository_name': self.settings.repository_name,
            'github_token': self.settings.github_token
        }

def integrate_with_main_window(main_window):
    """
    Integration function to add version notifier to main window
    
    Usage in main_window.py:
    from github_version_integration import integrate_with_main_window
    integrate_with_main_window(self)
    """
    if not PYQT_AVAILABLE:
        print("PyQt6 not available - cannot integrate version notifier")
        return None
    
    try:
        # Create integration instance
        integration = CDPVersionNotifierIntegration(main_window)
        
        # Add version checking to application startup
        integration.start_version_checking()
        
        # Add menu items for version checking
        if hasattr(main_window, 'menu_manager') and main_window.menu_manager:
            _add_version_menu_items(main_window, integration)
        
        print("Version notifier integrated with main window")
        return integration
        
    except Exception as e:
        print(f"Error integrating version notifier: {e}")
        return None

def _add_version_menu_items(main_window, integration):
    """Add version-related menu items to the main window"""
    try:
        from PyQt6.QtWidgets import QAction
        from PyQt6.QtCore import QKeySequence
        
        # Get the Help menu or create it
        help_menu = None
        if hasattr(main_window.menu_manager, 'menus'):
            help_menu = main_window.menu_manager.menus.get('Help')
        
        if help_menu:
            # Add separator
            help_menu.addSeparator()
            
            # Check for updates action
            check_updates_action = QAction("Check for Updates", main_window)
            check_updates_action.setShortcut(QKeySequence("Ctrl+Shift+U"))
            check_updates_action.triggered.connect(integration.check_now)
            help_menu.addAction(check_updates_action)
            
            # Version settings action
            version_settings_action = QAction("Update Settings", main_window)
            version_settings_action.triggered.connect(lambda: _show_settings_dialog(main_window, integration))
            help_menu.addAction(version_settings_action)
            
            print("Version menu items added to Help menu")
        
    except Exception as e:
        print(f"Error adding version menu items: {e}")

def _show_settings_dialog(main_window, integration):
    """Show version notifier settings dialog"""
    try:
        from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                                   QLineEdit, QSpinBox, QCheckBox, QPushButton,
                                   QLabel, QGroupBox)
        
        dialog = QDialog(main_window)
        dialog.setWindowTitle("Version Notifier Settings")
        dialog.setModal(True)
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Repository settings group
        repo_group = QGroupBox("Repository Settings")
        repo_layout = QFormLayout()
        
        owner_edit = QLineEdit(integration.settings.repository_owner)
        name_edit = QLineEdit(integration.settings.repository_name)
        token_edit = QLineEdit(integration.settings.github_token or "")
        token_edit.setEchoMode(QLineEdit.EchoMode.Password)
        
        repo_layout.addRow("Repository Owner:", owner_edit)
        repo_layout.addRow("Repository Name:", name_edit)
        repo_layout.addRow("GitHub Token (optional):", token_edit)
        
        repo_group.setLayout(repo_layout)
        layout.addWidget(repo_group)
        
        # Notification settings group
        notif_group = QGroupBox("Notification Settings")
        notif_layout = QFormLayout()
        
        interval_spin = QSpinBox()
        interval_spin.setRange(1, 168)  # 1 hour to 1 week
        interval_spin.setValue(integration.settings.check_interval_hours)
        interval_spin.setSuffix(" hours")
        
        prerelease_check = QCheckBox()
        prerelease_check.setChecked(integration.settings.notify_on_prerelease)
        
        draft_check = QCheckBox()
        draft_check.setChecked(integration.settings.notify_on_draft)
        
        changelog_check = QCheckBox()
        changelog_check.setChecked(integration.settings.show_changelog)
        
        notif_layout.addRow("Check Interval:", interval_spin)
        notif_layout.addRow("Notify on Prereleases:", prerelease_check)
        notif_layout.addRow("Notify on Drafts:", draft_check)
        notif_layout.addRow("Show Changelog:", changelog_check)
        
        notif_group.setLayout(notif_layout)
        layout.addWidget(notif_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(lambda: _save_settings_and_close(
            dialog, integration, owner_edit.text(), name_edit.text(),
            token_edit.text(), interval_spin.value(), prerelease_check.isChecked(),
            draft_check.isChecked(), changelog_check.isChecked()
        ))
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        dialog.exec()
        
    except Exception as e:
        print(f"Error showing settings dialog: {e}")

def _save_settings_and_close(dialog, integration, owner, name, token, interval, prerelease, draft, changelog):
    """Save settings and close dialog"""
    try:
        integration.update_settings(
            repository_owner=owner,
            repository_name=name,
            github_token=token if token else None,
            check_interval_hours=interval,
            notify_on_prerelease=prerelease,
            notify_on_draft=draft,
            show_changelog=changelog
        )
        dialog.accept()
    except Exception as e:
        print(f"Error saving settings: {e}")

# Standalone usage example
if __name__ == "__main__":
    print("CDP Version Notifier Integration")
    print("This module integrates the GitHub version notifier with the CDP application")
    print("\nTo use in your main application:")
    print("1. Import: from github_version_integration import integrate_with_main_window")
    print("2. Call: integration = integrate_with_main_window(self)")
    print("3. The notifier will start automatically")
    
    # Example of standalone usage
    if PYQT_AVAILABLE:
        try:
            from PyQt6.QtWidgets import QApplication
            
            app = QApplication(sys.argv)
            integration = CDPVersionNotifierIntegration()
            integration.start_version_checking()
            
            print("Version notifier started. Press Ctrl+C to stop.")
            app.exec()
            
        except KeyboardInterrupt:
            print("\nStopping version notifier...")
            if integration:
                integration.stop_version_checking()
        except Exception as e:
            print(f"Error in standalone mode: {e}")
    else:
        print("PyQt6 not available - cannot run standalone example")
