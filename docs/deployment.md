# Deployment

This document describes how the Raspberry Pi Zero W e-paper monitor was deployed.

---

# Operating System

Recommended OS:

```text
Raspberry Pi OS Lite (Bullseye) 32-bit
```

Bullseye proved significantly more stable than newer images on the Raspberry Pi Zero W.

---

# Enable SPI

SPI must be enabled for the Waveshare display.

Run:

```bash
sudo raspi-config
```

Navigate to:

```text
Interface Options
    → SPI
        → Enable
```

Verify:

```bash
ls /dev/spi*
```

Expected:

```text
/dev/spidev0.0
/dev/spidev0.1
```

---

# Required Packages

Install required packages:

```bash
sudo apt install -y \
    python3-pil \
    python3-numpy \
    python3-spidev \
    python3-rpi.gpio
```

---

# Waveshare Library

Clone Waveshare Python examples:

```bash
git clone https://github.com/waveshare/e-Paper.git
```

Example project location:

```text
~/waveshare_epaper/
```

---

# SSH Remote Telemetry

The Raspberry Pi Zero W connects to the monitored server using SSH public key authentication.

Generate key:

```bash
ssh-keygen
```

Copy key:

```bash
ssh-copy-id user@remote-host
```

Test:

```bash
ssh user@remote-host hostname
```

---

# Wi-Fi Stability Fix

Disable Wi-Fi power saving:

```bash
sudo iw dev wlan0 set power_save off
```

Persistent configuration:

```bash
sudo nano /etc/rc.local
```

Add before:

```bash
exit 0
```

Add:

```bash
iw dev wlan0 set power_save off
```

---

# Systemd Service

Service file:

```text
/etc/systemd/system/epaper-dashboard.service
```

Example:

```ini
[Unit]
Description=Raspberry Pi Zero W e-Paper Dashboard
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/hmasi/waveshare_epaper/dashboard_loop.py
Restart=always
User=hmasi

[Install]
WantedBy=multi-user.target
```

---

# Enable Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable epaper-dashboard.service
sudo systemctl start epaper-dashboard.service
```

Check status:

```bash
systemctl status epaper-dashboard.service
```

---

# Dashboard Loop

The display updates continuously through a lightweight refresh loop.

Example:

```python
while True:
    render_dashboard()
    time.sleep(300)
```

---

# Refresh Interval

Current refresh interval:

```text
5 minutes
```

This minimizes:

- unnecessary display refreshes
- Wi-Fi traffic
- CPU usage
- SD card writes

while still keeping telemetry reasonably fresh.

---

# Notes

The Raspberry Pi Zero W acts only as:

- display node
- telemetry collector
- lightweight appliance

All heavy workloads remain on the monitored server.
