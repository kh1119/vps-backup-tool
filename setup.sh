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

# Kiểm tra pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed"
    exit 1
fi

echo "✅ pip3 found"

# Cài đặt dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

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

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit config.yaml with your VPS connection details"
echo "2. Make sure your SSH key is properly configured"
echo "3. Test connection: python3 quick_bandwidth.py"
echo "4. Run backup: ./backup_with_monitoring.sh"
echo ""
echo "For help: ./backup_with_monitoring.sh and select option 4"
