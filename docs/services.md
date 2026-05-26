# Monitored Services

The Raspberry Pi Zero W dashboard monitors telemetry from a remote Raspberry Pi 5 infrastructure server.

---

# Current Monitored Components

## System Telemetry

Collected remotely over SSH:

- hostname
- online/offline state
- CPU temperature
- root filesystem usage
- NVMe filesystem usage

---

# Docker Monitoring

The dashboard monitors Docker container status.

Currently displayed:

- total running containers
- unhealthy container count
- unhealthy container names

Example:

```text
Docker: 10 up / 0 unhealthy
```

The monitored server uses Docker for several self-hosted services.

Example workloads:

- Nextcloud
- Immich
- Navidrome
- Kavita
- Homepage dashboard

---

# Fail2ban Monitoring

The dashboard monitors Fail2ban telemetry remotely.

Currently displayed:

- total jail count
- sshd ban count
- nginx ban count

Example:

```text
F2B: 7 jails
Bans: sshd 0 / nginx 0
```

This allows the display to function as a lightweight security monitoring appliance.

---

# Offline Detection

If SSH telemetry fails:

- the remote server enters OFFLINE state
- the display node continues operating
- automatic retries occur during the next refresh cycle

No manual recovery is required.

---

# Refresh Strategy

The dashboard intentionally avoids continuous polling.

Current refresh interval:

```text
5 minutes
```

This minimizes:

- network overhead
- Wi-Fi instability
- CPU usage
- unnecessary display refreshes

while remaining suitable for infrastructure monitoring.

---

# Telemetry Collection Design

The final implementation uses:

- one SSH session
- multiple remote commands
- local parsing and rendering

instead of many separate SSH queries.

This proved significantly more stable on the Raspberry Pi Zero W.
