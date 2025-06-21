#!/usr/bin/env python3
import subprocess
import time
import json
import yaml
from datetime import datetime

def load_config(path="config.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)

def run_ssh_command(cfg, command):
    """Chạy lệnh SSH trên VPS đích"""
    ssh_cmd = [
        'ssh',
        '-i', cfg['ssh_key'],
        '-p', str(cfg.get('ssh_port', 22)),
        f"{cfg['ssh_user']}@{cfg['ssh_host']}"
    ]
    
    try:
        result = subprocess.run(ssh_cmd + [command], 
                              capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return None
    except Exception as e:
        print(f"SSH Error: {e}")
        return None

def get_network_stats(cfg):
    """Lấy thống kê network từ /proc/net/dev"""
    command = "cat /proc/net/dev"
    output = run_ssh_command(cfg, command)
    
    if not output:
        return None
    
    lines = output.split('\n')
    stats = {}
    
    for line in lines[2:]:  # Skip header lines
        if ':' in line:
            parts = line.split(':')
            interface = parts[0].strip()
            
            # Skip loopback and docker interfaces
            if interface in ['lo'] or interface.startswith('docker'):
                continue
                
            data = parts[1].split()
            if len(data) >= 16:
                stats[interface] = {
                    'rx_bytes': int(data[0]),
                    'tx_bytes': int(data[8]),
                    'rx_packets': int(data[1]),
                    'tx_packets': int(data[9])
                }
    
    return stats

def get_bandwidth_usage(cfg):
    """Lấy thông tin sử dụng băng thông hiện tại"""
    # Lấy stats lần đầu
    stats1 = get_network_stats(cfg)
    if not stats1:
        return None
    
    time.sleep(1)  # Đợi 1 giây
    
    # Lấy stats lần thứ 2
    stats2 = get_network_stats(cfg)
    if not stats2:
        return None
    
    bandwidth = {}
    for interface in stats1:
        if interface in stats2:
            rx_diff = stats2[interface]['rx_bytes'] - stats1[interface]['rx_bytes']
            tx_diff = stats2[interface]['tx_bytes'] - stats1[interface]['tx_bytes']
            
            bandwidth[interface] = {
                'download_bps': rx_diff,  # bytes per second
                'upload_bps': tx_diff,
                'download_mbps': rx_diff * 8 / 1024 / 1024,  # Mbps
                'upload_mbps': tx_diff * 8 / 1024 / 1024,
                'total_rx_gb': stats2[interface]['rx_bytes'] / 1024 / 1024 / 1024,
                'total_tx_gb': stats2[interface]['tx_bytes'] / 1024 / 1024 / 1024
            }
    
    return bandwidth

def get_system_info(cfg):
    """Lấy thông tin hệ thống cơ bản"""
    commands = {
        'uptime': 'uptime',
        'load': 'cat /proc/loadavg',
        'memory': 'free -h',
        'disk_usage': 'df -h /',
    }
    
    info = {}
    for key, cmd in commands.items():
        info[key] = run_ssh_command(cfg, cmd)
    
    return info

def format_bytes(bytes_val):
    """Format bytes thành đơn vị dễ đọc"""
    for unit in ['B/s', 'KB/s', 'MB/s', 'GB/s']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} TB/s"

def monitor_bandwidth(cfg, duration=60, interval=5):
    """Monitor băng thông trong khoảng thời gian nhất định"""
    print(f"🔍 Monitoring VPS bandwidth: {cfg['ssh_host']}:{cfg['ssh_port']}")
    print(f"⏱️  Duration: {duration}s, Interval: {interval}s")
    print("=" * 80)
    
    max_download = 0
    max_upload = 0
    
    for i in range(0, duration, interval):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Lấy bandwidth stats
        bandwidth = get_bandwidth_usage(cfg)
        if not bandwidth:
            print(f"[{timestamp}] ❌ Unable to get bandwidth stats")
            continue
        
        # Tìm interface chính (thường là eth0, ens3, etc.)
        main_interface = None
        for iface in bandwidth:
            if iface.startswith(('eth', 'ens', 'enp')):
                main_interface = iface
                break
        
        if not main_interface and bandwidth:
            main_interface = list(bandwidth.keys())[0]
        
        if main_interface:
            stats = bandwidth[main_interface]
            download_speed = format_bytes(stats['download_bps'])
            upload_speed = format_bytes(stats['upload_bps'])
            
            # Cập nhật max speeds
            max_download = max(max_download, stats['download_bps'])
            max_upload = max(max_upload, stats['upload_bps'])
            
            print(f"[{timestamp}] 📡 {main_interface}: "
                  f"⬇️  {download_speed} | ⬆️  {upload_speed} | "
                  f"Total: ⬇️  {stats['total_rx_gb']:.2f}GB ⬆️  {stats['total_tx_gb']:.2f}GB")
        
        time.sleep(interval)
    
    print("=" * 80)
    print(f"📊 Max speeds observed:")
    print(f"   ⬇️  Download: {format_bytes(max_download)}")
    print(f"   ⬆️  Upload: {format_bytes(max_upload)}")

def check_current_bandwidth(cfg):
    """Kiểm tra băng thông hiện tại một lần"""
    print(f"🔍 Checking current bandwidth for {cfg['ssh_host']}...")
    
    # System info
    sys_info = get_system_info(cfg)
    if sys_info.get('uptime'):
        print(f"⏱️  Uptime: {sys_info['uptime']}")
    if sys_info.get('load'):
        print(f"📈 Load: {sys_info['load']}")
    
    # Bandwidth
    bandwidth = get_bandwidth_usage(cfg)
    if not bandwidth:
        print("❌ Unable to get bandwidth stats")
        return
    
    print("\n📡 Network Interfaces:")
    for interface, stats in bandwidth.items():
        download_speed = format_bytes(stats['download_bps'])
        upload_speed = format_bytes(stats['upload_bps'])
        
        print(f"   {interface}: ⬇️  {download_speed} | ⬆️  {upload_speed}")
        print(f"            Total: ⬇️  {stats['total_rx_gb']:.2f}GB | ⬆️  {stats['total_tx_gb']:.2f}GB")

def main():
    import sys
    
    config_file = "config.yaml"
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("Usage:")
            print("  python3 monitor_bandwidth.py [config_file] [action] [options]")
            print("")
            print("Actions:")
            print("  check    - Check current bandwidth once (default)")
            print("  monitor  - Monitor bandwidth continuously")
            print("")
            print("Examples:")
            print("  python3 monitor_bandwidth.py")
            print("  python3 monitor_bandwidth.py config_test.yaml")
            print("  python3 monitor_bandwidth.py config.yaml monitor")
            print("  python3 monitor_bandwidth.py config.yaml monitor 120 3  # 120s, 3s interval")
            return
        
        config_file = sys.argv[1]
    
    try:
        cfg = load_config(config_file)
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return
    
    action = sys.argv[2] if len(sys.argv) > 2 else "check"
    
    if action == "monitor":
        duration = int(sys.argv[3]) if len(sys.argv) > 3 else 60
        interval = int(sys.argv[4]) if len(sys.argv) > 4 else 5
        monitor_bandwidth(cfg, duration, interval)
    else:
        check_current_bandwidth(cfg)

if __name__ == '__main__':
    main()
