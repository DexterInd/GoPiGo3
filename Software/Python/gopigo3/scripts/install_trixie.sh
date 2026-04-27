#!/bin/bash
# GoPiGo3 install script for Raspberry Pi OS Trixie

# Check if the script is being sourced or executed
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    echo "Warning: This script is not being sourced. Any virtual environment activation will not persist in the shell after the script ends."
    echo "To activate the virtual environment in your current shell, run: source install_trixie.sh"
    echo "or activate the virtual environment manually: source .venv/bin/activate upon completion."
    read -n 1 -s -r -p "Press SPACE to continue..." key
    echo
fi

# install_trixie.sh - Custom install script for the 'trixie' branch
#
# Usage: source install_trixie.sh [local|user]
#
# Parameters:
#   local - Create/use virtual environment at the GoPiGo3 repository root (./venv)
#   user  - Create/use virtual environment at ~/.venv/gopigo3 (default if omitted)
#
# The script will:
#   - Detect or create a Python virtual environment with --system-site-packages
#   - Install the mr-gopigo3 package from PyPI
#   - Enable SPI, I2C, and VNC interfaces
#   - Install GoPiGo3 power management service
#   - Create desktop shortcuts for Control and Calibration panels
#   - Optionally configure automatic virtual environment activation in ~/.bashrc


# set -e

# Default: user-level venv (~/.venv), unless 'local' is specified
if [ "$1" = "local" ]; then
    # Place venv at the GoPiGo3 repo root (four levels up from scripts/)
    VENV_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)/.venv"
else
    VENV_DIR="$HOME/.venv/gopigo3"
fi

if [ -z "$VIRTUAL_ENV" ]; then
    if [ -f "$VENV_DIR/bin/activate" ]; then
        echo "No Python virtual environment detected, but $VENV_DIR exists. Activating it..."
        # shellcheck disable=SC1090
        source "$VENV_DIR/bin/activate"
        echo "Activated existing virtual environment at $VENV_DIR."
    elif [ -f "$HOME/.venv/bin/activate" ]; then
        # Also check the common $HOME/.venv location (user may have created their own venv there)
        echo "No Python virtual environment detected, but $HOME/.venv exists. Activating it..."
        # shellcheck disable=SC1090
        source "$HOME/.venv/bin/activate"
        echo "Activated existing virtual environment at $HOME/.venv."
        VENV_DIR="$HOME/.venv"
    else
        echo "No Python virtual environment detected. Creating one with --system-site-packages at $VENV_DIR..."
        python3 -m venv --system-site-packages "$VENV_DIR"
        # shellcheck disable=SC1090
        source "$VENV_DIR/bin/activate"
        echo "Virtual environment created and activated at $VENV_DIR."
    fi
else
    echo "Python virtual environment detected at $VIRTUAL_ENV."
    VENV_DIR="$VIRTUAL_ENV"
fi

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Install the GoPiGo3 Python package into the active venv.
echo "Installing GoPiGo3 Python package..."
pip install --quiet --upgrade mr-gopigo3
echo "GoPiGo3 package installed from PyPI ($(pip show mr-gopigo3 | grep ^Version | cut -d' ' -f2))."

# Print info
BRANCH="trixie"
echo "Starting installation for GoPiGo3 ($BRANCH branch)"

# Enable SPI, I2C and VNC interfaces.
# We edit /boot/firmware/config.txt directly for SPI and I2C rather than
# using 'raspi-config nonint do_spi/do_i2c', which rewrites the entire file
# on Trixie and strips essential settings like camera_auto_detect=1.
CONFIG=/boot/firmware/config.txt

REBOOT_NEEDED=false

echo "Checking SPI interface..."
if grep -qE "^dtparam=spi=on" "$CONFIG"; then
    echo "SPI is already enabled — skipping."
else
    echo "dtparam=spi=on" | sudo tee -a "$CONFIG" > /dev/null
    echo "SPI enabled."
    REBOOT_NEEDED=true
fi

echo "Checking I2C interface..."
if grep -qE "^dtparam=i2c_arm=on" "$CONFIG"; then
    echo "I2C is already enabled — skipping."
else
    echo "dtparam=i2c_arm=on" | sudo tee -a "$CONFIG" > /dev/null
    echo "I2C enabled."
    REBOOT_NEEDED=true
fi

if grep -qi "Lite" /etc/os-release 2>/dev/null; then
    echo "Raspberry Pi OS Lite detected — skipping VNC (no desktop environment)."
else
    if systemctl is-enabled vncserver-x11-serviced >/dev/null 2>&1 && \
       systemctl is-active vncserver-x11-serviced >/dev/null 2>&1; then
        echo "VNC server already enabled and active — skipping."
    else
        echo "Enabling VNC server..."
        sudo raspi-config nonint do_vnc 0
        sudo systemctl enable vncserver-x11-serviced
        sudo systemctl start vncserver-x11-serviced
        echo "VNC server enabled."
    fi
fi

