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

# Check and fix SSH key permissions
echo "🔑 Checking SSH key permissions..."
if [[ -f "config.yaml" ]]; then
    SSH_KEY=$(grep "^ssh_key:" config.yaml | cut -d' ' -f2 | tr -d '"' | tr -d "'")
    if [[ -n "$SSH_KEY" && -f "$SSH_KEY" ]]; then
        echo "Found SSH key: $SSH_KEY"
        CURRENT_PERM=$(stat -c "%a" "$SSH_KEY" 2>/dev/null || stat -f "%A" "$SSH_KEY" 2>/dev/null || echo "unknown")
        if [[ "$CURRENT_PERM" != "600" ]]; then
            echo "🔧 Fixing SSH key permissions: $SSH_KEY"
            chmod 600 "$SSH_KEY"
            echo "✅ SSH key permissions set to 600"
        else
            echo "✅ SSH key permissions already correct (600)"
        fi
    else
        echo "⚠️  SSH key not found or not specified in config.yaml"
        echo "   Make sure to set correct ssh_key path and run: chmod 600 /path/to/your/key"
    fi
else
    echo "⚠️  config.yaml not found, SSH key check skipped"
    echo "   After editing config.yaml, run: chmod 600 /path/to/your/ssh/key"
fi

echo ""
echo "🎉 Setup complete for Rocky Linux!"
echo ""
echo "Next steps:"
echo "1. Edit config.yaml: nano config.yaml"
echo "2. Set SSH key permissions: chmod 600 /path/to/your/ssh/key"
echo "3. Test connection: python3 quick_bandwidth.py"
echo "4. Run backup: ./backup_with_monitoring.sh"
echo ""
echo "💡 SSH Key Tips:"
echo "   - SSH key must have 600 permissions"
echo "   - Use absolute path in config.yaml"
echo "   - Test SSH: ssh -i /path/to/key user@host"
