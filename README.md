# Crestron Touch Panel Integration for Home Assistant

Control Crestron TSW-series touch panels (TSW-1070, TSW-760, etc.) directly from Home Assistant via SSH.

## Features

- **Power Control**: Put panels into standby or wake them up
- **Brightness Control**: Adjust LCD brightness (0-100%)
- **Auto-polling**: Syncs brightness state every 30 seconds
- **Config Flow**: Easy setup via Home Assistant UI

## Supported Devices

Tested on:
- TSW-1070

Should work with other Crestron touch panels that support SSH console commands (TSW-760, TSW-1060, etc.)

## Installation

### HACS (Recommended)

1. Add this repository as a custom repository in HACS
2. Search for "Crestron Touch Panel" and install
3. Restart Home Assistant

### Manual

1. Copy the `custom_components/crestron_tpanel` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for "Crestron Touch Panel"
3. Enter:
   - **Name**: Friendly name for the tablet (e.g., "Kitchen Tablet")
   - **IP Address**: The panel's IP address
   - **Username**: SSH username
   - **Password**: SSH password
   - **Port**: SSH port (default: 22)

Repeat for each tablet.

## Entities

Each panel creates:

| Entity | Type | Description |
|--------|------|-------------|
| `switch.<name>_power` | Switch | ON = awake, OFF = standby |
| `number.<name>_brightness` | Number | LCD brightness (0-100%) |

## SSH Commands Used

This integration uses the Crestron console commands:

- `BRIGHTNESS` - Query/set LCD brightness
- `STANDBY` - Enter standby mode
- `STANDBY off` - Exit standby mode

## Requirements

- Crestron touch panel with SSH enabled
- SSH credentials with Programmer-level access (for brightness control)
- Network access from Home Assistant to the panel

## Troubleshooting

**Cannot connect**: 
- Verify SSH is enabled on the panel
- Check IP address and credentials
- Ensure firewall allows port 22 from HA to the panel

**Brightness not updating**:
- The integration polls every 30 seconds
- Check HA logs for SSH connection errors

## License

MIT

## Credits

Inspired by a Node-RED implementation that controlled Crestron panels via SSH.
