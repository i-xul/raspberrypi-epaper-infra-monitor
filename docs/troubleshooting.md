# Troubleshooting

This project encountered several real-world Raspberry Pi Zero W and Waveshare e-paper issues during development.

The problems and solutions are documented here to help others building similar systems.

---

# Wi-Fi Instability

## Symptoms

- SSH sessions freezing
- `apt install` hanging randomly
- package downloads stalling
- intermittent DNS failures

Example:

```text
Temporary failure resolving 'raspbian.raspberrypi.org'
```

---

## Root Causes

Observed causes included:

- Wi-Fi power saving
- unstable DNS configuration
- Pi-hole DNS issues
- Raspberry Pi Zero W wireless instability under heavier network load

---

## Fixes

Disabled Wi-Fi power saving:

```bash
sudo iw dev wlan0 set power_save off
```

Verified:

```bash
iw dev wlan0 get power_save
```

Result:

```text
Power save: off
```

---

## Additional DNS Fix

Manual DNS configuration was temporarily required:

```bash
sudo nano /etc/resolv.conf
```

Example:

```text
nameserver 1.1.1.1
nameserver 8.8.8.8
```

---

# Waveshare Driver Compatibility Problems

## Symptoms

The display permanently locked during initialization:

```text
DEBUG:waveshare_epd.epd4in2_V2:e-Paper busy
```

The application never continued beyond this point.

---

## Root Cause

The newer `epd4in2_V2.py` driver was incompatible with the display hardware revision used in this project.

Display revision:

```text
Rev 2.1
```

---

## Fix

The issue was resolved by switching to the older compatible driver version.

Working driver:

```text
epd4in2.py
```

Non-working driver:

```text
epd4in2_V2.py
```

---

# SSH Timing During Boot

## Symptoms

After reboot:

- dashboard service started successfully
- remote SSH queries failed temporarily
- first telemetry refresh showed OFFLINE state

Example:

```text
ssh: connect to host 192.168.1.11 port 22
```

---

## Root Cause

The Raspberry Pi Zero W booted faster than the monitored server's SSH service became available.

---

## Resolution

The dashboard refresh loop was designed to recover automatically during the next refresh cycle.

No manual intervention required.

---

# Lessons Learned

- Raspberry Pi Zero W is capable as a lightweight telemetry appliance
- lightweight architectures matter more than CPU performance
- single SSH-query telemetry is significantly more stable than multiple sequential SSH calls
- e-paper displays work extremely well for always-on infrastructure monitoring
- real-world networking issues dominate low-power ARM systems
