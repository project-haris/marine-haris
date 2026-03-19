# Security Audit Checklist: Project Haris

**Vessel ID:** _______________
**Auditor:** _______________
**Date:** _______________

## 1. Physical Security

*   [ ] **Enclosure Integrity**: Is the device housed in a sealed, IP67-rated enclosure?
*   [ ] **Tamper Seals**: Are unique, serialized tamper seals applied to all access screws?
*   [ ] **Seal Log**: Have the seal serial numbers been logged in the M-SOC database?
*   [ ] **Port Access**: Are all unused physical ports (USB, Ethernet) physically blocked or disabled in software?
*   [ ] **Power**: Is the power connection secured to prevent accidental disconnection?

## 2. Network Security

*   [ ] **Firewall Status**: Is firewalld active (`sudo firewall-cmd --state`)?
*   [ ] **Input Policy**: Is the default zone set to `drop`?
*   [ ] **SSH Restriction**: Is SSH allowed *only* from the Tailscale zone?
*   [ ] **VPN Status**: Is the Tailscale interface (`tailscale0`) active and connected?
*   [ ] **Public IP**: Does `curl ifconfig.me` return the expected IP (verify network routing)?
*   [ ] **Port Scanning**: Run a local nmap scan. Are only expected ports open on the Tailscale interface?

## 3. Data Security

*   [ ] **Disk Encryption**: Is the NVMe SSD encrypted (LUKS)?
    *   Command: `lsblk -f` (Should show `crypto_LUKS` type).
*   [ ] **Key Management**: Is the encryption key stored securely (not in plaintext on the boot partition)?
*   [ ] **Transmission Encryption**: Is all outbound traffic routed via Tailscale? (Check `tailscale status`).
*   [ ] **Local Storage**: Are there any plaintext log files containing sensitive navigation data visible in `/var/log`?

## 4. System Hardening

*   [ ] **User Access**: Is the default `pi` user disabled or renamed?
*   [ ] **Root Login**: Is root login via SSH disabled (`PermitRootLogin no` in sshd_config)?
*   [ ] **Password Auth**: Is password authentication disabled (`PasswordAuthentication no` in sshd_config)?
*   [ ] **Services**: Are only essential services running?
    *   Check: `systemctl list-unit-files --type=service | grep enabled`
*   [ ] **Updates**: Is the system running the latest security patches? (`apt list --upgradable`).

## 5. Findings & Remediation

| ID | Finding | Severity | Remediation Plan | Status |
|---|---|---|---|---|
| 001 | Example: Port 80 found open | High | Close port via firewalld rule update | [ ] Fixed |
| 002 | Example: Firmware outdated | Medium | Schedule downtime for apt upgrade | [ ] Scheduled |

---

**Auditor Signature:** __________________
**M-SOC Supervisor Approval:** __________________
