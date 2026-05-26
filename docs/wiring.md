# Wiring

## Raspberry Pi Zero W → Waveshare 4.2" e-Paper

| Raspberry Pi Pin | GPIO | Display Pin |
|---|---|---|
| 3.3V | Power | VCC |
| GND | Ground | GND |
| GPIO10 | MOSI | DIN |
| GPIO11 | SCLK | CLK |
| GPIO8 | CE0 | CS |
| GPIO25 | BUSY | BUSY |
| GPIO24 | RESET | RST |
| GPIO17 | DC | DC |

---

## GPIO Wiring Photo

![GPIO Wiring](../screenshots/gpio-wiring.jpg)

---

## Notes

This project uses SPI communication through the Raspberry Pi Zero W GPIO header.

The display is connected directly using female-to-female jumper wires without additional adapter boards.

The Waveshare display revision used in this project is:

```text
Rev 2.1
```

---

## Important Driver Note

The newer `epd4in2_V2.py` driver caused permanent busy-state locking:

```text
DEBUG:waveshare_epd.epd4in2_V2:e-Paper busy
```

The issue was resolved by switching to the older compatible driver version.

This appears to be related to hardware revision compatibility.
