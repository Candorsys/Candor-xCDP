"""
Quick test script for GitHub Version Notifier configuration
"""

import json
import sys
from pathlib import Path

def test_configuration():
    """Test the current configuration"""
    print("Testing GitHub Version Notifier Configuration")
    print("=" * 50)
    
    try:
        # Load settings
        config_file = Path("config/version_notifier_settings.json")
        if not config_file.exists():
            print("❌ Configuration file not found.")
            return False
        
        with open(config_file, 'r') as f:
            settings = json.load(f)
        
        print("Current Configuration:")
        print(f"   Repository: {settings['repository_owner']}/{settings['repository_name']}")
        print(f"   Check interval: {settings['check_interval_hours']} hours ({settings['check_interval_hours'] * 60} minutes)")
        print(f"   Notify on prereleases: {settings['notify_on_prerelease']}")
        print(f"   Notify on drafts: {settings['notify_on_draft']}")
        print(f"   Show changelog: {settings['show_changelog']}")
        print(f"   GitHub token: {'Set' if settings['github_token'] else 'Not set'}")
        
        # Test GitHub API connection
        print("\nTesting GitHub API connection...")
        
        import requests
        
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Candor-CDP-Version-Checker/1.0'
        }
        
        if settings['github_token']:
            headers['Authorization'] = f'token {settings["github_token"]}'
        
        url = f"https://api.github.com/repos/{settings['repository_owner']}/{settings['repository_name']}/releases"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            releases = response.json()
            print(f"Successfully connected to GitHub API")
            print(f"   Found {len(releases)} releases")
            
            if releases:
                latest = releases[0]
                print(f"   Latest release: {latest.get('tag_name', 'Unknown')}")
                print(f"   Published: {latest.get('published_at', 'Unknown')}")
                print(f"   Prerelease: {latest.get('prerelease', False)}")
                print(f"   Draft: {latest.get('draft', False)}")
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"GitHub API request failed: {e}")
            return False
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_configuration()
    
    if success:
        print("\nConfiguration test completed successfully!")
        print("\nNext steps:")
        print("1. Integrate with your main application:")
        print("   from github_version_integration import integrate_with_main_window")
        print("   self.version_integration = integrate_with_main_window(self)")
        print("\n2. Or run standalone:")
        print("   python github_version_notifier.py")
    else:
        print("\nConfiguration test failed. Please check your settings.")
        sys.exit(1)
