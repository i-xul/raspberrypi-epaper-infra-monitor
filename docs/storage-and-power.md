# Storage and Power Considerations

This project was intentionally designed around low-power and lightweight infrastructure principles.

---

# Raspberry Pi Zero W Role

The Raspberry Pi Zero W acts only as:

- telemetry collector
- dashboard renderer
- e-paper display controller

Heavy workloads remain on the monitored infrastructure server.

This keeps the display node:

- lightweight
- stable
- low-power
- simple to maintain

---

# Why Not Use HDMI Displays?

Traditional displays would require:

- continuous backlight power
- GPU rendering
- HDMI output
- higher idle power usage

The e-paper display avoids all of those requirements.

---

# E-Paper Advantages

The Waveshare 4.2\" e-paper display provides several advantages:

- image remains visible without refresh
- extremely low idle power usage
- no backlight
- suitable for always-on monitoring
- silent operation
- minimal thermal output

This makes it ideal for 24/7 infrastructure telemetry.

---

# Refresh Strategy

The display refreshes every:

```text
5 minutes
```

The display spends most of its time idle.

This minimizes:

- CPU usage
- SPI traffic
- unnecessary refresh cycles
- display wear
- power consumption

---

# SSH-Based Telemetry

Telemetry is collected remotely over SSH.

Advantages:

- no web browser required
- no web dashboard stack required
- no database required
- no additional telemetry agents required

Only lightweight command execution is used.

---

# Storage Considerations

The Raspberry Pi Zero W uses:

- microSD storage
- lightweight Python scripts
- minimal package footprint

Large data storage is intentionally avoided on the display node.

The monitored Raspberry Pi 5 handles:

- Docker workloads
- NVMe storage
- application data
- heavy infrastructure services

---

# Design Philosophy

The project intentionally favors:

- lightweight architecture
- simple dependencies
- low network overhead
- low power consumption
- reliability over complexity

instead of:

- heavy monitoring stacks
- browser-based dashboards
- large databases
- graphical desktop environments

---

# Real-World Observation

In practice, the Raspberry Pi Zero W proved significantly more reliable when treated as:

- a dedicated appliance
- a telemetry endpoint
- a rendering node

rather than as a full development workstation.
