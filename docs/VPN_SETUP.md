# Tailscale VPN Configuration

## 🏗️ **VPN Architecture Overview**

```mermaid
flowchart LR
    A[Marine_Haris Device] --> B[TP-Link NX200 Router]
    B --> C[Tailscale Client]
    C --> D((Internet<br/>Cellular))
    D --> E[Tailscale Coordination<br/>Server]
    E --> F[Remote MSOC Server<br/>Tailscale Node]
    F --> G[MSOC Network]
```

## 🖥️ **Server Configuration (Remote MSOC)**

### **Step 1: Install Tailscale**
```bash
# Install Tailscale on server
curl -fsSL https://tailscale.com/install.sh | sh

# Authenticate and connect to your tailnet
sudo tailscale up
```

### **Step 2: Configure as Subnet Router (Optional)**
If the MSOC server needs to provide access to the internal network:

```bash
# Advertise routes to internal MSOC network
sudo tailscale up --advertise-routes=192.168.1.0/24

# Enable IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
```

### **Step 3: Approve Routes**
1. Go to [Tailscale Admin Console](https://login.tailscale.com/admin/machines)
2. Find your server machine
3. Click "Edit route settings"
4. Approve the advertised routes

## 📡 **Client Configuration (Marine_Haris Device)**

### **Step 1: Install Tailscale**
```bash
# Install Tailscale on Raspberry Pi
curl -fsSL https://tailscale.com/install.sh | sh
```

### **Step 2: Authenticate Device**
```bash
# Connect to your tailnet (requires auth key or interactive login)
sudo tailscale up

# Or use an auth key for headless setup
sudo tailscale up --authkey=tskey-auth-xxxxxxxxxxxxx
```

### **Step 3: Configure for Headless Operation**
```bash
# Generate auth key from Tailscale Admin Console
# https://login.tailscale.com/admin/settings/keys

# Create systemd override for auto-start
sudo systemctl enable tailscaled
```

## 📱 **TP-Link NX200 Router (Optional)**

If routing all device traffic through the router's VPN:

1. Access router at `http://tplinkwifi.net`
2. Install Tailscale via router app store (if supported)
3. Authenticate with your tailnet
4. Configure as exit node if needed

## 🔐 **Security Best Practices**

### **ACL Configuration**
Configure Tailscale ACLs to restrict access:

```json
{
  "acls": [
    {
      "action": "accept",
      "src": ["tag:msoc-server"],
      "dst": ["tag:haris-device:*"]
    },
    {
      "action": "accept",
      "src": ["tag:haris-device"],
      "dst": ["tag:msoc-server:22", "tag:msoc-server:3000"]
    }
  ],
  "tagOwners": {
    "tag:msoc-server": ["autogroup:admin"],
    "tag:haris-device": ["autogroup:admin"]
  }
}
```

### **Network Security**
```bash
# On Raspberry Pi, restrict access to Tailscale interface only
sudo firewall-cmd --permanent --zone=tailscale --add-service=ssh
sudo firewall-cmd --permanent --zone=tailscale --add-port=3000/tcp
sudo firewall-cmd --set-default-zone=drop
sudo firewall-cmd --reload
```

## 🧪 **Connection Testing**

### **From Marine_Haris Device**
```bash
# Check Tailscale status
sudo tailscale status

# Get device's Tailscale IP
tailscale ip -4

# Test connectivity to MSOC server (using Tailscale hostname or IP)
ping msoc-server

# Test specific services
ssh user@msoc-server
```

### **From Remote Server**
```bash
# List connected devices
sudo tailscale status

# Ping the Haris device
ping haris-vessel-001
```

## 🚨 **Troubleshooting**

| Issue | Solution |
|-------|----------|
| No connection | Check `tailscale status`, re-auth if needed |
| High latency | Check cellular signal, consider DERP relay |
| DNS issues | Use MagicDNS or configure custom DNS |
| Key expired | Re-authenticate with `sudo tailscale login` |

### **Useful Commands**
```bash
# Debug connectivity
sudo tailscale status
sudo tailscale ping <peer-name>

# Check network interfaces
ip addr show tailscale0

# View logs
journalctl -u tailscaled -f
```

## 📊 **Monitoring**

### **Connection Monitoring**
```bash
# Check connection status
watch -n 5 'sudo tailscale status'

# Monitor traffic on tailscale interface
sudo tcpdump -i tailscale0
```

### **Health Checks**
```bash
# Check if tailscaled is running
systemctl status tailscaled

# Verify connectivity
tailscale ping --c 3 msoc-server
```

## 🔄 **Maintenance**

### **Key Management**
- Tailscale automatically handles key rotation
- Keys expire based on tailnet settings (default: 180 days)
- Pre-auth keys can be set to expire or be reusable

### **Backup Configuration**
```bash
# Export current ACL (from admin console)
# https://login.tailscale.com/admin/acls

# List device info
tailscale status --json > /backup/tailscale-devices.json
```

## 🌐 **Tailscale vs WireGuard**

| Feature | Tailscale | WireGuard |
|---------|-----------|-----------|
| Setup | Automatic | Manual key management |
| NAT Traversal | Built-in DERP relays | Requires manual config |
| Key Rotation | Automatic | Manual |
| Device Discovery | MagicDNS | Manual IP management |
| ACLs | Built-in | Firewall rules |
| Coordination | Managed service | Self-hosted |
