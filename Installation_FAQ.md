# GoPiGo3 Installation FAQ
### For Raspberry Pi 3B+, 4, and 5

This guide is written for educators who want to use GoPiGo3 in their classroom.
The Raspberry Pi is assumed to be **headless** — no monitor, no keyboard attached. You will connect to it from your laptop over WiFi or ethernet using SSH.

---

## Which option is right for me?

| Situation | Recommended option |
|---|---|
| I want the simplest setup and I'm starting from scratch | **Option A** — `pip install` on a fresh Raspberry Pi OS |
| I want the full source code and example projects | **Option B** — Install via `git clone` |
| I have an ethernet cable + router handy, and want a fully pre-configured image | **Option C** — Download the ready-made image |

> **Why is the pre-made image not listed first?** When you download a ready-made image, there is no way to tell it your WiFi password before first boot. You will need an ethernet cable plugged into a router to connect. Options A and B use the official Raspberry Pi Imager, which lets you enter your WiFi details in advance so you can connect wirelessly right away.

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
     - **Remote Access** — toggle **Enable SSH** to on, then choose **"Use password authentication"**. Click **Next**.
   - On the summary screen, click **"Write"** and confirm.

2. **Insert the card, power on the Pi, and SSH in.**

   Insert the microSD card into the Pi and plug in power. After about a minute, open a terminal on your laptop and type:

   ```bash
   ssh yourusername@gopigo3.local
   ```

   Replace `yourusername` and `gopigo3` with whatever you set in the wizard. You will be asked for your password and then land at a command prompt on the Pi.

   > **If `gopigo3.local` doesn't work**, you can find the Pi's IP address by logging into your router's admin page — open a browser on your laptop and try `192.168.1.1`, `192.168.0.1`, or `10.0.0.1` (these are the router's own admin addresses, not the Pi's). Look for a list of connected devices; the Pi will appear with the hostname you chose. Then SSH using its IP directly:
   > ```bash
   > ssh yourusername@192.168.x.x
   > ```

3. **Create and activate a virtual environment** (see the [Setting up a Python virtual environment](#setting-up-a-python-virtual-environment) section below):

   ```bash
   python3 -m venv ~/.venv/gopigo3
   source ~/.venv/gopigo3/bin/activate
   ```

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

> **Every time you open a new SSH session**, you will need to activate the virtual environment again before running any Python code:
> ```bash
> source ~/.venv/gopigo3/bin/activate
> ```
> To make this automatic on login, add that line to the end of your `~/.bashrc` file:
> ```bash
> echo 'source ~/.venv/gopigo3/bin/activate' >> ~/.bashrc
> ```

---

## Option C — Download the ready-made image ⚠️ Requires ethernet cable + router

We provide a complete Raspberry Pi OS image with GoPiGo3 already installed and configured —
SPI, I2C, SSH, the power management service, and everything else is already set up.

> **Important:** Because this is a pre-built image, there is no way to enter your WiFi password before first boot.
> You **must** connect your Raspberry Pi to a router using an **ethernet cable** for the first boot.
> Once you are connected and logged in, you can configure WiFi from the command line.

### What you need
- A Raspberry Pi 3B+ *(recommended)*, 4, or 5
- A microSD card (16 GB or larger)
- An **ethernet cable** and access to a router
- A laptop with [Raspberry Pi Imager](https://www.raspberrypi.com/software/) installed

### Steps

1. **Download the image** (about 1–2 GB):

   👉 *(link coming soon)*

2. **Write it to your microSD card**:

   - Open **Raspberry Pi Imager**.
   - In the **Device** tab, select your Pi model. Click **Next**.
   - In the **OS** tab, scroll to the bottom and select **"Use custom"** → select the zip file you downloaded. Click **Next**.
   - In the **Storage** tab, select your microSD card. Click **Next**.
   - When Imager starts the customisation wizard, click **"Skip customisation"** — do not modify the image, it is already configured.
   - On the summary screen, click **"Write"** and confirm with **"I understand, erase and write"**.

   > ⚠️ This will erase everything currently on the microSD card.

3. **Connect the Pi to your router with an ethernet cable**, insert the card, and power it on.

4. **Find the Pi's IP address** by logging into your router's admin page (usually `192.168.1.1` or `192.168.0.1` in a browser) and looking for a device named `gopigo3` in the connected devices list.

5. **SSH into the Pi**:

   ```bash
   ssh gopigo3@gopigo3.local
   ```

   The default password is printed on the included card or in the image release notes.
