#!/bin/bash
# Resolution 2026 - Installation Script
# Sets up the systemd user service for auto-start on boot

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SYSTEMD_USER_DIR/resolution.service"
BOOT_SCRIPT="$HOME/.local/bin/resolution-boot.sh"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           🌅 Resolution 2026 - Installer                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo

# Install Python package
echo "📦 Installing Python package..."
pip install -e "$SCRIPT_DIR"
echo "✓ Package installed"
echo

# Create directories
echo "📁 Creating directories..."
mkdir -p "$SYSTEMD_USER_DIR"
mkdir -p "$HOME/.local/bin"
mkdir -p "$HOME/.config/resolution"
echo "✓ Directories created"
echo

# Create boot script
echo "📝 Creating boot script..."
cat > "$BOOT_SCRIPT" << 'BOOTSCRIPT'
#!/bin/bash
# Resolution 2026 - Boot check script
# This runs at login and launches the TUI if conditions are met

# Check if after 6am
HOUR=$(date +%H)
if [ "$HOUR" -lt 6 ]; then
    exit 0
fi

# Check if already ran today
CONFIG_DIR="$HOME/.config/resolution"
STATE_FILE="$CONFIG_DIR/state.json"
TODAY=$(date +%Y-%m-%d)

if [ -f "$STATE_FILE" ]; then
    LAST_RUN=$(grep -o '"last_run_date": "[^"]*"' "$STATE_FILE" | cut -d'"' -f4)
    if [ "$LAST_RUN" = "$TODAY" ]; then
        exit 0
    fi
fi

# Launch in a fullscreen terminal
# Try common terminal emulators in order of preference
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal --maximize -- bash -c "resolution; exec bash"
elif command -v konsole &> /dev/null; then
    konsole --fullscreen -e resolution
elif command -v xfce4-terminal &> /dev/null; then
    xfce4-terminal --maximize -e "resolution"
elif command -v xterm &> /dev/null; then
    xterm -maximized -e resolution
else
    # Fallback: just run in current terminal context
    resolution
fi
BOOTSCRIPT

chmod +x "$BOOT_SCRIPT"
echo "✓ Boot script created at $BOOT_SCRIPT"
echo

# Create systemd service
echo "📝 Creating systemd user service..."
cat > "$SERVICE_FILE" << SERVICEFILE
[Unit]
Description=Resolution 2026 Morning Check
After=graphical-session.target
PartOf=graphical-session.target

[Service]
Type=oneshot
ExecStart=$BOOT_SCRIPT
Environment=DISPLAY=:0
Environment=PATH=$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=graphical-session.target
SERVICEFILE

echo "✓ Service file created at $SERVICE_FILE"
echo

# Reload and enable service
echo "🔧 Enabling systemd service..."
systemctl --user daemon-reload
systemctl --user enable resolution.service
echo "✓ Service enabled"
echo

# Initialize with default shop items
echo "🏪 Initializing shop with default items..."
resolution init 2>/dev/null || true
echo

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    ✓ Installation Complete!                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo
echo "Commands available:"
echo "  resolution         - Run the morning routine"
echo "  resolution status  - Show current progress"
echo "  resolution shop    - Manage reward shop"
echo "  resolution bye     - End of day + shutdown"
echo "  resolution init    - Re-initialize shop items"
echo "  resolution reset   - Reset all progress"
echo
echo "The morning routine will auto-start on next boot (after 6am)."
echo
echo "🌅 Happy New Year 2026! Good luck with your resolutions!"

