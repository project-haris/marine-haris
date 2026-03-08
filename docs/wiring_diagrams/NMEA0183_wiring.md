# NMEA 0183 Wiring Diagram: Marine_Haris

## 1. Overview
This document details the wiring procedure for connecting legacy NMEA 0183 devices (GPS, Depth Sounders, Wind Instruments) to the **Marine_Haris** device via the PiCAN-M HAT's screw terminal block.

## 2. Connector Specification
The PiCAN-M HAT provides a **5-way Screw Terminal (J3)** for NMEA 0183 (RS-422) connections.

## 3. Pinout Configuration (Screw Terminal J3)

| Terminal Label | Signal Direction | Function |
| :--- | :--- | :--- |
| **IN -** | Input (Negative) | Receive Data - (from Sensor TX-) |
| **IN +** | Input (Positive) | Receive Data + (from Sensor TX+) |
| **OUT -** | Output (Negative) | Transmit Data - (to Sensor RX-) |
| **OUT +** | Output (Positive) | Transmit Data + (to Sensor RX+) |
| **GND** | Ground | Signal Ground Reference |

## 4. Standard "Listener" Wiring (Data Collection)
For the Marine_Haris device to **collect** data from a sensor (e.g., a GPS plotter), the sensor acts as the "Talker" and the PiCAN-M acts as the "Listener".

**Wiring Connection Table:**

| Sensor Side (Talker) | Wire Color (Typical) | PiCAN-M Terminal (Listener) |
| :--- | :--- | :--- |
| TX + (Data Out +) | White or Yellow | **IN +** |
| TX - (Data Out -) | Blue or Green | **IN -** |
| GND (Signal Ground) | Black or Shield | **GND** |

**Diagram:**

```text
[Vessel Sensor]                  [PiCAN-M HAT]
(GPS/Sounder)
+-----------+                  +---------------+
|           |                  |               |
| TX +  ----(White)----------->| IN +          |
|           |                  |               |
| TX -  ----(Blue)------------>| IN -          |
|           |                  |               |
| GND   ----(Black)----------->| GND           |
|           |                  |               |
+-----------+                  +---------------+
```

## 5. Bi-Directional Wiring (Advanced)
If the Marine_Haris device needs to **send commands** to the sensor (rare for security logging), use the OUT terminals.

| Sensor Side (Listener) | PiCAN-M Terminal (Talker) |
| :--- | :--- |
| RX + (Data In +) | **OUT +** |
| RX - (Data In -) | **OUT -** |

## 6. RS-422 vs. RS-232 Note
Most modern marine NMEA 0183 devices use **RS-422** (differential signaling), which matches the PiCAN-M input.
*   **RS-422**: Uses TX+ and TX- wires. Connect as shown above.
*   **RS-232 (Single Ended)**: Some very old equipment uses RS-232. In this case, connect the single Data Out wire to **IN +** and leave **IN -** unconnected (floating). Consult equipment manual.

## 7. Grounding & Shielding
*   **Shield**: If the signal cable has an outer shield (braid/foil), connect this to the **GND** terminal on the PiCAN-M side only. Do not connect the shield at both ends to avoid ground loops.
*   **Ground Wire**: Always connect the sensor's Signal Ground wire to the PiCAN-M **GND** terminal to ensure a common reference voltage.

## 8. Verification Steps
1.  Power on the sensor.
2.  Set the sensor Baud Rate (typically **4800** for standard NMEA 0183, or **38400** for high-speed).
3.  On the Raspberry Pi, verify the serial port settings match the sensor.
4.  Run `cat /dev/ttyS0` (or your configured serial port) to view the raw NMEA sentences.