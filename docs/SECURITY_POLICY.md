# Security Policy for Marine_Haris

## 📜 **Overview**

**Marine_Haris** (derived from Arabic "Haris" حارس, meaning "Guardian") is designed with a **Security-First Architecture**. As an edge device operating in remote maritime environments, it is a potential target for physical tampering and cyber intrusion. This document outlines the security protocols, hardening procedures, and incident response plans enforced for this project.

## 🛡️ **Security Architecture Principles**

The system adheres to **Zero Trust** principles:
1.  **Never Trust, Always Verify**: All network connections are encrypted and authenticated.
2.  **Least Privilege**: Services run with minimal permissions; only necessary ports are open.
3.  **Defense in Depth**: Multiple layers of security (Physical, Network, Data, Application).
4.  **Assume Breach**: Mechanisms are in place to detect, contain, and report compromises.

## 📦 **Supported Versions**

Security updates are applied to the `main` branch. We recommend always using the latest tagged release.

| Version | Supported          | Status |
| ------- | ------------------ | ------ |
| 1.0.x   | :white_check_mark: | Current Release |
| < 1.0   | :x:                | Development/Alpha |

---

## 🔒 **Security Domains**

### **1. Physical Security**
*The device operates in unattended environments (vessels).*

*   **Tamper-Evident Enclosure**: The device must be housed in a sealed, IP67-rated enclosure. Use unique, serialized security seals on all access screws. A log of seal numbers must be maintained by the MSOC.
*   **Tamper Detection Script**: The system runs a background service to detect hardware changes (e.g., USB devices, enclosure opening sensors).
*   **Secure Boot**: The Raspberry Pi 5 bootloader is configured to restrict boot media to the internal NVMe only (disabling USB/SD boot) to prevent physical injection attacks.

### **2. Network Security**
*The device connects via untrusted cellular networks.*

*   **VPN Tunneling**: All outbound traffic is routed strictly through a WireGuard VPN tunnel. No direct internet access is permitted.
    *   *Fail-Closed Policy*: If the VPN tunnel drops, the device loses internet connectivity. It does *not* fall back to the raw cellular connection.
*   **Firewall (UFW)**: The device runs a strict host-based firewall.
    *   **Ingress**: Blocked by default. Only SSH (port 22) and Signal K (port 3000) are allowed *exclusively* from the VPN subnet (e.g., `10.0.0.0/24`).
    *   **Egress**: Allowed only to the VPN server IP and defined monitoring endpoints.
*   **DDNS/Static IP**: The device does not expose any public ports. It initiates connections outbound only.

### **3. Data Security**
*Protecting the integrity and confidentiality of vessel data.*

*   **Encryption at Rest**: The NVMe SSD is encrypted using **LUKS (Linux Unified Key Setup)**. The encryption key is stored in a keyfile on the boot partition (which is itself inaccessible from the outside) or requires manual entry upon boot (depending on deployment mode).
*   **Encryption in Transit**: All data is encapsulated in WireGuard's encrypted tunnel (ChaCha20-Poly1305).
*   **Data Sanitization**: If the device is flagged as compromised or is being decommissioned, a `secure-wipe.sh` script utilizes `shred` to overwrite sensitive data directories before disposal.

### **4. Access Control**

*   **SSH Hardening**:
    *   Password authentication is **disabled**.
    *   Root login is **disabled**.
    *   Access is strictly via SSH keys, which are rotated annually or upon personnel changes.
*   **User Privileges**: The data collection services run under a dedicated `haris` user account with limited `sudo` privileges.

---

## 🚨 **Incident Response Plan**

In the event of a security incident (physical breach, network anomaly, or compromise):

1.  **Detection**: Automated scripts alert the MSOC if:
    *   The VPN connection is unstable for > 15 minutes.
    *   Unknown USB devices are detected.
    *   File integrity checks (using `AIDE`) detect modifications to critical configuration files.
2.  **Containment**:
    *   The MSOC can remotely trigger a "Kill Switch" script that disables the data collection services and shuts down network interfaces.
    *   In extreme cases, the MSOC can trigger a crypto-shred (wipe encryption keys), rendering the NVMe data unreadable.
3.  **Recovery**:
    *   Restore the device to a known good state by re-imaging the NVMe SSD with the "Golden Image".
    *   Rotate all WireGuard keys and SSH credentials associated with that node.

---

## 📝 **Reporting a Vulnerability**

We take the security of Marine_Haris seriously. If you discover a vulnerability, please report it responsibly.

**Please do NOT open a public GitHub Issue for security vulnerabilities.**

Instead, please report it via GitHub Security Advisories:

1.  Go to the **Security** tab of this repository.
2.  Click **"New Security Advisory"**.
3.  Provide a detailed description of the vulnerability, steps to reproduce, and potential impact.

We commit to:
*   Acknowledging your report within **48 hours**.
*   Providing a detailed response and remediation plan within **7 days**.
*   Crediting you in the security advisory (if desired).

---

## ✅ **Security Checklist for Deployment**

Before deploying a Marine_Haris node to a vessel, ensure the following checks are passed:

- [ ] **Hardware**: Tamper seals applied and logged.
- [ ] **Storage**: NVMe SSD is fully encrypted (LUKS).
- [ ] **Boot**: Bootloader is locked to NVMe only.
- [ ] **Network**: WireGuard VPN is active and stable.
- [ ] **Firewall**: UFW is enabled; only VPN subnet ports are open.
- [ ] **Access**: Password authentication is disabled; SSH keys are deployed.
- [ ] **Updates**: System is updated to the latest supported version (`sudo apt upgrade`).

---

*This security policy is subject to review and updates. Last updated: February 2026.*