# GitHub Version Notifier for Candor Coding Platform

This module provides automatic version checking and user notifications when new releases are available on GitHub. It integrates seamlessly with the Candor Coding Platform (CDP) application.

## Features

- 🔍 **Automatic Version Checking**: Periodically checks GitHub for new releases
- 🔔 **User Notifications**: Shows beautiful dialog notifications for new versions
- ⚙️ **Configurable Settings**: Customizable check intervals and notification preferences
- 🚫 **Skip Versions**: Users can skip specific versions they don't want to update to
- 📝 **Changelog Display**: Shows release notes and changelog in notifications
- 🔐 **GitHub Token Support**: Optional authentication for higher API rate limits
- 🎨 **PyQt6 Integration**: Native GUI integration with the CDP application

## Files Overview

- `github_version_notifier.py` - Core version checking and notification system
- `github_version_integration.py` - Integration module for CDP main application
- `setup_version_notifier.py` - Interactive setup and configuration script
- `config/version_notifier_settings.json` - Configuration file
- `version.txt` - Current application version file

## Quick Setup

1. **Run the setup script**:
   ```bash
   python setup_version_notifier.py
   ```

2. **Configure your repository**:
   - Enter your GitHub username/organization
   - Enter your repository name
   - Optionally add a GitHub token for higher rate limits
   - Set notification preferences

3. **Integrate with your application**:
   ```python
   from github_version_integration import integrate_with_main_window
   
   class CCPMainWindow(QMainWindow):
       def __init__(self):
           super().__init__()
           # ... your existing code ...
           
           # Add version notifier
           self.version_integration = integrate_with_main_window(self)
   ```

## Configuration Options

The version notifier can be configured through the `version_notifier_settings.json` file:

```json
{
  "check_interval_hours": 24,
  "notify_on_prerelease": false,
  "notify_on_draft": false,
  "auto_download": false,
  "show_changelog": true,
  "github_token": null,
  "repository_owner": "your-github-username",
  "repository_name": "your-repository-name"
}
```

### Settings Explained

- `check_interval_hours`: How often to check for updates (1-168 hours)
- `notify_on_prerelease`: Whether to notify about prerelease versions
- `notify_on_draft`: Whether to notify about draft releases
- `auto_download`: Whether to automatically open download page
- `show_changelog`: Whether to display release notes in notifications
- `github_token`: Optional GitHub personal access token
- `repository_owner`: GitHub username or organization name
- `repository_name`: Repository name

## Usage Examples

### Basic Integration

```python
from github_version_integration import integrate_with_main_window

# In your main window initialization
self.version_integration = integrate_with_main_window(self)
```

### Manual Version Check

```python
# Trigger immediate version check
if hasattr(self, 'version_integration') and self.version_integration:
    self.version_integration.check_now()
```

### Update Settings Programmatically

```python
# Update repository settings
self.version_integration.update_settings(
    repository_owner="new-owner",
    repository_name="new-repo",
    check_interval_hours=12,
    notify_on_prerelease=True
)
```

### Standalone Usage

```python
# Run as standalone script
python github_version_notifier.py
```

## GitHub Token Setup

For higher API rate limits and access to private repositories:

1. Go to [GitHub Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. Click "Generate new token"
3. Select appropriate scopes:
   - `public_repo` for public repositories
   - `repo` for private repositories
4. Copy the token and paste it during setup

## Version File

The system reads the current version from `version.txt`. Create this file with your current version:

```
1.0.0
```

## Notification Dialog

When a new version is found, users see a notification dialog with:

- Version number and release name
- Changelog/release notes
- Download button (opens GitHub release page)
- "Remind Me Later" option
- "Skip This Version" option
- Settings to disable future notifications

## Error Handling

The system includes comprehensive error handling:

- Network connectivity issues
- GitHub API rate limiting
- Invalid repository configuration
- Missing version files
- PyQt6 availability checks

## Dependencies

- `requests` - For GitHub API calls
- `PyQt6` - For GUI notifications (optional)
- `json` - For configuration management
- `pathlib` - For file operations

## Installation

1. Ensure dependencies are installed:
   ```bash
   pip install requests PyQt6
   ```

2. Copy the version notifier files to your project directory

3. Run the setup script:
   ```bash
   python setup_version_notifier.py
   ```

## Testing

Test your configuration:

```bash
python setup_version_notifier.py
# Choose option 2: Test current configuration
```

Or test manually:

```python
from github_version_notifier import GitHubVersionNotifier, create_default_settings

settings = create_default_settings()
settings.repository_owner = "your-username"
settings.repository_name = "your-repo"

notifier = GitHubVersionNotifier(settings)
notifier.start_version_check()
```

## Troubleshooting

### Common Issues

1. **"PyQt6 not available"**: Install PyQt6 or run without GUI notifications
2. **"Repository configuration missing"**: Run setup script to configure repository
3. **"GitHub API request failed"**: Check network connection and repository name
4. **"No new versions found"**: Verify current version in `version.txt`

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Notes

- GitHub tokens are stored in plain text - secure your configuration file
- The system only reads from GitHub, never writes
- No sensitive data is transmitted to external services
- All API calls use HTTPS

## License

This module is part of the Candor Coding Platform and follows the same license terms.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Run the test configuration
3. Review the error logs
4. Contact the CDP development team
