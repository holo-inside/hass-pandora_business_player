# Pandora for Business Player for Home Assistant

This is a custom integration for Home Assistant that provides a media player for Pandora for Business (tested running on a Mood Media ProFusion iO device).

## Installation

### HACS (Recommended)
1. Open HACS in your Home Assistant instance
2. Go to the Integrations tab
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository: `https://github.com/yourusername/hass-pandora_business_player`
6. Select "Integration" as the category
7. Click "Add"
8. Find "Pandora Business Player" in the list and click "Install"
9. Restart Home Assistant

### Manual Installation
1. Copy the `custom_components/pandora_business_player` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

The integration can be configured through the Home Assistant UI:

1. Go to Settings > Devices & Services
2. Click "Add Integration"
3. Search for "Pandora Business Player"
4. Enter your Pandora Business credentials:
   - Username
   - Password
   - Location (URL of your Pandora Business server)

## Features

- Control Pandora Business playback
- Adjust volume
- Mute/unmute
- Select different stations
- Play/Pause/Stop controls
- Skip tracks
- Display current track information

## Development

This integration is under active development. Future updates will include:

- Actual Pandora Business API integration
- More station management features
- Enhanced playback controls

## Support

For support, please open an issue in the GitHub repository. 