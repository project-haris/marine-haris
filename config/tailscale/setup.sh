#!/bin/bash
# Tailscale Setup Script for Project Haris
# This script installs and configures Tailscale on the Raspberry Pi.

echo "--- Project Haris Tailscale Setup ---"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root."
    exit 1
fi

# Install Tailscale if not present
if ! command -v tailscale &> /dev/null; then
    echo "Installing Tailscale..."
    curl -fsSL https://tailscale.com/install.sh | sh
fi

# Enable the service
echo "Enabling Tailscale service..."
systemctl enable tailscaled
systemctl start tailscaled

echo ""
echo "Tailscale installed successfully."
echo ""
echo "To connect to your tailnet, run:"
echo "  sudo tailscale up"
echo ""
echo "Or for headless setup with an auth key:"
echo "  sudo tailscale up --authkey=tskey-auth-xxxxxxxxxxxxx"
echo ""
echo "Generate auth keys at: https://login.tailscale.com/admin/settings/keys"
echo ""
echo "After connecting, your device's Tailscale IP will be:"
echo "  tailscale ip -4"
