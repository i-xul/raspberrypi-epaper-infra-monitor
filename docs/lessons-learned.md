# Lessons Learned

This project started as a simple e-paper experiment but evolved into a lightweight infrastructure monitoring appliance.

Several important lessons were learned during development.

---

# Lightweight Architectures Matter

The Raspberry Pi Zero W is extremely resource-constrained compared to newer Raspberry Pi models.

Because of this:

- unnecessary SSH sessions mattered
- unstable Wi-Fi behavior mattered
- package management performance mattered
- DNS failures mattered

The final architecture intentionally minimized:

- CPU load
- network activity
- memory usage
- dependency count

---

# Single SSH Query Design Was Critical

Earlier versions performed multiple SSH calls:

- temperature
- Docker status
- filesystem usage
- Fail2ban status

This caused instability and slower refresh cycles.

The final implementation used:

- one SSH connection
- multiple remote commands
- local parsing

This proved significantly more stable.

---

# Real-World Reliability Is More Important Than "Clean" Design

Some technically cleaner approaches were intentionally avoided.

For example:

- heavy frameworks
- web dashboards
- browser rendering
- complex telemetry stacks

Instead, the project focused on:

- reliability
- recoverability
- simplicity
- low-power operation

---

# Waveshare Driver Compatibility Was Non-Trivial

The newer Waveshare V2 driver permanently locked in BUSY state.

The issue was not obvious initially because:

- SPI worked correctly
- GPIO wiring was correct
- the display partially initialized

The actual issue was driver compatibility with the hardware revision.

This reinforced the importance of:

- testing older drivers
- verifying hardware revisions
- keeping troubleshooting notes

---

# E-Paper Displays Are Excellent For Infrastructure Monitoring

The display technology turned out to be ideal for telemetry dashboards because:

- the image remains visible without power
- there is no backlight
- refreshes are infrequent
- idle power consumption is extremely low

This makes e-paper very attractive for:

- homelab monitoring
- infrastructure dashboards
- appliance-style telemetry devices

---

# Raspberry Pi Zero W Is Better As An Appliance Than A Development Machine

The Pi Zero W worked well as:

- telemetry collector
- display renderer
- low-power appliance

But it was uncomfortable as a development environment because:

- package operations were slow
- Wi-Fi was occasionally unstable
- SSH freezes occurred during heavy operations

Development was much smoother from larger systems while the Pi Zero W focused only on its runtime role.

---

# Real Debugging Makes Better Projects

Many of the most valuable parts of this project came from solving real problems:

- Wi-Fi instability
- DNS failures
- SSH timing during boot
- Waveshare compatibility issues
- systemd startup behavior

Documenting those issues made the project significantly more useful for others.

---

# Final Thoughts

The final result achieved the original goals surprisingly well:

- low power usage
- always-visible monitoring
- lightweight telemetry
- reliable autonomous operation
- simple architecture

without requiring heavy software stacks or expensive hardware.
