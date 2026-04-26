# GoPiGo3 Installation FAQ
### For Raspberry Pi 3B+, 4, and 5

This guide is written for educators who want to use GoPiGo3 in their classroom.
The Raspberry Pi is assumed to be **headless** — no monitor, no keyboard attached. You will connect to it from your laptop over WiFi or ethernet using SSH.

---

## Table of Contents

**Installation Options:**
- [Which option is right for me?](#which-option-is-right-for-me)
- [Option A — Install using `pip` on a fresh Raspberry Pi OS](#option-a--install-using-pip-on-a-fresh-raspberry-pi-os--easiest)
- [Option B — Install using `git clone` (Full source + examples)](#option-b--install-using-git-clone-full-source--examples)
- [Setting up a Python virtual environment](#setting-up-a-python-virtual-environment)

**Frequently Asked Questions:**
- [What does the install_trixie.sh script do?](#what-does-the-install_trixiesh-script-do)
- [The power LED keeps on blinking.. What can I do?](#the-power-led-keeps-on-blinking-what-can-i-do)
- [What does "mr" in mr-gopigo3 stand for?](#what-does-mr-in-mr-gopigo3-stand-for)

---

## Which option is right for me?

| Situation | Recommended option |
|---|---|
| I want the simplest setup and I'm starting from scratch | **Option A** — `pip install` on a fresh Raspberry Pi OS |
| I want the full source code and example projects | **Option B** — Install via `git clone` |

> **Why isn't there a pre-made image?** When you download a ready-made image, it is a heavy download. Plus there is no way to tell it your WiFi password before first boot. You would need an ethernet cable plugged into a router to connect. Options A and B use the official Raspberry Pi Imager, which lets you enter your WiFi details in advance so you can connect wirelessly right away. And you get the option of enabling Raspberry Pi Connect.

---

## Option A — Install using `pip` on a fresh Raspberry Pi OS ✅ Easiest

This is the recommended approach for most users. You flash a standard Raspberry Pi OS image yourself (which means you can pre-configure WiFi), then install GoPiGo3 with a single command.

### What you need
- A Raspberry Pi 3B+ *(recommended)*, 4, or 5
- A microSD card (16 GB or larger)
- A laptop with [Raspberry Pi Imager](https://www.raspberrypi.com/software/) installed

### Steps

1. **Flash Raspberry Pi OS to your microSD card**

   - Open **Raspberry Pi Imager**.
   - In the **Device** tab, select your Pi model (Raspberry Pi 3B+, 4, or 5). Click **Next**.
   - In the **OS** tab, choose **"Raspberry Pi OS (64-bit)"** for a full desktop, or **"Raspberry Pi OS (other)"** → **"Raspberry Pi OS Lite (64-bit)"** if you prefer a lighter, terminal-only system. Either works with GoPiGo3. Click **Next**.
   - In the **Storage** tab, select your microSD card. Click **Next**.
   - Imager launches the **Customisation wizard** automatically. Go through each screen:
     - **Hostname** — enter a name for your Pi, e.g. `gopigo3`. Click **Next**.
     - **Localisation** — choose your city (timezone and keyboard fill in automatically). Click **Next**.
     - **User** — enter a username and password you will remember. Click **Next**.
     - **Wi-Fi** — enter your WiFi network name (SSID) and password. Click **Next**.
     - **SSH Authentication** — toggle **Enable SSH** to on, then choose **"Use password authentication"**. Click **Next**.
     - **Raspberry Pi Connect** — Optionally enable Raspberry Pi Connect. Follow the on-screen steps to complete setup (see [Raspberry Pi Connect documentation](https://www.raspberrypi.com/software/connect/) for detailed information). Click **Next**.

       > **What is Raspberry Pi Connect?** It's a free cloud-based remote access service that lets you connect to your Pi from anywhere in the world through your web browser, without needing to be on the same network. You'll need to sign in with a Raspberry Pi ID (free account). [Learn more about Raspberry Pi Connect](https://www.raspberrypi.com/software/connect/).
       >
       > **When to enable it:** If you want to access your Pi remotely from outside your local network (e.g., from school, home, or while traveling), or if your network blocks incoming SSH connections.
       >
       > **When to skip it:** If you only plan to use the Pi on your local network, or if you prefer not to use cloud services for security/privacy reasons. SSH over local network is sufficient for most classroom use.
       >
       > **Note:** Raspberry Pi Connect is a service provided by Raspberry Pi Ltd. Modular Robotics does not provide support for Raspberry Pi Connect. For issues with this service, please contact Raspberry Pi support.
   - On the summary screen, click **"Write"** and confirm.

2. **Insert the card, power on the Pi, and SSH in.**

   Insert the microSD card into the Pi and plug in power. After about a minute, open a terminal on your laptop and type (replace with your hostname if you chose something other than `gopigo3`):

   ```bash
   ssh yourusername@gopigo3.local
   ```

   Replace `yourusername` and `gopigo3` with whatever you set in the wizard. You will be asked for your password and then land at a command prompt on the Pi.

   > **If `gopigo3.local` doesn't work**, you can find the Pi's IP address by logging into your router's admin page — open a browser on your laptop and try `192.168.1.1`, `192.168.0.1`, or `10.0.0.1` (these are the router's own admin addresses, not the Pi's). Look for a list of connected devices; the Pi will appear with the hostname you chose. Then SSH using its IP directly:
   > ```bash
   > ssh yourusername@192.168.x.x
   > ```

3. **Create and activate a virtual environment**:

   ```bash
   python3 -m venv ~/.venv/gopigo3
   source ~/.venv/gopigo3/bin/activate
   ```

   See the [Setting up a Python virtual environment](#setting-up-a-python-virtual-environment) section below for more details.

4. **Install GoPiGo3**:

   ```bash
   pip install mr-gopigo3
   ```

5. **Run the setup script** to enable SPI, I2C, VNC, the power management service, and desktop shortcuts.
   The script was installed alongside the package into your virtual environment:

   ```bash
   source ~/.venv/gopigo3/lib/python3.*/site-packages/gopigo3/scripts/install_trixie.sh
   ```

   > The `python3.*` part matches whichever Python version is on your Pi (e.g. `python3.11`, `python3.12`). The `*` wildcard handles this automatically — no need to type the version number.

6. **Reboot** to apply interface changes:

   ```bash
   sudo reboot
   ```

### Test it

```bash
python3 -c 'import gopigo3; print("GoPiGo3 installed successfully!")'
```

---

## Option B — Install using `git clone` (Full source + examples)

Use this if you want the complete source code and the sample projects folder.
The setup steps are identical to Option A — the only difference is how the library is installed.

### Steps

1. Flash Raspberry Pi OS and connect via SSH exactly as described in **Option A, steps 1 and 2**.

2. **Clone the repository** into the directory of your choice, then enter it:

   ```bash
   git clone https://github.com/DexterInd/GoPiGo3.git
   cd GoPiGo3
   ```

3. **Run the setup script** to install GoPiGo3 and enable SPI, I2C, VNC, the power management service, and desktop shortcuts:

   ```bash
   source Install/install_trixie.sh
   ```

   **Script parameters:**
   - No parameter (default): Creates/uses a virtual environment at `~/.venv/gopigo3`
   - `local`: Creates/uses a virtual environment at the GoPiGo3 repository root (`./.venv`)

   Example with parameter:
   ```bash
   source Install/install_trixie.sh local
   ```

   **If you already have a virtual environment:**
   - If you activate a venv before running the script, it will use your active environment and configure auto-activation for that specific path in your `~/.bashrc`.
   - If no venv is active, the script will detect existing environments at the default location or create a new one.

4. **Reboot** to apply interface changes:

   ```bash
   sudo reboot
   ```

5. **Test it**

```bash
python3 -c 'import gopigo3; print("GoPiGo3 installed successfully!")'
```

### Explore the examples

The `Projects/` folder inside the cloned repository contains ready-to-run example programs for driving, sensors, line following, and more.

---

## Setting up a Python virtual environment

Modern Raspberry Pi OS (Trixie / Debian 13) will refuse to install Python packages system-wide with `pip` by default. The clean solution is to use a **virtual environment** — a self-contained folder where Python packages are installed without touching the rest of the system.

You only need to do this once. Run these commands on the Pi after SSHing in:

```bash
# Create a virtual environment at ~/.venv/gopigo3
python3 -m venv ~/.venv/gopigo3

# Activate it (your prompt will change to show '(gopigo3)')
source ~/.venv/gopigo3/bin/activate
```

> **If you're using Option B (git clone)**: The `install_trixie.sh` script will automatically create and activate a virtual environment for you if one doesn't exist, so you can skip manual venv setup.

> **Every time you open a new SSH session**, you will need to activate the virtual environment again before running any Python code:
> ```bash
> source ~/.venv/gopigo3/bin/activate
> ```
> The `install_trixie.sh` script will offer to add automatic activation to your `~/.bashrc` file at the end of installation for both Option A and Option B.

---

### Virtual environment location options

When using `install_trixie.sh`, you can choose where to create the virtual environment:

- **Default (no parameter)**: `~/.venv/gopigo3` — User-level, persists across git updates
- **`local` parameter**: `./.venv` at repository root — Stays with the cloned repo

If you already have a virtual environment active when running `install_trixie.sh`, the script will use your active environment and configure auto-activation for that specific path. It will not create a new one and will disregard the `local` parameter if given.

---

## Frequently Asked Questions

### What does the install_trixie.sh script do?

The `install_trixie.sh` script performs a complete GoPiGo3 setup:

**Python environment:**
- Detects or creates a Python virtual environment with `--system-site-packages`
- Installs the `mr-gopigo3` package from PyPI

**System interfaces:**
- Enables SPI interface via `dtparam=spi=on` in `/boot/firmware/config.txt`
- Enables I2C interface via `dtparam=i2c_arm=on` in `/boot/firmware/config.txt`
- Installs and enables VNC server (desktop versions only, skipped on Lite)

**System services:**
- Installs `gopigo3_power` service — Monitors GPIO 22 for power button events and maintains GPIO 23 to signal the board that the Pi is running
- Installs `gopigo3_antenna_wifi` service — Controls the WiFi antenna LED indicator based on network connectivity

**Desktop shortcuts (if desktop environment present):**
- Creates GoPiGo3 Control Panel shortcut
- Creates GoPiGo3 Calibration Panel shortcut

**Shell configuration:**
- Optionally adds automatic virtual environment activation to `~/.bashrc`

**Reboot:**
- Prompts to reboot if interface changes were made (required for SPI/I2C to activate)

---

### The power LED keeps on blinking.. What can I do?

If the power LED on your GoPiGo3 keeps blinking continuously, it means the `gopigo3_power` service is not running properly. This service is responsible for signaling to the GoPiGo3 board that the Raspberry Pi is fully booted and running.

You may also see this error message when trying to use the GoPiGo3:

```
The GoPiGo3 power service (gopigo3_power) is not running.
Motor control will not work without it.
Start it with:
  sudo systemctl start gopigo3_power
```

**Check if the service is running:**

```bash
sudo systemctl status gopigo3_power
```

If the service is not running, you'll see `inactive (dead)` or `failed` in the output.

**Check the service logs to diagnose the issue:**

```bash
sudo journalctl -u gopigo3_power -n 50
```

This shows the last 50 log entries for the power service. Look for error messages that might explain why it's not running.

**Common issues and solutions:**

1. **Service not enabled** — If the service isn't set to start automatically:
   ```bash
   sudo systemctl enable gopigo3_power
   sudo systemctl start gopigo3_power
   ```

2. **Service not installed** — Check if the service file exists:
   ```bash
   cat /etc/systemd/system/gopigo3_power.service
   ```
   If the file doesn't exist, the installation script may not have completed successfully.

3. **Permissions or GPIO access** — The service needs permission to access GPIO pins. Check if there are any permission-related errors in the logs.

4. **Reinstall the service** — If all else fails, re-run the installation script:
   ```bash
   source ~/.venv/gopigo3/lib/python3.*/site-packages/gopigo3/scripts/install_trixie.sh
   ```
   Or if you installed via git clone:
   ```bash
   cd ~/GoPiGo3
   source Install/install_trixie.sh
   ```

After making changes, restart the service:

```bash
sudo systemctl restart gopigo3_power
```

The power LED should stop blinking and remain solid once the service is running correctly.

**Still having issues?**

If you can't figure out why the power service is not running, contact **info@modrobotics.com** for support. Please include the output of:

```bash
sudo journalctl -u gopigo3_power -n 50
```

---

### What does "mr" in mr-gopigo3 stand for?

The "mr" stands for **Modular Robotics**. The GoPiGo3 was originally developed by Dexter Industries, but since 2019 it has been under the wing of [Modular Robotics](https://www.modrobotics.com/), maker of Cubelets.


