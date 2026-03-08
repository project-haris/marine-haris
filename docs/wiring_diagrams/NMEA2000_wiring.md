# NMEA 2000 Wiring Diagram: Marine_Haris

## 1. Overview
This document details the wiring procedure for connecting the **Marine_Haris** edge device to a vessel's NMEA 2000 backbone using the PiCAN-M HAT.

## 2. Connector Specification
The PiCAN-M HAT features a standard **Micro-C (M12-5)** female connector.
- **Connector Type**: Micro-C (M12 5-pin A-Coding)
- **Interface**: J1

## 3. Pinout Configuration
The NMEA 2000 network provides both data connectivity and power.

| Pin Number | Signal | Wire Color (Standard) | Description |
| :--- | :--- | :--- | :--- |
| **1** | SHIELD | Bare/Drain | Cable Shield (Grounded at one end) |
| **2** | +12V | RED | Power Input (Net Supply) |
| **3** | GND | BLACK | Power Return / Ground |
| **4** | CAN-H | WHITE | CAN High Signal |
| **5** | CAN-L | BLUE | CAN Low Signal |

## 4. Wiring Diagram

```text
      [PiCAN-M HAT]                   [Drop Cable]                 [NMEA 2000 Backbone]
  +------------------+            +------------------+           +----------------------+
  |                  |<-----------| 1: Shield       |---------->| Backbone Shield      |
  |   Micro-C (J1)   |            | 2: +12V (Red)   |---------->| Backbone +12V (Red)  |
  |                  |            | 3: GND (Black)  |---------->| Backbone GND (Black) |
  |  [Raspberry Pi]  |            | 4: CAN_H (White)|---------->| Backbone CAN_H       |
  |                  |            | 5: CAN_L (Blue) |---------->| Backbone CAN_L       |
  +------------------+            +------------------+           +----------------------+
```

## 5. Termination Settings
NMEA 2000 networks require 120Ω termination at both ends of the backbone.

1.  **Check Backbone**: Verify the main backbone has 120Ω terminators at the start and end.
2.  **PiCAN-M Jumper (JP1)**:
    *   If the device is being added to an existing, properly terminated network, **DO NOT** install the jumper on JP1.
    *   If the device is acting as the end of the line, install the jumper on JP1 to enable the built-in 120Ω resistor.

## 6. Power Configuration
The PiCAN-M includes an onboard SMPS (Switching Mode Power Supply) capable of powering the Raspberry Pi from the NMEA 2000 12V bus.

**Warning**: While convenient, powering the Pi from the NMEA bus draws significant current (up to 3A peak).
*   **Standard Usage**: Safe for most modern vessels with robust electrical systems.
*   **Sensitive Networks**: If the vessel has older wiring or a sensitive NMEA network, it is recommended to cut the +12V trace (Pin 2) on the PiCAN-M or modify the drop cable to disconnect Pin 2, powering the Raspberry Pi via a separate 12V-to-USB-C adapter instead.

## 7. Verification Steps
1.  Power on the vessel's NMEA 2000 network.
2.  Check voltage at the PiCAN-M Micro-C port: Should read 12V-14V between Pin 2 and Pin 3.
3.  Boot the Raspberry Pi.
4.  Run `candump can0` in the terminal to verify data frames are appearing.

