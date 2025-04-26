# Pandora for Business Integration for Home Assistant

This integration allows you to control a local Mood Media ProFusion iO server running Pandora for Business from Home Assistant.

## Features

- Control playback (play/pause)
- Skip tracks
- Switch between stations
- Display current track information
- Show album art

## Installation

### HACS Installation

1. Open HACS in your Home Assistant instance
2. Go to the Integrations tab
3. Click the three dots in the top right and select "Custom repositories"
4. Add your repository URL
5. Select "Integration" as the category
6. Click "Add"
7. Find "Pandora for Business" in the list and click "Install"

### Manual Installation

1. Download the latest release
2. Extract the contents of the zip file
3. Copy the `custom_components/pandora_business` directory to your Home Assistant's `config/custom_components` directory
4. Restart Home Assistant

## Configuration

1. Go to Home Assistant's Configuration > Integrations
2. Click the "+" button to add a new integration
3. Search for "Pandora for Business"
4. Enter your Mood ProFusion iO server details:
   - Host: The IP address or hostname of your server
   - Username: Your Pandora for Business username
   - Password: Your Pandora for Business password

## Usage

Once configured, a media player entity should appear in Home Assistant. You can:
- Play/pause the current station
- Skip to the next track
- Switch between available stations
- See the current track information and album art

## Troubleshooting

If you encounter any issues:
1. Check your server's IP address and credentials
2. Ensure your Home Assistant instance can reach the server
3. Check the Home Assistant logs for any error messages

## Support

If you need help or have suggestions, please open an issue in the GitHub repository. 