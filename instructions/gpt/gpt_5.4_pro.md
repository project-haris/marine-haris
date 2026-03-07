Perfect, **the high crafter** — with that exact **PiCAN‑M NMEA 0183 + NMEA 2000 + 3A SMPS** board, the key point is this: use the PiCAN‑M for **CAN/NMEA 2000** and **0183/RS422**, but **do not rely on its 3 A SMPS to power a Pi 5 with NVMe**. The board’s SMPS can power older/lighter setups from the NMEA 2000 12 V line, but Raspberry Pi 5 is specified for **5 V / 5 A** and Raspberry Pi recommends a **5 V / 5 A USB‑C supply**; Copperhill also says the PiCAN‑M SMPS can cause undervoltage and instability on Pi 5. ([SK Pang Electronics Ltd][1])

Here’s the setup I’d use:

1. **Power the Pi 5 separately.**
   Use the Pi 5’s own **5 V / 5 A USB‑C power** or a properly sized **12/24 V to 5 V USB‑C marine DC/DC converter**. Keep the PiCAN‑M connected to the NMEA 2000 network for data, but don’t make its onboard 3 A SMPS your main Pi 5 supply. ([Raspberry Pi][2])

2. **Get NVMe boot working first.**
   If your NVMe adapter is **HAT+ compliant**, Raspberry Pi OS auto-detects it. Flash Raspberry Pi OS to the NVMe with Raspberry Pi Imager, then reboot; with **no SD card inserted**, Pi 5 will boot from NVMe automatically. If an SD card is inserted, set `raspi-config > Advanced Options > Boot Order > NVMe/USB boot`. On current Raspberry Pi OS, `config.txt` is in **`/boot/firmware/config.txt`**, not `/boot/config.txt`. For a **non-HAT+** adapter, add `dtparam=pciex1` to `/boot/firmware/config.txt`, and in EEPROM config set `BOOT_ORDER=0xf416` plus `PCIE_PROBE=1`. ([Raspberry Pi][3])

If you’re using the **official standard M.2 HAT+**, it’s the easier one to combine mechanically with a GPIO HAT because it includes a **16 mm GPIO stacking header**; the **Compact** version does not. ([Raspberry Pi][3])

3. **Enable PiCAN‑M on current Raspberry Pi OS.**
   Start with these lines in **`/boot/firmware/config.txt`**. The older PiCAN‑M manual enables I²C as well, and SK Pang’s current install page still uses the MCP2515 overlay but leaves the bcm2835 SPI overlay commented. ([SK Pang Electronics Ltd][4])

```bash
sudo nano /boot/firmware/config.txt
```

Add:

```text
dtparam=i2c_arm=on
dtparam=spi=on
dtoverlay=mcp2515-can0,oscillator=16000000,interrupt=25
#dtoverlay=spi-bcm2835-overlay
```

Then reboot. ([SK Pang Electronics Ltd][4])

4. **Bring up NMEA 2000 on `can0` at 250000.**
   For **PiCAN‑M on NMEA 2000**, use **250000 bps**. SK Pang’s generic CAN install page shows **500000** for general CAN examples, but the PiCAN‑M manual and newer PiCAN‑M marine wiring guide both use **250000** for NMEA 2000. ([SK Pang Electronics Ltd][4])

```bash
sudo apt update
sudo apt install can-utils
sudo ip link set can0 up type can bitrate 250000
candump can0
```

The board appears as **`can0`** to applications. ([SK Pang Electronics Ltd][1])

5. **Enable NMEA 0183 on `ttyS0` only if you need it.**
   PiCAN‑M exposes the RS422/NMEA 0183 side as **`/dev/ttyS0`**. In `raspi-config`, set **Serial login shell = No** and **Serial hardware = Yes**, then reboot. Test with: ([Copperhill Technologies][5])

```bash
sudo raspi-config
stty -F /dev/ttyS0 raw 4800 cs8 clocal
cat /dev/ttyS0
```

Your **J3** terminal is: **1 = GND, 2 = IN+, 3 = IN-, 4 = OUT-, 5 = OUT+**. ([Copperhill Technologies][5])

One marine-specific warning: PiCAN‑M has an **optional 120 Ω terminator** at **JP1**, but a normal **NMEA 2000 backbone should already be terminated at both ends**. So leave the PiCAN‑M terminator **off** unless it is genuinely acting as one end of the CAN segment. ([Copperhill Technologies][5])

Send your **NVMe adapter model**, and I’ll tell you whether it can auto-detect as HAT+ or needs the extra `pciex1` / `PCIE_PROBE` settings.

[1]: https://www.skpang.co.uk/products/pican-m-with-can-bus-micro-c-and-rs422-connector-3a-smps "PiCAN-M with CAN-Bus Micro-C and RS422 Connector + 3A SMPS — SK Pang Electronics Ltd"
[2]: https://www.raspberrypi.com/products/raspberry-pi-5/ "Buy a Raspberry Pi 5 – Raspberry Pi"
[3]: https://www.raspberrypi.com/documentation/accessories/m2-hat-plus.html "M.2 HAT+ - Raspberry Pi Documentation"
[4]: https://www.skpang.co.uk/pages/install "Installing driver for PiCAN2 PiCAN3 and PiCAN-M on a Raspberry Pi — SK Pang Electronics Ltd"
[5]: https://copperhilltech.com/content/pican-m_UGB_10.pdf "pican-m_UGB_10"
