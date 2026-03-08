#!/bin/bash
# WireGuard Client Setup Script for Marine_Haris
# This script automates the generation of keys and the setup of the WireGuard interface on the Raspberry Pi.

# Directory definitions
WG_DIR="/etc/wireguard"
CONFIG_FILE="$WG_DIR/wg0.conf"

echo "--- Marine_Haris WireGuard Setup ---"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root."
    exit 1
fi

# Install WireGuard if not present
if ! command -v wg &> /dev/null; then
    echo "Installing WireGuard..."
    apt update
    apt install -y wireguard
fi

# Generate Keys
echo "Generating cryptographic keys..."
PRIVATE_KEY=$(wg genkey)
PUBLIC_KEY=$(echo "$PRIVATE_KEY" | wg pubkey)

echo "Private Key: (Hidden for security)"
echo "Public Key: $PUBLIC_KEY"

# Create Configuration File
echo "Creating configuration file..."
mkdir -p $WG_DIR

# Write configuration (using the generated private key)
# Note: You must fill in the Server Peer details manually or pass them as arguments
cat <<EOF > $CONFIG_FILE
[Interface]
Address = 10.0.0.2/24
SaveConfig = false
PrivateKey = $PRIVATE_KEY
ListenPort = 51820

[Peer]
PublicKey = <SERVER_PUBLIC_KEY_TO_BE_FILLED>
Endpoint = <SERVER_PUBLIC_IP:PORT>
AllowedIPs = 10.0.0.1/32
PersistentKeepalive = 25
EOF

# Set permissions (Strict!)
chmod 600 $CONFIG_FILE

echo "Configuration saved to $CONFIG_FILE"
echo "IMPORTANT: Edit $CONFIG_FILE to add the Server Public Key and Endpoint."

# Enable the service to start on boot
echo "Enabling wg-quick service..."
systemctl enable wg-quick@wg0

echo "Setup Complete. Start the VPN with: wg-quick up wg0"