# Architecture

This project uses a lightweight split-architecture design.

The Raspberry Pi Zero W acts only as:

- telemetry collector
- dashboard renderer
- low-power display node

Heavy workloads remain on the monitored infrastructure server.

---

# High-Level Overview

```text
+---------------------------+
| Raspberry Pi Zero W       |
|---------------------------|
| Python dashboard          |
| Waveshare e-paper driver  |
| systemd refresh loop      |
| SSH telemetry client      |
+-------------+-------------+
              |
              | SSH telemetry
              |
              v
+---------------------------+
| Raspberry Pi 5 Server     |
|---------------------------|
| Docker                    |
| Fail2ban                  |
| NVMe storage              |
| System telemetry          |
+---------------------------+
```

---

# Telemetry Flow

The display node performs:

1. single SSH connection
2. remote telemetry collection
3. local rendering
4. e-paper refresh
5. sleep/wait cycle

---

# Why Single SSH Queries?

Early versions used multiple SSH calls for:

- temperature
- Docker
- filesystem usage
- Fail2ban

This proved unstable on the Raspberry Pi Zero W.

The final design uses:

- one SSH session
- multiple remote commands
- parsed local rendering

Benefits:

- lower CPU usage
- lower Wi-Fi load
- fewer connection failures
- faster refresh cycle

---

# Dashboard Refresh Logic

The dashboard loop runs continuously through a systemd service.

Example flow:

```text
loop:
    collect telemetry
    render image
    refresh display
    sleep 5 minutes
```

---

# Offline Detection

If the monitored server is unavailable:

- SSH query fails
- dashboard enters OFFLINE state
- display remains operational
- next refresh automatically retries

No manual recovery is required.

---

# Display Technology

The project uses a Waveshare 4.2" e-paper display.

Advantages:

- extremely low idle power usage
- always-visible display
- no backlight
- suitable for 24/7 infrastructure monitoring

---

# Design Philosophy

The project intentionally prioritizes:

- simplicity
- reliability
- low power usage
- low network overhead
- lightweight software architecture

instead of:

- heavy frameworks
- web dashboards
- browser rendering
- complex dependencies

---

# Future Improvements

Possible future improvements:

- partial refresh support
- multiple monitored hosts
- graphical statistics
- VPN monitoring
- historical telemetry
- alert icons
- stale-data timers