install_power_service() {
    echo "Checking GoPiGo3 power management service..."

    # Check if the main power service is already installed and running
    if systemctl is-enabled gopigo3_power >/dev/null 2>&1 && \
       systemctl is-active gopigo3_power >/dev/null 2>&1; then
        echo "GoPiGo3 power management service is already installed and running — skipping."
        return
    fi

    echo "Installing GoPiGo3 power management service..."
    local PYTHON3
    PYTHON3=$(PATH=/usr/local/bin:/usr/bin:/bin command -v python3)

    # When running from a git clone, the local install_power_service.py is always the
    # authoritative version. Using it unconditionally avoids stale pip-installed versions
    # that may still call `systemctl start`, which would shut down the machine over SSH.
    local SCRIPT_LOCAL="$SCRIPT_DIR/install_power_service.py"
    if [ -f "$SCRIPT_LOCAL" ]; then
        echo "Running $SCRIPT_LOCAL directly."
        # Pass VIRTUAL_ENV explicitly — sudo strips env vars but allows inline assignments.
        # install_power_service.py uses it to embed the correct python3 path in the
        # gopigo3_antenna_wifi service unit so antenna_wifi.sh can import gopigo3.
        sudo VIRTUAL_ENV="$VIRTUAL_ENV" "$PYTHON3" "$SCRIPT_LOCAL"
        return
    fi

    # No local script — fall back to the console entry point from pip install.
    if [ -n "$VIRTUAL_ENV" ] && [ -x "$VIRTUAL_ENV/bin/gopigo3-install-power-service" ]; then
        POWER_SVC="$VIRTUAL_ENV/bin/gopigo3-install-power-service"
    else
        POWER_SVC=$(command -v gopigo3-install-power-service 2>/dev/null)
    fi

    if [ -n "$POWER_SVC" ]; then
        sudo "$POWER_SVC"
    else
        echo "Warning: gopigo3-install-power-service not found and $SCRIPT_LOCAL is missing."
        echo "Make sure mr-gopigo3 is installed: pip install mr-gopigo3"
        echo "Then run: sudo gopigo3-install-power-service"
    fi
}

install_power_service

install_list_of_serials_with_16_ticks() {
    echo "Installing list of serial numbers with 16 ticks..."
    local SOURCE_FILE="$SCRIPT_DIR/../../Install/list_of_serial_numbers.pkl"

    if [ ! -f "$SOURCE_FILE" ]; then
        echo "Warning: $SOURCE_FILE not found. Skipping serial numbers installation."
        return
    fi

    # Copy to user's home directory
    local DEST_FILE="$HOME/.gpg3_list_of_serial_numbers.pkl"
    cp "$SOURCE_FILE" "$DEST_FILE"
    echo "Serial numbers list installed to $DEST_FILE."
}

install_list_of_serials_with_16_ticks

install_calibration_panel() {
    echo "Installing GoPiGo3 Calibration Panel shortcut on desktop..."

    PYTHON_BIN=$(python3 -c "import sys; print(sys.executable)")
    PANEL_DIR=$(python3 -c "import importlib.util, os; spec = importlib.util.find_spec('gopigo3'); print(os.path.join(os.path.dirname(spec.origin), 'examples', 'Calibration_Panel') if spec else '')" 2>/dev/null)
    # fallback to repo-relative path
    if [ -z "$PANEL_DIR" ]; then
        PANEL_DIR="$SCRIPT_DIR/../examples/Calibration_Panel"
    fi

    if [ ! -d "$PANEL_DIR" ]; then
        echo "Warning: Calibration Panel not found at $PANEL_DIR. Make sure mr-gopigo3 is installed."
        return
    fi

    ICON_PATH="$PANEL_DIR/drive-config-icon.png"
    DESKTOP_DIR="$HOME/Desktop"
    mkdir -p "$DESKTOP_DIR"
    DEST="$DESKTOP_DIR/gopigo3_calibration.desktop"

    cat > "$DEST" << EOF
[Desktop Entry]
Encoding=UTF-8
Type=Application
Name=GoPiGo3 Calibration Panel
Comment=GoPiGo3 Calibration Panel
Icon=$ICON_PATH
Exec=$PYTHON_BIN $PANEL_DIR/calibration_panel_gui.py
EOF

    chmod +x "$DEST"
    # Mark as trusted for PCManFM/PIXEL desktop.
    # setfattr writes directly to filesystem xattr (no GVFS daemon needed, works from SSH).
    # Fall back to gio set if setfattr is unavailable.
    setfattr -n "user.metadata::trusted" -v "yes" "$DEST" 2>/dev/null || \
        gio set "$DEST" metadata::trusted true 2>/dev/null || true
    echo "Calibration Panel shortcut installed to $DEST."
}

install_calibration_panel

