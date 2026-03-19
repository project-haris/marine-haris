# Tamper Evidence Protocol: Project Haris

## 1. Purpose
This document establishes the procedures for applying, inspecting, and managing tamper-evident security measures for Project Haris edge devices. These measures are critical for maintaining the integrity of maritime security data and detecting unauthorized physical access.

## 2. Security Seal Specifications

### 2.1 Seal Requirements
All seals used for Project Haris devices must meet the following minimum specifications:
- **Type**: Holographic void seals or high-security barrier seals
- **Material**: Destructible vinyl or frangible material that shows visible evidence of tampering
- **Adhesion**: Pressure-sensitive adhesive with minimum 24-hour cure time
- **Identification**: Unique serial number and barcode for tracking
- **Durability**: Resistant to marine environment (salt spray, humidity, UV)

### 2.2 Approved Seal Types
1. **Holographic Void Seals** - For enclosure access panels
   - Part Number: HS-VOID-500
   - Size: 1.5" x 3"
   - Color: Silver holographic with red "VOID" pattern

2. **Cable Barrier Seals** - For external cable connections
   - Part Number: CB-LOCK-200
   - Material: Aluminum body with steel cable
   - Serial Number Range: 000001-999999

## 3. Application Procedures

### 3.1 Pre-Application Inspection
Before applying seals, verify:
- [ ] Device is functioning correctly (all tests passed)
- [ ] Enclosure is clean and dry
- [ ] All access points are properly secured
- [ ] No visible damage to enclosure or components

### 3.2 Seal Application

#### Enclosure Seals (Holographic Void)
1. Clean the application area with isopropyl alcohol.
2. Remove backing from seal, avoiding touching adhesive.
3. Position seal across the seam between the access panel and main enclosure.
4. Apply firm pressure for 30 seconds.
5. Verify seal shows no air bubbles or lifted edges.

#### Cable Seals (Barrier Type)
1. Route the steel cable through the cable gland and enclosure eyelet.
2. Insert cable end into seal body until it clicks.
3. Pull gently to verify it's locked.
4. Record the seal's serial number.

### 3.3 Serial Number Recording
All seal serial numbers must be recorded in the M-SOC Security Database within 1 hour of application:
```sql
INSERT INTO security_seals (vessel_id, seal_type, serial_number, applied_by, applied_date) 
VALUES ('VESSEL-001', 'HS-VOID-500', 'A1234567', 'TECH-NAME', '2023-11-15 14:30:00');
```

## 4. Inspection Protocol

### 4.1 Routine Inspections
Project Haris devices must be inspected for tamper evidence during:
- Initial installation (pre-sealing)
- Monthly maintenance visits (if applicable)
- Any service call or repair
- Random audits (minimum quarterly)

### 4.2 Inspection Checklist
```markdown
## Project Haris Tamper Inspection Form

**Vessel ID:** _______________
**Date:** _______________
**Inspector:** _______________

### Enclosure Seals
- [ ] Seal Serial #: _________ Intact □ Damaged □ Missing □
- [ ] Seal Serial #: _________ Intact □ Damaged □ Missing □
- [ ] Seal Serial #: _________ Intact □ Damaged □ Missing □

### Cable Seals
- [ ] Seal Serial #: _________ Intact □ Damaged □ Missing □
- [ ] Seal Serial #: _________ Intact □ Damaged □ Missing □

### Visual Inspection
- [ ] No scratches or marks on enclosure
- [ ] All screws present and tight
- [ ] No evidence of forced entry
- [ ] All ports/cables properly secured

### Tamper Detection system
- [ ] Software tamper detection shows no alerts
- [ ] System logs show no unauthorized access attempts

**Inspector Signature:** _______________
```

### 4.3 Inspection Frequency
| Device Location | Inspection Frequency | Responsible Party |
|----------------|----------------------|-------------------|
| Port Facilities | Monthly | Field Technician |
| Vessels at Sea | Quarterly | Vessel Operator (remote check) |
| High-Security Areas | Weekly | Security Personnel |

## 5. Tamper Detection Procedures

### 5.1 Indicators of Tampering
Tampering may be indicated by:
- Broken, missing, or altered security seals
- Scratches, marks, or damage to enclosure
- Loose or missing screws
- Unexplained changes in device behavior
- Alerts from the device's software tamper detection system

### 5.2 Response Protocol
**If tampering is detected:**

1. **DO NOT** attempt to power on or use the device.
2. Secure the area and restrict access.
3. Document the evidence:
   - Photograph the device from multiple angles
   - Note serial numbers of affected seals
   - Collect any physical evidence
4. Immediately report to the M-SOC Security Team:
   - Email: security@marineharis-ops.org
   - Phone: +1-555-MARIS-SEC
5. Complete a Tamper Incident Report within 24 hours.

### 5.3 Software-Based Detection
Project Haris devices include software tamper detection that monitors:
- Enclosure opening sensor (if equipped)
- Unexpected USB device connections
- Changes to critical system files
- Unauthorized login attempts

These are logged and can trigger alerts to the M-SOC.

## 6. Seal Replacement Procedures

### 6.1 Authorized Replacement
Seals may only be replaced by authorized personnel during:
- Scheduled maintenance
- Authorized repairs
- Replacement of damaged seals (with proper documentation)

### 6.2 Replacement Process
1. Document reason for seal removal.
2. Photograph existing seals before removal.
3. Remove old seals carefully, preserving serial numbers.
4. Perform required maintenance or repairs.
5. Apply new seals following the Application Procedures (Section 3).
6. Update M-SOC database with new seal information.

## 7. Seal Inventory Management

### 7.1 Inventory Control
All security seals must be:
- Stored in a secure location with limited access
- Tracked by serial number
- Accounted for during inventory audits

### 7.2 Damaged/Used Seals
- Damaged seals must be retained for forensic analysis if tampering is suspected.
- Used seals must be destroyed or defaced before disposal to prevent reuse.

## 8. Training Requirements

All personnel handling Project Haris devices must complete:
- Tamper Evidence Awareness Training (online module)
- Practical Seal Application Exercise
- Annual refresher training

## 9. Compliance and Auditing

### 9.1 Records Retention
All tamper evidence records must be retained for a minimum of **5 years**, including:
- Seal application records
- Inspection forms
- Tamper incident reports
- Training records

### 9.2 Audit Schedule
The M-SOC Security Team will conduct random audits of:
- Seal application records (monthly)
- Inspection documentation (quarterly)
- Physical seal integrity (during field visits)

## 10. References

- ISO 17712:2013 - Freight containers — Mechanical seals
- Maritime Security Regulations (MSR) Section 12.4
- M-SOC Physical Security Policy

---

**Document Control:**
- Version: 1.0
- Last Updated: [Current Date]
- Approved By: [M-SOC Security Director]
- Next Review Date: [One Year from Current Date]
