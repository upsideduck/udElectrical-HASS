# UDElectrical Home Assistant Integration

This custom component integrates UDElectrical devices and services into Home Assistant.

## Features
- Sensor platform for UDElectrical data
- Configuration via Home Assistant UI
- Periodic data updates using a DataUpdateCoordinator

## Setup
1. Copy this folder to `config/custom_components/udelectrical/` in your Home Assistant config directory.
2. Restart Home Assistant.
3. Go to Settings > Devices & Services > Add Integration, search for "UDElectrical".
4. Enter your credentials and complete the setup.

## Requirements
- No additional Python packages required (uses built-in libraries or requirements specified in `manifest.json`).

## Configuration
All configuration is done via the Home Assistant UI. No YAML configuration is required or supported.

## Troubleshooting
- If the integration does not appear, ensure the directory and file permissions are correct.
- Check Home Assistant logs for errors.
- Ensure the `version` key is present in `manifest.json` (required for custom components).

## Support
For issues or feature requests, please open an issue on the repository where you obtained this custom component.