install_control_panel() {
    echo "Installing GoPiGo3 Control Panel shortcut on desktop..."

    PYTHON_BIN=$(python3 -c "import sys; print(sys.executable)")
    PANEL_DIR=$(python3 -c "import importlib.util, os; spec = importlib.util.find_spec('gopigo3'); print(os.path.join(os.path.dirname(spec.origin), 'examples', 'Control_Panel') if spec else '')" 2>/dev/null)
    # fallback to repo-relative path
    if [ -z "$PANEL_DIR" ]; then
        PANEL_DIR="$SCRIPT_DIR/../examples/Control_Panel"
    fi

    if [ ! -d "$PANEL_DIR" ]; then
        echo "Warning: Control Panel not found at $PANEL_DIR. Make sure mr-gopigo3 is installed."
        return
    fi

    ICON_PATH="$PANEL_DIR/GoPiGo-icon.png"
    DESKTOP_DIR="$HOME/Desktop"
    mkdir -p "$DESKTOP_DIR"
    DEST="$DESKTOP_DIR/gopigo3_control_panel.desktop"

    cat > "$DEST" << EOF
[Desktop Entry]
Encoding=UTF-8
Type=Application
Name=GoPiGo3 Control Panel
Comment=GoPiGo3 Control Panel
Icon=$ICON_PATH
Exec=$PYTHON_BIN $PANEL_DIR/control_panel_gui_3.py
EOF

    chmod +x "$DEST"
    # Mark as trusted for PCManFM/PIXEL desktop.
    # setfattr writes directly to filesystem xattr (no GVFS daemon needed, works from SSH).
    # Fall back to gio set if setfattr is unavailable.
    setfattr -n "user.metadata::trusted" -v "yes" "$DEST" 2>/dev/null || \
        gio set "$DEST" metadata::trusted true 2>/dev/null || true
    echo "Control Panel shortcut installed to $DEST."
}

install_control_panel

trust_desktop_launcher() {
    local DEST="$1"

    [ -f "$DEST" ] || return

    chmod +x "$DEST"

    # If script was run via sudo, make sure the desktop launcher belongs to the desktop user.
    if [ -n "$SUDO_USER" ]; then
        sudo chown "$SUDO_USER":"$SUDO_USER" "$DEST" 2>/dev/null || true
    fi

    # Mark as trusted for PCManFM/PIXEL desktop.
    setfattr -n "user.metadata::trusted" -v "yes" "$DEST" 2>/dev/null || \
        gio set "$DEST" metadata::trusted true 2>/dev/null || true
}

trust_desktop_launcher "$HOME/Desktop/gopigo3_control_panel.desktop"
trust_desktop_launcher "$HOME/Desktop/gopigo3_calibration.desktop"

configure_shell_activation() {
    local target_user target_home bashrc_path activation_block

    target_user="${SUDO_USER:-$USER}"
    target_home=$(getent passwd "$target_user" | cut -d: -f6)
    if [ -z "$target_home" ]; then
        target_home="$HOME"
    fi

    bashrc_path="$target_home/.bashrc"
    activation_block=$(cat <<EOF
# >>> GoPiGo3 virtual environment >>>
if [ -f "$VENV_DIR/bin/activate" ] && [ "\$VIRTUAL_ENV" != "$VENV_DIR" ]; then
    . "$VENV_DIR/bin/activate"
fi
# <<< GoPiGo3 virtual environment <<<
EOF
)

    while true; do
        echo ""
        read -r -p "Do you want the virtual environment to be activated automatically for you each time you log in? [y/n] " auto_activate

        case "$auto_activate" in
            [Yy]|[Yy][Ee][Ss])
                touch "$bashrc_path"
                if grep -Fq "# >>> GoPiGo3 virtual environment >>>" "$bashrc_path"; then
                    echo "GoPiGo3 virtual environment auto-activation is already configured in $bashrc_path."
                else
                    printf '\n%s\n' "$activation_block" >> "$bashrc_path"
                    echo "Added GoPiGo3 virtual environment auto-activation to $bashrc_path."
                fi
                break
                ;;
            [Nn]|[Nn][Oo])
                if [ -f "$bashrc_path" ]; then
                    sed -i '/# >>> GoPiGo3 virtual environment >>>/,/# <<< GoPiGo3 virtual environment <<</d' "$bashrc_path"
                fi
                echo "To work on GoPiGo3 later, run: source $VENV_DIR/bin/activate"
                break
                ;;
            *)
                echo "Please answer y or n."
                ;;
        esac
    done
}

configure_shell_activation

echo ""
echo "Done."

if [ "$REBOOT_NEEDED" = true ]; then
    while true; do
        read -r -p "Reboot now for all changes to take effect? [y/n] " reboot_now

        case "$reboot_now" in
            [Yy]|[Yy][Ee][Ss])
                echo "Rebooting now..."
                sudo reboot
                break
                ;;
            [Nn]|[Nn][Oo])
                echo "Please reboot before using the GoPiGo3 so the configuration changes can take effect."
                break
                ;;
            *)
                echo "Please answer y or n."
                ;;
        esac
    done
else
    echo "No reboot required."
fi
