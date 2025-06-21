#!/usr/bin/env python3
"""
VPS Backup Tool - Application Launcher
Công cụ backup VPS với monitoring băng thông và screen session support

Author: Backup Tool Team
Version: 2.0
"""

import os
import sys
import platform
import subprocess
import importlib.util
from pathlib import Path

class AppLauncher:
    """Lớp khởi động ứng dụng với kiểm tra dependencies và cấu hình"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.required_packages = ['PyYAML', 'rich']
        self.required_commands = ['rsync', 'ssh', 'screen']
        self.config_dir = self.script_dir / 'configs'
        self.src_dir = self.script_dir / 'src'
        
    def check_python_version(self):
        """Kiểm tra phiên bản Python"""
        if sys.version_info < (3, 6):
            print("❌ Lỗi: Cần Python 3.6 hoặc cao hơn")
            print(f"   Phiên bản hiện tại: {sys.version}")
            return False
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        return True
        
    def check_operating_system(self):
        """Kiểm tra hệ điều hành được hỗ trợ"""
        os_name = platform.system()
        print(f"🖥️  Hệ điều hành: {os_name} {platform.release()}")
        
        if os_name not in ['Linux', 'Darwin']:
            print(f"⚠️  Cảnh báo: Hệ điều hành {os_name} có thể không được hỗ trợ đầy đủ")
            return False
        return True
        
    def check_package_installed(self, package_name):
        """Kiểm tra package Python đã cài đặt chưa"""
        try:
            spec = importlib.util.find_spec(package_name.lower())
            return spec is not None
        except ImportError:
            return False
            
    def install_package(self, package_name):
        """Cài đặt package Python"""
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', package_name
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False
            
    def check_command_exists(self, command):
        """Kiểm tra lệnh có tồn tại trên hệ thống không"""
        try:
            subprocess.run(['which', command], 
                         check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False
            
    def install_system_packages(self):
        """Cài đặt các gói hệ thống cần thiết"""
        os_name = platform.system()
        
        if os_name == 'Darwin':  # macOS
            print("📦 Đang kiểm tra Homebrew...")
            if not self.check_command_exists('brew'):
                print("❌ Homebrew không được cài đặt. Vui lòng cài đặt Homebrew trước:")
                print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
                return False
                
            missing_packages = []
            for cmd in self.required_commands:
                if not self.check_command_exists(cmd):
                    missing_packages.append(cmd)
                    
            if missing_packages:
                print(f"🔧 Đang cài đặt các gói thiếu: {', '.join(missing_packages)}")
                for package in missing_packages:
                    if package == 'screen':
                        package = 'screen'
                    try:
                        subprocess.check_call(['brew', 'install', package])
                        print(f"✅ Đã cài đặt {package}")
                    except subprocess.CalledProcessError:
                        print(f"❌ Không thể cài đặt {package}")
                        return False
                        
        elif os_name == 'Linux':
            # Phát hiện package manager
            if self.check_command_exists('apt'):
                package_manager = 'apt'
                install_cmd = ['sudo', 'apt', 'update', '&&', 'sudo', 'apt', 'install', '-y']
            elif self.check_command_exists('yum'):
                package_manager = 'yum'
                install_cmd = ['sudo', 'yum', 'install', '-y']
            elif self.check_command_exists('dnf'):
                package_manager = 'dnf'
                install_cmd = ['sudo', 'dnf', 'install', '-y']
            else:
                print("❌ Không tìm thấy package manager được hỗ trợ (apt/yum/dnf)")
                return False
                
            missing_packages = []
            for cmd in self.required_commands:
                if not self.check_command_exists(cmd):
                    missing_packages.append(cmd)
                    
            if missing_packages:
                print(f"🔧 Đang cài đặt các gói thiếu bằng {package_manager}: {', '.join(missing_packages)}")
                try:
                    if package_manager == 'apt':
                        subprocess.check_call(['sudo', 'apt', 'update'])
                        subprocess.check_call(['sudo', 'apt', 'install', '-y'] + missing_packages)
                    else:
                        subprocess.check_call(['sudo', package_manager, 'install', '-y'] + missing_packages)
                    print("✅ Đã cài đặt tất cả gói hệ thống cần thiết")
                except subprocess.CalledProcessError:
                    print("❌ Không thể cài đặt một số gói hệ thống")
                    return False
                    
        return True
        
    def check_python_packages(self):
        """Kiểm tra và cài đặt Python packages"""
        print("🐍 Đang kiểm tra Python packages...")
        
        missing_packages = []
        for package in self.required_packages:
            if not self.check_package_installed(package):
                missing_packages.append(package)
            else:
                print(f"✅ {package}")
                
        if missing_packages:
            print(f"📦 Đang cài đặt packages thiếu: {', '.join(missing_packages)}")
            for package in missing_packages:
                if self.install_package(package):
                    print(f"✅ Đã cài đặt {package}")
                else:
                    print(f"❌ Không thể cài đặt {package}")
                    return False
                    
        return True
        
    def check_system_commands(self):
        """Kiểm tra các lệnh hệ thống cần thiết"""
        print("🔧 Đang kiểm tra system commands...")
        
        all_ok = True
        for cmd in self.required_commands:
            if self.check_command_exists(cmd):
                print(f"✅ {cmd}")
            else:
                print(f"❌ {cmd} - không tìm thấy")
                all_ok = False
                
        return all_ok
        
    def check_configuration(self):
        """Kiểm tra file cấu hình"""
        print("⚙️  Đang kiểm tra cấu hình...")
        
        config_file = self.config_dir / 'config.yaml'
        template_file = self.config_dir / 'config.yaml.template'
        
        if not config_file.exists():
            if template_file.exists():
                print(f"📋 Tạo file cấu hình từ template: {config_file}")
                import shutil
                shutil.copy2(template_file, config_file)
                print("⚠️  Vui lòng chỉnh sửa file cấu hình trước khi sử dụng:")
                print(f"   {config_file}")
                return False
            else:
                print(f"❌ Không tìm thấy file cấu hình: {config_file}")
                return False
                
        return True
        
    def test_ssh_connection(self, config):
        """Test kết nối SSH"""
        print("🔐 Đang test kết nối SSH...")
        
        try:
            ssh_cmd = [
                'ssh',
                '-i', config['ssh_key'],
                '-p', str(config.get('ssh_port', 22)),
                '-o', 'ConnectTimeout=10',
                '-o', 'BatchMode=yes',
                f"{config['ssh_user']}@{config['ssh_host']}",
                'echo "SSH connection successful"'
            ]
            
            result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print("✅ Kết nối SSH thành công")
                return True
            else:
                print(f"❌ Kết nối SSH thất bại: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Kết nối SSH timeout")
            return False
        except Exception as e:
            print(f"❌ Lỗi kết nối SSH: {e}")
            return False
            
    def check_paths(self, config):
        """Kiểm tra đường dẫn nguồn và đích"""
        print("📂 Đang kiểm tra đường dẫn...")
        
        # Kiểm tra SSH key
        ssh_key = Path(config['ssh_key'])
        if not ssh_key.exists():
            print(f"❌ SSH key không tồn tại: {ssh_key}")
            return False
        print(f"✅ SSH key: {ssh_key}")
        
        # Kiểm tra local destination
        local_root = Path(config['local_root'])
        local_root.mkdir(parents=True, exist_ok=True)
        print(f"✅ Local destination: {local_root}")
        
        # Kiểm tra remote path (qua SSH)
        try:
            ssh_cmd = [
                'ssh',
                '-i', config['ssh_key'],
                '-p', str(config.get('ssh_port', 22)),
                f"{config['ssh_user']}@{config['ssh_host']}",
                f'[ -d "{config["remote_root"]}" ] && echo "EXISTS" || echo "NOT_EXISTS"'
            ]
            
            result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and 'EXISTS' in result.stdout:
                print(f"✅ Remote path: {config['remote_root']}")
                return True
            else:
                print(f"❌ Remote path không tồn tại: {config['remote_root']}")
                return False
                
        except Exception as e:
            print(f"❌ Không thể kiểm tra remote path: {e}")
            return False
            
    def load_config(self):
        """Load cấu hình"""
        try:
            import yaml
            config_file = self.config_dir / 'config.yaml'
            
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Không thể đọc file cấu hình: {e}")
            return None
            
    def run_system_checks(self):
        """Chạy tất cả kiểm tra hệ thống"""
        print("🚀 VPS Backup Tool - System Check")
        print("=" * 50)
        
        # Kiểm tra Python version
        if not self.check_python_version():
            return False
            
        # Kiểm tra OS
        if not self.check_operating_system():
            return False
            
        # Kiểm tra và cài đặt system commands
        if not self.check_system_commands():
            print("🔧 Đang cài đặt system packages...")
            if not self.install_system_packages():
                return False
            # Kiểm tra lại sau khi cài đặt
            if not self.check_system_commands():
                return False
                
        # Kiểm tra Python packages
        if not self.check_python_packages():
            return False
            
        # Kiểm tra cấu hình
        if not self.check_configuration():
            return False
            
        print("✅ Tất cả kiểm tra hệ thống đã hoàn thành")
        return True
        
    def run_config_checks(self):
        """Chạy kiểm tra cấu hình và kết nối"""
        print("\n🔍 Đang kiểm tra cấu hình và kết nối...")
        print("=" * 50)
        
        # Load config
        config = self.load_config()
        if not config:
            return False
            
        # Kiểm tra đường dẫn
        if not self.check_paths(config):
            return False
            
        # Test SSH connection
        if not self.test_ssh_connection(config):
            return False
            
        print("✅ Tất cả kiểm tra cấu hình đã hoàn thành")
        return True
        
    def launch_application(self):
        """Khởi động ứng dụng chính"""
        try:
            # Add src directory to Python path
            sys.path.insert(0, str(self.src_dir))
            
            # Import và chạy main application
            from ui.main_menu import BackupApplication
            
            app = BackupApplication()
            app.run()
            
        except ImportError as e:
            print(f"❌ Không thể import ứng dụng: {e}")
            return False
        except Exception as e:
            print(f"❌ Lỗi khi khởi động ứng dụng: {e}")
            return False
            
        return True
        
    def run(self):
        """Chạy toàn bộ quá trình khởi động"""
        try:
            # Kiểm tra hệ thống
            if not self.run_system_checks():
                print("\n❌ Kiểm tra hệ thống thất bại. Vui lòng khắc phục lỗi và thử lại.")
                return False
                
            # Kiểm tra cấu hình
            if not self.run_config_checks():
                print("\n❌ Kiểm tra cấu hình thất bại. Vui lòng khắc phục lỗi và thử lại.")
                return False
                
            # Khởi động ứng dụng
            print("\n🎉 Hệ thống sẵn sàng! Đang khởi động ứng dụng...")
            print("=" * 50)
            
            return self.launch_application()
            
        except KeyboardInterrupt:
            print("\n👋 Ứng dụng đã được dừng bởi người dùng")
            return True
        except Exception as e:
            print(f"\n❌ Lỗi không mong muốn: {e}")
            return False

def main():
    """Entry point"""
    launcher = AppLauncher()
    success = launcher.run()
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()
