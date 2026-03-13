# Hardware Assembly Guide: Marine_Haris Edge Device

## 📋 **Table of Contents**
1. [Introduction](#introduction)
2. [Safety Precautions](#safety-precautions)
3. [Required Components](#required-components)
4. [Tools Required](#tools-required)
5. [Assembly Procedure](#assembly-procedure)
6. [Post-Assembly Verification](#post-assembly-verification)
7. [Troubleshooting](#troubleshooting)

---

## 1. Introduction

This guide provides detailed instructions for assembling the **Marine_Haris** maritime security edge device. The system is designed for deployment on vessels to collect NMEA 2000/0183 data and transmit it securely to a Maritime Security Operations Center (MSOC).

**Target Audience**: Authorized field technicians and MSOC personnel
**Estimated Assembly Time**: 60-90 minutes
**Difficulty Level**: Intermediate

---

## 2. Safety Precautions

⚠️ **CRITICAL WARNINGS**:

- **Electrical Hazard**: This device connects to vessel 12V systems. Ensure power is disconnected before assembly.
- **ESD Sensitivity**: Electronic components are sensitive to electrostatic discharge. Use proper grounding.
- **Marine Environment**: Salt water is highly corrosive. Ensure all connections are properly sealed.
- **NMEA Network**: Incorrect connections can disrupt vessel navigation systems. Follow diagrams carefully.

**Required Personal Protective Equipment (PPE)**:
- [ ] Anti-static wrist strap
- [ ] Safety glasses
- [ ] Insulated tools

---

## 3. Required Components

### 3.1 Core Components Checklist

| Component | Quantity | Specification | Verification |
|-----------|----------|---------------|--------------|
| Raspberry Pi 5 | 1 | 16GB RAM | Check RAM chip marking |
| PiCAN-M HAT | 1 | Marine-grade with SMPS | Check for SMPS components |
| NVMe SSD | 1 | 128GB M.2 2280 | Verify capacity label |
| NVMe Base | 1 | Pimoroni NVMe Base | Check PCIe connector |
| Router | 1 | TP-Link Archer NX200 | Verify 4G/5G capability |
| MicroSD Card | 1 | 16GB minimum (for initial setup) | Class 10 or higher |
| Enclosure | 1 | IP67 waterproof | Check seal integrity |
| Power Cable | 1 | 12V DC, 3A minimum | Verify wire gauge (18AWG+) |
| NMEA 2000 Cable | 1 | Micro-C male, 6ft | Check pin configuration |
| Ethernet Cable | 1 | Cat6, 3ft | Verify RJ45 connectors |

### 3.2 Optional Components

- External GPS antenna (for improved signal)
- USB-A to USB-C cable (for initial configuration)
- Spare microSD card (backup boot media)

---

## 4. Tools Required

| Tool | Purpose |
|------|---------|
| Precision screwdriver set | Assembly of HAT and enclosure |
| Anti-static mat | ESD protection |
| Multimeter | Voltage verification |
| Wire strippers/cutters | Power cable preparation |
| Heat gun | Heat shrink tubing |
| Crimping tool | Cable connectors |
| Flashlight | Visibility in tight spaces |
| Label maker | Component identification |

---

## 5. Assembly Procedure

### Step 1: Prepare Raspberry Pi 5

![Warning](https://img.shields.io/badge/Step-1-blue)

**5.1.1 ESD Protection**
1. Place anti-static mat on work surface
2. Connect anti-static wrist strap to mat
3. Remove Raspberry Pi 5 from packaging

**5.1.2 Visual Inspection**
- Check for bent pins on GPIO header
- Verify no visible damage to PCB
- Ensure all chips are properly seated

**5.1.3 Prepare Boot Media (Initial Setup)**

For initial configuration, you'll need a microSD card:

```bash
# On a separate computer
# 1. Download Raspberry Pi Imager
# 2. Insert microSD card
# 3. Write Raspberry Pi OS Lite (64-bit)
# 4. Configure settings:
#    - hostname: marine-haris-setup
#    - Enable SSH
#    - Set username/password
```

**5.1.4 Insert microSD Card**
- Insert prepared microSD card into Raspberry Pi 5 slot

---

### Step 2: Install NVMe SSD

![Storage](https://img.shields.io/badge/Step-2-informational)

**5.2.1 Prepare Pimoroni NVMe Base**

```mermaid
flowchart LR
    A[NVMe Base] --> B[Remove Screw]
    B --> C[Insert SSD]
    C --> D[Secure with Screw]
    D --> E[Connect to Pi]
```

1. Remove the screw from the NVMe Base
2. Insert the NVMe SSD into the M.2 slot at a 30° angle
3. Gently press down and secure with the screw
4. **Do not overtighten** - just snug

**5.2.2 Connect to Raspberry Pi 5**

The Pimoroni NVMe Base connects via the PCIe interface:

1. Locate the PCIe connector on the Raspberry Pi 5 (near the USB-C power port)
2. Insert the PCIe ribbon cable from the NVMe Base
3. Ensure proper alignment (pin 1 to pin 1)
4. Secure with provided standoff/screws

**5.2.3 Important Note on Booting**

The Raspberry Pi 5 will initially boot from the microSD card. We'll configure NVMe boot later in software setup.

---

### Step 3: Install PiCAN-M HAT

![CAN](https://img.shields.io/badge/Step-3-blue)

**5.3.1 Prepare the HAT**

1. Remove PiCAN-M HAT from packaging
2. Inspect the Micro-C connector (J1) for damage
3. Verify the SMPS components (inductor, capacitors) are present

**5.3.2 Mount the HAT**

1. **Power off the Raspberry Pi 5** (disconnect power if connected)
2. Align the 40-pin GPIO header on the HAT with the Raspberry Pi GPIO pins
3. Gently press down until fully seated
4. Secure with provided standoffs and screws

```text
Raspberry Pi 5 GPIO Header
    [::::::::::::::::::::::::]  <-- 40 pins
         ||        ||
         ||        ||  Standoff locations
         \/        \/
    [PiCAN-M HAT]
```

**5.3.3 Configure Jumpers (If Needed)**

- **JP1 (CAN Termination)**: If this is the only device on the NMEA 2000 network, or if termination is required, install a jumper here. For most installations, the backbone should already be terminated.

---

### Step 4: Connect Power System

![Power](https://img.shields.io/badge/Step-4-orange)

**5.4.1 Power Options**

The PiCAN-M HAT can power the Raspberry Pi from the NMEA 2000 bus via its onboard SMPS. However, for reliability, we recommend a dedicated 12V connection.

**Option A: Power from NMEA 2000 Bus** (Not Recommended for Production)
- The 12V from the NMEA 2000 network powers the device
- May overload smaller NMEA networks

**Option B: Dedicated 12V Power** (Recommended)
- More reliable
- Doesn't load the NMEA network
- Recommended for production deployments

**5.4.2 Prepare Dedicated Power Cable**

1. Cut the power cable to required length (typically 3-6 feet)
2. Strip 1/4" (6mm) of insulation from both ends
3. On the vessel end:
   - Red wire: Connect to 12V positive (via appropriate fuse, 3A recommended)
   - Black wire: Connect to vessel ground
4. On the device end:
   - Connect to the PiCAN-M's screw terminal (J3) or use a separate DC-DC converter

**5.4.3 Voltage Verification**

Before connecting, verify vessel power:

```text
Multimeter Settings:
- DC Voltage Range: 20V
- Red probe: 12V positive
- Black probe: Ground

Expected Reading: 11.5V - 14.5V (engine off to engine running)
```

---

### Step 5: Prepare NMEA Connections

![NMEA](https://img.shields.io/badge/Step-5-blue)

**5.5.1 NMEA 2000 Connection**

The NMEA 2000 interface uses a Micro-C connector (J1):

```text
Micro-C Connector Pinout:
    _____
   /     \
  | 1 2 3 |  1: Shield
  |  4 5  |  2: +12V
   \_____/  3: GND
            4: CAN_H
            5: CAN_L
```

**Connection Steps:**
1. Locate an available drop on the vessel's NMEA 2000 backbone
2. Connect the drop cable to the backbone
3. Connect the other end to the PiCAN-M's Micro-C connector (J1)
4. Ensure the backbone is properly terminated (120Ω at each end)

**5.5.2 NMEA 0183 Connection (Optional)**

If connecting to legacy NMEA 0183 devices:

```text
PiCAN-M Screw Terminal (J3):
  _______________________
 | IN-    IN+    OUT-  |
 |                      |
 | OUT+   GND           |
 |______________________|
```

**Wiring:**
| Vessel NMEA 0183 | PiCAN-M Terminal | Notes |
|------------------|------------------|-------|
| TX+ (Data Out +) | IN + | Positive data line |
| TX- (Data Out -) | IN - | Negative data line |
| Shield/Ground | GND | Common ground |
| RX+ (Data In +) | OUT + | If receiving data from Pi |
| RX- (Data In -) | OUT - | If receiving data from Pi |

**Baud Rate Consideration:**
- Standard NMEA 0183: 4800 baud
- NMEA 0183-HS (High Speed): 38400 baud
- Check your vessel's equipment documentation

---

### Step 6: Install Router (TP-Link Archer NX200)

![Network](https://img.shields.io/badge/Step-6-yellow)

**5.6.1 SIM Card Installation**

1. Locate the SIM card slot on the router
2. Insert the activated SIM card with gold contacts facing down
3. Ensure the SIM is properly seated

**5.6.2 Power Connection**

1. Connect the router's power adapter to a 12V source (may need a 12V to 5V USB adapter)
2. Power on the router
3. Wait for the router to boot (LED indicators will stabilize)

**5.6.3 Ethernet Connection**

1. Connect one end of the Ethernet cable to the router's LAN port
2. Connect the other end to the Raspberry Pi's Ethernet port

**5.6.4 Initial Router Configuration**

Connect to the router's Wi-Fi network (default credentials on label):

1. Open a web browser and navigate to `http://tplinkwifi.net`
2. Log in with default credentials
3. Configure the cellular connection (should be automatic with valid SIM)
4. Change the default password
5. Note the router's IP address for later configuration

---

### Step 7: Final Assembly and Enclosure

![Final](https://img.shields.io/badge/Step-7-success)

**5.7.1 Cable Management**

1. Organize cables neatly inside the enclosure
2. Use cable ties to secure cables
3. Ensure no strain on connectors
4. Leave service loops for future maintenance

```text
Enclosure Layout (Top View):
 _______________________________
|                              |
|  [PiCAN-M HAT]               |
|       |                      |
|  [Raspberry Pi 5]            |
|       |                      |
|  [NVMe Base + SSD]           |
|                              |
|  [Cable Glands]--> [Router]  |
|______________________________|
```

**5.7.2 Enclosure Sealing**

1. Ensure all cable glands are properly tightened
2. Apply silicone sealant around cable entries (if required by enclosure type)
3. Check the enclosure gasket for proper seating
4. Close the enclosure lid

**5.7.3 Tamper Seals**

1. Apply tamper-evident seals across the enclosure seams
2. Record seal serial numbers in the MSOC database
3. Take photographs of the sealed enclosure

---

## 6. Post-Assembly Verification

### 6.1 Power-On Test

1. Apply power to the device
2. Observe LED indicators:
   - Raspberry Pi 5: Red LED (power), Green LED (activity)
   - PiCAN-M: LED indicators for CAN activity
   - Router: LED indicators for cellular connection

3. Wait 60 seconds for full boot

### 6.2 NMEA 2000 Verification

From a computer connected to the router's network, SSH into the Raspberry Pi:

```bash
# If using microSD boot initially
ssh username@marine-haris-setup.local

# Check CAN interface
sudo ip link set can0 up type can bitrate 250000

# Monitor NMEA 2000 traffic
candump can0
```

**Expected Output:**
```text
can0  09F80201   [8] 00 FF FF FF FF FF FF FF
can0  09F80201   [8] 01 FF FF FF FF FF FF FF
...
```

### 6.3 NMEA 0183 Verification

```bash
# Check serial port
ls -la /dev/ttyS0

# Monitor NMEA 0183 traffic
cat /dev/ttyS0
```

**Expected Output:**
```text
$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A
$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47
...
```

### 6.4 Network Connectivity

```bash
# Check internet connectivity via cellular
ping -c 4 8.8.8.8

# Check if router is accessible
ping -c 4 192.168.1.1  # Replace with router IP
```

---

## 7. Troubleshooting

### 7.1 Power Issues

| Problem | Possible Cause | Solution |
|---------|---------------|----------|
| No power LEDs | Blown fuse, reversed polarity | Check vessel fuse, verify polarity |
| Intermittent power | Loose connection, low voltage | Secure connections, check voltage under load |
| Overheating | Poor ventilation, high load | Improve airflow, reduce processing load |

### 7.2 NMEA 2000 Issues

| Problem | Possible Cause | Solution |
|---------|---------------|----------|
| No CAN traffic | Incorrect bitrate, wiring issue | Verify 250000 baud, check connections |
| Errors in candump | Bus termination issue | Verify 120Ω terminators at backbone ends |
| Interface won't start | Driver not loaded | Check `/boot/firmware/config.txt` for overlay |

### 7.3 NMEA 0183 Issues

| Problem | Possible Cause | Solution |
|---------|---------------|----------|
| No serial data | Wrong device path, baud rate | Try `/dev/ttyS0` or `/dev/AMA0` |
| Garbled data | Baud rate mismatch | Try 4800, 9600, 38400 |
| Partial sentences | Wiring issue, ground loop | Check connections, add ground |

### 7.4 Network Issues

| Problem | Possible Cause | Solution |
|---------|---------------|----------|
| No cellular connection | SIM issue, signal problem | Verify SIM status, check signal strength |
| Can't reach router | Wrong IP, network conflict | Verify router IP, check DHCP settings |
| VPN won't connect | Auth issue, firewall | Verify Tailscale authentication |

---

## 8. Maintenance Notes

### 8.1 Periodic Checks

- Monthly: Visual inspection of enclosure and cables
- Quarterly: Verify all connections are secure
- Annually: Update software and firmware

### 8.2 Firmware Updates

```bash
# Update Raspberry Pi firmware
sudo rpi-update

# Update system software
sudo apt update && sudo apt upgrade
```

### 8.3 Component Replacement

If components need replacement:
1. Power off the device
2. Remove tamper seals (document serial numbers)
3. Perform required maintenance
4. Re-apply new tamper seals
5. Update MSOC database with new seal numbers

---

## 9. Document Control

**Version:** 1.0  
**Last Updated:** [Current Date]  
**Approved By:** [MSOC Technical Director]  
**Next Review Date:** [One Year from Current Date]

---

## 10. Appendix

### A. Pinout Reference

**Raspberry Pi 5 GPIO Header (40-pin)**
```text
3V3  (1)  (2)  5V
GPIO2  (3)  (4)  5V
GPIO3  (5)  (6)  GND
GPIO4  (7)  (8)  GPIO14
GND    (9) (10)  GPIO15
...
```

**PiCAN-M Micro-C Connector**
```text
Pin 1: Shield
Pin 2: +12V (Input/Output)
Pin 3: GND
Pin 4: CAN_H
Pin 5: CAN_L
```

### B. Recommended Spare Parts

- 2x microSD cards (16GB, pre-configured)
- 1x NVMe SSD (128GB)
- 5x tamper seals (same type as primary)
- 2x Ethernet cables (3ft)
- 2x NMEA 2000 drop cables (6ft)

### C. Environmental Specifications

| Parameter | Specification |
|-----------|--------------|
| Operating Temperature | -20°C to +60°C |
| Storage Temperature | -40°C to +85°C |
| Humidity | 5% to 95% non-condensing |
| IP Rating (Enclosure) | IP67 |
| Vibration | IEC 60068-2-6 |
| Shock | IEC 60068-2-27 |

---

**End of Assembly Guide**