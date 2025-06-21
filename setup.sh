#!/usr/bin/env bash
# setup.sh - Script setup cho VPS Backup Tool

set -euo pipefail

echo "🔧 VPS Backup Tool Setup"
echo "======================="

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed"
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"

# Kiểm tra và cài đặt pip
PIP_CMD=""
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
    echo "✅ pip3 found"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
    echo "✅ pip found"
elif command -v python3 -m pip &> /dev/null; then
    PIP_CMD="python3 -m pip"
    echo "✅ pip found via python3 -m pip"
else
    echo "❌ pip is not installed. Installing..."
    
    # Detect OS and install pip
    if [[ -f /etc/redhat-release ]]; then
        # RHEL/CentOS/Rocky/Fedora
        echo "🔍 Detected Red Hat based system"
        if command -v dnf &> /dev/null; then
            echo "Installing python3-pip with dnf..."
            if command -v sudo &> /dev/null; then
                sudo dnf install -y python3-pip
            else
                echo "⚠️  Running as root, installing directly..."
                dnf install -y python3-pip
            fi
        elif command -v yum &> /dev/null; then
            echo "Installing python3-pip with yum..."
            if command -v sudo &> /dev/null; then
                sudo yum install -y python3-pip
            else
                echo "⚠️  Running as root, installing directly..."
                yum install -y python3-pip
            fi
        fi
        PIP_CMD="pip3"
    elif [[ -f /etc/debian_version ]]; then
        # Debian/Ubuntu
        echo "🔍 Detected Debian based system"
        if command -v sudo &> /dev/null; then
            sudo apt update && sudo apt install -y python3-pip
        else
            echo "⚠️  Running as root, installing directly..."
            apt update && apt install -y python3-pip
        fi
        PIP_CMD="pip3"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install python3
        else
            echo "Please install pip3 manually or install Homebrew first"
            exit 1
        fi
        PIP_CMD="pip3"
    else
        echo "❌ Unsupported OS. Please install pip3 manually"
        exit 1
    fi
    
    # Verify installation
    if ! command -v $PIP_CMD &> /dev/null; then
        echo "❌ Failed to install pip3"
        exit 1
    fi
    echo "✅ pip3 installed successfully"
fi

# Cài đặt dependencies
echo "📦 Installing Python dependencies..."
$PIP_CMD install -r requirements.txt

# Cấp quyền thực thi
echo "🔐 Setting executable permissions..."
chmod +x backup_with_monitoring.sh
chmod +x run_backup.sh

# Tạo config từ template nếu chưa có
if [[ ! -f "config.yaml" ]]; then
    echo "📝 Creating config.yaml from template..."
    cp config.yaml.template config.yaml
    echo "⚠️  IMPORTANT: Please edit config.yaml with your VPS details before running!"
    echo "   Required fields: ssh_user, ssh_host, ssh_port, ssh_key"
else
    echo "✅ config.yaml already exists"
fi

# Tạo config_test.yaml từ template nếu chưa có
if [[ ! -f "config_test.yaml" ]]; then
    echo "📝 Creating config_test.yaml from template..."
    cp config_test.yaml.template config_test.yaml
    echo "⚠️  Please edit config_test.yaml with your VPS details for testing"
else
    echo "✅ config_test.yaml already exists"
fi

# Tạo thư mục cần thiết
echo "📁 Creating directories..."
mkdir -p backup_data logs tmp

# Check SSH key permissions
echo "🔑 Checking SSH key permissions..."
check_ssh_key_permissions() {
    local config_file="$1"
    if [[ -f "$config_file" ]]; then
        local ssh_key=$(grep "^ssh_key:" "$config_file" | cut -d' ' -f2 | tr -d '"' | tr -d "'")
        if [[ -n "$ssh_key" && -f "$ssh_key" ]]; then
            echo "Found SSH key: $ssh_key"
            local current_perm
            if [[ "$OSTYPE" == "darwin"* ]]; then
                current_perm=$(stat -f "%A" "$ssh_key" 2>/dev/null || echo "unknown")
            else
                current_perm=$(stat -c "%a" "$ssh_key" 2>/dev/null || echo "unknown")
            fi
            
            if [[ "$current_perm" != "600" ]]; then
                echo "🔧 Fixing SSH key permissions: $ssh_key"
                chmod 600 "$ssh_key"
                echo "✅ SSH key permissions set to 600"
            else
                echo "✅ SSH key permissions already correct (600)"
            fi
        else
            echo "⚠️  SSH key not found: $ssh_key"
            echo "   Make sure SSH key exists and run: chmod 600 /path/to/your/key"
        fi
    fi
}

check_ssh_key_permissions "config.yaml"
check_ssh_key_permissions "config_test.yaml"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit config.yaml with your VPS connection details"
echo "2. Make sure your SSH key has correct permissions (600)"
echo "3. Test connection: python3 quick_bandwidth.py"
echo "4. Run backup: ./backup_with_monitoring.sh"
echo ""
echo "💡 SSH Key Requirements:"
echo "   - Must have 600 permissions: chmod 600 /path/to/key"
echo "   - Use absolute path in config files"
echo "   - Test SSH connection: ssh -i /path/to/key user@host"
echo ""
echo "For help: ./backup_with_monitoring.sh and select option 4"
