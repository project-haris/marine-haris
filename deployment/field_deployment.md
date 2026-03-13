Here are the deployment documentation files for the `deployment/` directory. These guides are designed for field technicians and security personnel responsible for installing and maintaining the **Marine_Haris** systems.

### `deployment/field_deployment.md`

```markdown
# Field Deployment Guide: Marine_Haris

## 1. Purpose
This document provides step-by-step instructions for the physical installation, commissioning, and verification of a Marine_Haris edge device on a target vessel. It is intended for authorized field technicians and MSOC personnel.

## 2. Pre-Deployment Checklist

Before traveling to the vessel, confirm the following items are prepared and packed:

**Hardware Kit:**
- [ ] Marine_Haris Unit (Pre-assembled: Pi 5 + PiCAN-M + NVMe + Case)
- [ ] NMEA 2000 Drop Cable (Micro-C Male to Male, 6ft)
- [ ] NMEA 0183 Connection Cable (if required, 2-core shielded)
- [ ] TP-Link Archer NX200 Router (with active SIM card)
- [ ] Ethernet Cable (Cat6, 3ft)
- [ ] 12V Power Cable (Cigarette lighter plug or bare wire leads)
- [ ] Tamper-Evident Seal Kit (Holographic security seals)
- [ ] Installation Tools (Screwdriver set, wire strippers, multimeter)

**Software/Configuration:**
- [ ] Vessel ID assigned in MSOC database.
- [ ] Tailscale device authorized in MSOC tailnet.
- [ ] Device pre-configured with vessel-specific SSH keys and Tailscale auth.
- [ ] Technician has access to MSOC deployment portal for registration.

## 3. Installation Procedure

### 3.1 Site Selection
Choose a location that meets the following criteria:
- **Dry**: Protected from spray, rain, and condensation.
- **Accessible**: Allow space for future maintenance (minimum 6" clearance).
- **Ventilated**: Not in an enclosed, unventilated compartment.
- **Network Proximity**: Within 6 feet of an NMEA 2000 backbone drop or NMEA 0183 junction.
- **Power**: Near a stable 12V DC power source (10-14V range).

### 3.2 NMEA 2000 Connection (Preferred)
1. Locate an available **Micro-C port** on the vessel's NMEA 2000 backbone.
2. Connect the NMEA 2000 drop cable from the backbone to the **PiCAN-M's Micro-C connector (J1)**.
3. Ensure the backbone is properly terminated (check for 120Ω terminators at both ends).

### 3.3 NMEA 0183 Connection (Legacy)
1. Identify the vessel's NMEA 0183 output port (typically labeled "Talker" or "TX").
2. Connect the wires to the PiCAN-M's **5-way screw terminal (J3)** as follows:
   - NMEA 0183 `TX+` (or `DATA+`) → `IN +` terminal.
   - NMEA 0183 `TX-` (or `DATA-`) → `IN -` terminal.
   - Shield/Ground → `GND` terminal.
3. Ensure correct polarity. Reversing connections may result in no data.

### 3.4 Power Connection
1. Connect the 12V power cable to the vessel's power system.
2. **Do NOT power on yet.** Verify voltage with multimeter (10.8V - 14.4V acceptable).
3. Connect the power cable to the **PiCAN-M's Micro-C connector (Pin 2: +12V)** or use the dedicated power terminal if available.

### 3.5 Network Router Setup
1. Insert the pre-configured SIM card into the TP-Link NX200.
2. Connect the router's **WAN/LAN port** to the Raspberry Pi's Ethernet port using the Cat6 cable.
3. Power on the router and wait for cellular connectivity (check LED indicators).

## 4. Commissioning & Verification

### 4.1 Power-On Sequence
1. Apply power to the Marine_Haris unit.
2. Observe the Pi's **green activity LED** - it should flash intermittently during boot.
3. Wait approximately **60 seconds** for the system to boot fully.

### 4.2 VPN Connection Test
1. On a separate laptop connected to the TP-Link router's Wi-Fi, attempt to SSH into the device:
   ```bash
   ssh haris@10.0.0.2  # Replace with the assigned VPN IP
   ```
2. If successful, verify the VPN tunnel is active:
   ```bash
   sudo wg show
   ```
   The output should show a "peer" with a recent "latest handshake."

### 4.3 Data Flow Verification
1. From the SSH session, check NMEA 2000 data reception:
   ```bash
   candump can0
   ```
   You should see a stream of CAN bus frames (if NMEA 2000 connected).

2. Check NMEA 0183 data reception:
   ```bash
   cat /dev/ttyS0
   ```
   You should see NMEA sentences (e.g., `$GPRMC...`).

3. Verify the **Signal K server** is running:
   ```bash
   curl http://localhost:3000/signalk/v1/api/vessels/self
   ```
   This should return a JSON object with navigation data.

### 4.4 MSOC Registration
1. Access the MSOC deployment portal via the VPN connection.
2. Register the device using the **Vessel ID**.
3. Confirm the device appears as "Online" in the MSOC dashboard.
4. Verify data is being received in the MSOC's data lake.

## 5. Physical Security & Tamper Evidence

1. Once verified, place the device in its final operating position.
2. Apply **tamper-evident seals** according to the [Tamper Evidence Protocol](tamper_evidence.md).
3. Record seal serial numbers in the MSOC database.
4. Take photographs of the installation for the vessel's records.

## 6. Handover & Documentation

1. Complete the **Installation Report Form** in the MSOC portal.
2. Provide the vessel operator with the **Marine_Haris Quick Reference Card** containing:
   - Device location
   - Power requirements
   - Emergency contact for MSOC
3. Instruct the operator **NOT** to move, open, or modify the device.

## 7. Troubleshooting Common Issues

| Issue | Probable Cause | Resolution |
|-------|---------------|------------|
| No power | Blown fuse, reversed polarity | Check vessel fuse, verify polarity with multimeter |
| No NMEA 2000 data | Loose connection, wrong termination | Re-seat connectors, verify backbone termination |
| No NMEA 0183 data | Reversed polarity, wrong baud rate | Swap IN+ and IN- wires, confirm baud rate in config |
| No VPN connection | SIM card inactive, router misconfigured | Verify SIM status, check router settings |
| Device overheating | Poor ventilation | Relocate to cooler, ventilated area |

## 8. Emergency Procedures

**If the device is damaged or suspected of tampering:**
1. **DO NOT** attempt to repair or power on.
2. Disconnect power immediately.
3. Secure the area and restrict access.
4. Contact the MSOC Security Team for further instructions.

---

**Document Control:**
- Version: 1.0
- Last Updated: [Current Date]
- Approved By: [MSOC Technical Director]

