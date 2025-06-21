"""
SSH connection and testing utilities
"""

import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

class SSHManager:
    """Quản lý kết nối SSH và các thao tác remote"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ssh_base_cmd = self._build_ssh_command()
        
    def _build_ssh_command(self) -> list:
        """Build base SSH command"""
        return [
            'ssh',
            '-i', str(Path(self.config['ssh_key']).expanduser()),
            '-p', str(self.config.get('ssh_port', 22)),
            '-o', 'ConnectTimeout=30',
            '-o', 'ServerAliveInterval=60',
            '-o', 'ServerAliveCountMax=3',
            '-o', 'BatchMode=yes',  # Non-interactive mode
            f"{self.config['ssh_user']}@{self.config['ssh_host']}"
        ]
        
    def test_connection(self, timeout: int = 15) -> Tuple[bool, str]:
        """Test SSH connection"""
        try:
            cmd = self.ssh_base_cmd + ['echo "SSH connection successful"']
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                return True, "Connection successful"
            else:
                error_msg = result.stderr.strip() or "Unknown error"
                return False, f"Connection failed: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, "Connection timeout"
        except FileNotFoundError:
            return False, "SSH command not found"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
            
    def run_command(self, command: str, timeout: int = 30) -> Tuple[bool, str, str]:
        """Run remote command via SSH"""
        try:
            cmd = self.ssh_base_cmd + [command]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return (
                result.returncode == 0,
                result.stdout.strip(),
                result.stderr.strip()
            )
            
        except subprocess.TimeoutExpired:
            return False, "", "Command timeout"
        except Exception as e:
            return False, "", f"Command error: {str(e)}"
            
    def check_remote_path(self, path: str) -> Tuple[bool, str]:
        """Check if remote path exists"""
        success, stdout, stderr = self.run_command(
            f'[ -d "{path}" ] && echo "EXISTS" || echo "NOT_EXISTS"'
        )
        
        if success and "EXISTS" in stdout:
            return True, f"Path exists: {path}"
        elif success and "NOT_EXISTS" in stdout:
            return False, f"Path does not exist: {path}"
        else:
            return False, f"Cannot check path: {stderr}"
            
    def get_remote_info(self) -> Dict[str, Any]:
        """Get remote system information"""
        info = {}
        
        commands = {
            'hostname': 'hostname',
            'os': 'uname -a',
            'uptime': 'uptime',
            'disk_usage': f'df -h "{self.config["remote_root"]}"',
            'memory': 'free -h',
            'user': 'whoami'
        }
        
        for key, command in commands.items():
            success, stdout, stderr = self.run_command(command)
            if success:
                info[key] = stdout
            else:
                info[key] = f"Error: {stderr}"
                
        return info
        
    def test_rsync_connection(self) -> Tuple[bool, str]:
        """Test rsync connection by doing a dry run"""
        try:
            ssh_cmd = f"ssh -i {Path(self.config['ssh_key']).expanduser()} -p {self.config.get('ssh_port', 22)}"
            
            # Create a temporary test file on remote
            test_file = '/tmp/backup_test_file'
            success, _, _ = self.run_command(f'echo "test" > {test_file}')
            
            if not success:
                return False, "Cannot create test file on remote"
                
            # Test rsync dry run
            rsync_cmd = [
                'rsync',
                '--dry-run',
                '-e', ssh_cmd,
                f"{self.config['ssh_user']}@{self.config['ssh_host']}:{test_file}",
                '/tmp/'
            ]
            
            result = subprocess.run(
                rsync_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Cleanup test file
            self.run_command(f'rm -f {test_file}')
            
            if result.returncode == 0:
                return True, "Rsync connection successful"
            else:
                return False, f"Rsync failed: {result.stderr}"
                
        except Exception as e:
            return False, f"Rsync test error: {str(e)}"

class NetworkInterfaceMonitor:
    """Monitor network interfaces on remote server"""
    
    def __init__(self, ssh_manager: SSHManager):
        self.ssh = ssh_manager
        
    def get_network_stats(self) -> Optional[Dict[str, Dict[str, int]]]:
        """Get network statistics from /proc/net/dev"""
        success, output, _ = self.ssh.run_command("cat /proc/net/dev")
        
        if not success or not output:
            return None
            
        stats = {}
        lines = output.split('\n')
        
        for line in lines[2:]:  # Skip header lines
            if ':' in line:
                parts = line.split(':')
                interface = parts[0].strip()
                
                # Skip virtual/container interfaces
                skip_patterns = ['lo', 'docker', 'br-', 'veth', 'virbr', 'tun', 'tap']
                if any(interface.startswith(pattern) for pattern in skip_patterns):
                    continue
                    
                data = parts[1].split()
                if len(data) >= 16:
                    try:
                        stats[interface] = {
                            'rx_bytes': int(data[0]),
                            'tx_bytes': int(data[8]),
                            'rx_packets': int(data[1]),
                            'tx_packets': int(data[9])
                        }
                    except (ValueError, IndexError):
                        continue
                        
        return stats
        
    def get_bandwidth_usage(self, interval: float = 1.0) -> Optional[Dict[str, Any]]:
        """Calculate bandwidth usage over interval"""
        stats1 = self.get_network_stats()
        if not stats1:
            return None
            
        time.sleep(interval)
        
        stats2 = self.get_network_stats()
        if not stats2:
            return None
            
        interfaces_data = {}
        total_download = 0
        total_upload = 0
        
        for interface in stats1:
            if interface in stats2:
                rx_diff = stats2[interface]['rx_bytes'] - stats1[interface]['rx_bytes']
                tx_diff = stats2[interface]['tx_bytes'] - stats1[interface]['tx_bytes']
                
                # Calculate rate per second
                rx_rate = max(0, rx_diff / interval)
                tx_rate = max(0, tx_diff / interval)
                
                interfaces_data[interface] = {
                    'download_bps': rx_rate,
                    'upload_bps': tx_rate,
                    'total_rx_gb': stats2[interface]['rx_bytes'] / 1024 / 1024 / 1024,
                    'total_tx_gb': stats2[interface]['tx_bytes'] / 1024 / 1024 / 1024,
                    'is_active': rx_rate > 0 or tx_rate > 0
                }
                
                total_download += rx_rate
                total_upload += tx_rate
                
        if interfaces_data:
            active_interfaces = {k: v for k, v in interfaces_data.items() if v['is_active']}
            main_interface = None
            
            if active_interfaces:
                main_interface = max(
                    active_interfaces.keys(),
                    key=lambda x: active_interfaces[x]['download_bps'] + active_interfaces[x]['upload_bps']
                )
                
            return {
                'interfaces': interfaces_data,
                'active_interfaces': active_interfaces,
                'main_interface': main_interface,
                'total_download_bps': total_download,
                'total_upload_bps': total_upload,
                'interface_count': len(interfaces_data),
                'active_count': len(active_interfaces)
            }
            
        return None
        
    def test_interfaces(self) -> Dict[str, Any]:
        """Test and get information about network interfaces"""
        result = {
            'interfaces_found': [],
            'active_interfaces': [],
            'total_interfaces': 0,
            'test_successful': False
        }
        
        try:
            # Get current stats
            stats = self.get_network_stats()
            if stats:
                result['interfaces_found'] = list(stats.keys())
                result['total_interfaces'] = len(stats)
                
                # Test bandwidth measurement
                bandwidth = self.get_bandwidth_usage(interval=2.0)
                if bandwidth:
                    result['active_interfaces'] = list(bandwidth['active_interfaces'].keys())
                    result['test_successful'] = True
                    result['bandwidth_data'] = bandwidth
                    
        except Exception as e:
            result['error'] = str(e)
            
        return result
