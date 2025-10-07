"""
Setup script for GitHub Version Notifier
This script helps configure the version notifier for your GitHub repository
"""

import json
import os
from pathlib import Path

def setup_version_notifier():
    """Interactive setup for version notifier"""
    print("🚀 GitHub Version Notifier Setup")
    print("=" * 40)
    
    # Get repository information
    print("\n1. GitHub Repository Configuration")
    print("-" * 30)
    
    owner = input("Enter GitHub repository owner/username: ").strip()
    if not owner:
        print("❌ Repository owner is required!")
        return False
    
    repo_name = input("Enter repository name: ").strip()
    if not repo_name:
        print("❌ Repository name is required!")
        return False
    
    # Optional GitHub token
    print("\n2. GitHub Token (Optional)")
    print("-" * 25)
    print("A GitHub token allows for higher API rate limits.")
    print("You can create one at: https://github.com/settings/tokens")
    print("Required scopes: public_repo (for public repos) or repo (for private repos)")
    
    token = input("Enter GitHub token (or press Enter to skip): ").strip()
    if not token:
        token = None
    
    # Notification preferences
    print("\n3. Notification Preferences")
    print("-" * 28)
    
    try:
        interval = int(input("Check interval in hours (default: 24): ") or "24")
        if interval < 1:
            interval = 24
    except ValueError:
        interval = 24
    
    prerelease = input("Notify about prereleases? (y/N): ").lower().startswith('y')
    draft = input("Notify about draft releases? (y/N): ").lower().startswith('y')
    changelog = input("Show changelog in notifications? (Y/n): ").lower() != 'n'
    
    # Create settings
    settings = {
        "check_interval_hours": interval,
        "notify_on_prerelease": prerelease,
        "notify_on_draft": draft,
        "auto_download": False,
        "show_changelog": changelog,
        "github_token": token,
        "repository_owner": owner,
        "repository_name": repo_name
    }
    
    # Save settings
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    settings_file = config_dir / "version_notifier_settings.json"
    
    try:
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        
        print(f"\n✅ Settings saved to: {settings_file}")
        
        # Create version file if it doesn't exist
        version_file = Path("version.txt")
        if not version_file.exists():
            current_version = input("\nEnter current application version (default: 1.0.0): ").strip() or "1.0.0"
            version_file.write_text(current_version)
            print(f"✅ Version file created: {version_file}")
        
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Update your main application to integrate the version notifier")
        print("2. Test the integration by running: python github_version_notifier.py")
        print("3. The notifier will automatically check for updates based on your settings")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving settings: {e}")
        return False

def test_configuration():
    """Test the current configuration"""
    print("🧪 Testing Version Notifier Configuration")
    print("=" * 40)
    
    try:
        from github_version_notifier import load_settings_from_file, GitHubVersionChecker
        
        # Load settings
        config_file = Path("config/version_notifier_settings.json")
        if not config_file.exists():
            print("❌ Configuration file not found. Run setup first.")
            return False
        
        settings = load_settings_from_file(str(config_file))
        
        print(f"Repository: {settings.repository_owner}/{settings.repository_name}")
        print(f"Check interval: {settings.check_interval_hours} hours")
        print(f"Notify on prereleases: {settings.notify_on_prerelease}")
        print(f"Notify on drafts: {settings.notify_on_draft}")
        print(f"Show changelog: {settings.show_changelog}")
        print(f"GitHub token: {'Set' if settings.github_token else 'Not set'}")
        
        # Test GitHub API connection
        print("\n🔍 Testing GitHub API connection...")
        checker = GitHubVersionChecker(settings)
        release_info = checker.check_for_updates()
        
        if release_info:
            print(f"✅ Found release: {release_info.version}")
            print(f"   Name: {release_info.name}")
            print(f"   Published: {release_info.published_at}")
        else:
            print("ℹ️  No new releases found (or API connection failed)")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def show_usage_examples():
    """Show usage examples"""
    print("📖 Usage Examples")
    print("=" * 20)
    
    print("\n1. Basic Integration:")
    print("""
# In your main_window.py or main application file:
from github_version_integration import integrate_with_main_window

class CCPMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # ... your existing initialization code ...
        
        # Add version notifier integration
        self.version_integration = integrate_with_main_window(self)
    """)
    
    print("\n2. Manual Version Check:")
    print("""
# Check for updates manually:
if hasattr(self, 'version_integration') and self.version_integration:
    self.version_integration.check_now()
    """)
    
    print("\n3. Update Settings Programmatically:")
    print("""
# Update repository settings:
self.version_integration.update_settings(
    repository_owner="your-username",
    repository_name="your-repo",
    check_interval_hours=12
)
    """)
    
    print("\n4. Standalone Usage:")
    print("""
# Run as standalone script:
python github_version_notifier.py
    """)

def main():
    """Main setup function"""
    print("GitHub Version Notifier Setup & Configuration")
    print("=" * 50)
    
    while True:
        print("\nChoose an option:")
        print("1. Setup version notifier")
        print("2. Test current configuration")
        print("3. Show usage examples")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            setup_version_notifier()
        elif choice == "2":
            test_configuration()
        elif choice == "3":
            show_usage_examples()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main()
