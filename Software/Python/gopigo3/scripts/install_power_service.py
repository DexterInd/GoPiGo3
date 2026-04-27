"""
Console-script entry point for installing the GoPiGo3 power management service.

After `pip install gopigo3`, run:
    sudo gopigo3-install-power-service

This script:
  1. Copies gopigo3_power.py and antenna_wifi.sh to /opt/gopigo3/
  2. Installs the gopigo3_power systemd service
  3. Installs the gopigo3_antenna_wifi systemd service
"""

import os
import shutil
import subprocess
import sys

POWER_SERVICE_NAME = "gopigo3_power"
WIFI_SERVICE_NAME = "gopigo3_antenna_wifi"
INSTALL_DIR = "/opt/gopigo3"


def _copy_to_opt(src, name):
    dest = os.path.join(INSTALL_DIR, name)
    shutil.copy2(src, dest)
    os.chmod(dest, 0o755)
    print(f"Copied {name} to {dest}")
    return dest


def _install_service(service_name, service_content):
    service_file = f"/etc/systemd/system/{service_name}.service"
    with open(service_file, "w") as f:
        f.write(service_content)
    print(f"Service file written to {service_file}")
    subprocess.run(["systemctl", "enable", service_name], check=True)
    print(f"{service_name} enabled.")


def main():
    if os.geteuid() != 0:
        print("This command must be run as root. Try: sudo gopigo3-install-power-service")
        sys.exit(1)

    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(INSTALL_DIR, exist_ok=True)

    # --- gopigo3_power.py ---
    power_py_src = os.path.join(scripts_dir, "gopigo3_power.py")
    if not os.path.isfile(power_py_src):
        print(f"ERROR: {power_py_src} not found.", file=sys.stderr)
        sys.exit(1)
    power_py_dest = _copy_to_opt(power_py_src, "gopigo3_power.py")

    python3 = shutil.which("python3") or sys.executable
    print(f"Installing {POWER_SERVICE_NAME}.service...")
    print(f"  gopigo3_power.py : {power_py_dest}")
    print(f"  python3          : {python3}")
    _install_service(POWER_SERVICE_NAME, f"""\
[Unit]
Description=GoPiGo3 Power Management
After=local-fs.target

[Service]
Type=simple
WorkingDirectory=/tmp
ExecStart={python3} {power_py_dest}
Restart=on-failure

[Install]
WantedBy=multi-user.target
""")

    # --- antenna_wifi.sh ---
    wifi_sh_src = os.path.join(scripts_dir, "antenna_wifi.sh")
    if os.path.isfile(wifi_sh_src):
        wifi_sh_dest = _copy_to_opt(wifi_sh_src, "antenna_wifi.sh")

        # Resolve python3 from the active venv (passed via VIRTUAL_ENV env var from
        # install_trixie.sh), falling back to the system python3. Rewrite the installed
        # copy of antenna_wifi.sh so it calls the absolute path — the service runs without
        # any venv activated, so a bare 'python3' would miss gopigo3 in site-packages.
        venv = os.environ.get("VIRTUAL_ENV", "")
        python3_wifi = os.path.join(venv, "bin", "python3") if venv and os.path.isfile(os.path.join(venv, "bin", "python3")) else (shutil.which("python3") or sys.executable)
        print(f"  python3 for antenna_wifi.sh : {python3_wifi}")
        with open(wifi_sh_dest, "r") as f:
            content = f.read()
        content = content.replace("python3 ", f"{python3_wifi} ")
        with open(wifi_sh_dest, "w") as f:
            f.write(content)

        print(f"Installing {WIFI_SERVICE_NAME}.service...")
        _install_service(WIFI_SERVICE_NAME, f"""\
[Unit]
Description=GoPiGo3 Antenna WiFi Indicator
After=network.target

[Service]
Type=idle
ExecStart=/bin/bash {wifi_sh_dest}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
""")
        subprocess.run(["systemctl", "start", WIFI_SERVICE_NAME], check=True)
        print(f"{WIFI_SERVICE_NAME} started.")
    else:
        print(f"Warning: {wifi_sh_src} not found — skipping antenna WiFi service.")

    subprocess.run(["systemctl", "daemon-reload"], check=True)
    print("systemd daemon reloaded.")
    print("NOTE: The gopigo3_power service is NOT started now — starting it during an SSH")
    print("      install session risks an immediate shutdown if GPIO 22 is transiently high.")
    print("      Reboot when prompted to bring the power management service online.")


if __name__ == "__main__":
    main()
