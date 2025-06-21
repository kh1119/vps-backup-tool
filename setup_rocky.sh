#!/usr/bin/env bash
# setup_rocky.sh - Quick setup for Rocky/RHEL/CentOS systems

set -euo pipefail

echo "🔧 VPS Backup Tool Setup for Rocky Linux"
echo "========================================"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo "✅ Running as root"
    SUDO=""
else
    echo "ℹ️  Running as user, will use sudo"
    SUDO="sudo"
fi

# Install pip3
echo "📦 Installing python3-pip..."
if command -v dnf &> /dev/null; then
    $SUDO dnf install -y python3-pip
elif command -v yum &> /dev/null; then
    $SUDO yum install -y python3-pip
else
    echo "❌ Neither dnf nor yum found"
    exit 1
fi

# Install PyYAML
echo "📦 Installing PyYAML..."
pip3 install --user PyYAML

# Set permissions
echo "🔐 Setting executable permissions..."
chmod +x *.sh

# Create configs from templates
if [[ ! -f "config.yaml" ]]; then
    echo "📝 Creating config.yaml from template..."
    cp config.yaml.template config.yaml
    echo "⚠️  IMPORTANT: Edit config.yaml with your VPS details!"
fi

if [[ ! -f "config_test.yaml" ]]; then
    echo "📝 Creating config_test.yaml from template..."
    cp config_test.yaml.template config_test.yaml
    echo "⚠️  Edit config_test.yaml for testing"
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p backup_data logs tmp

echo ""
echo "🎉 Setup complete for Rocky Linux!"
echo ""
echo "Next steps:"
echo "1. Edit config.yaml: nano config.yaml"
echo "2. Test: python3 quick_bandwidth.py"
echo "3. Run: ./backup_with_monitoring.sh"
