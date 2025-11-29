"""Constants for Crestron Touch Panel integration."""

DOMAIN = "crestron_tpanel"

# Configuration keys
CONF_HOST = "host"
CONF_PORT = "port"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_NAME = "name"

# Defaults
DEFAULT_PORT = 22
DEFAULT_SCAN_INTERVAL = 30

# SSH Commands
CMD_BRIGHTNESS_GET = "BRIGHTNESS"
CMD_BRIGHTNESS_SET = "BRIGHTNESS {}"
CMD_STANDBY_ON = "STANDBY"
CMD_STANDBY_OFF = "STANDBY off"

# Platforms
PLATFORMS = ["switch", "number"]
