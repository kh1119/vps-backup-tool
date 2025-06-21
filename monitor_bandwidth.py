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
                    continue  # Skip malformed data
    
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
    total_download = 0
    total_upload = 0
    active_count = 0
    
    for interface in stats1:
        if interface in stats2:
            rx_diff = stats2[interface]['rx_bytes'] - stats1[interface]['rx_bytes']
            tx_diff = stats2[interface]['tx_bytes'] - stats1[interface]['tx_bytes']
            
            # Đảm bảo không âm và lưu tất cả interfaces
            rx_diff = max(0, rx_diff)
            tx_diff = max(0, tx_diff)
            
            bandwidth[interface] = {
                'download_bps': rx_diff,  # bytes per second
                'upload_bps': tx_diff,
                'download_mbps': rx_diff * 8 / 1024 / 1024,  # Mbps
                'upload_mbps': tx_diff * 8 / 1024 / 1024,
                'total_rx_gb': stats2[interface]['rx_bytes'] / 1024 / 1024 / 1024,
                'total_tx_gb': stats2[interface]['tx_bytes'] / 1024 / 1024 / 1024,
                'is_active': rx_diff > 0 or tx_diff > 0
            }
            
            total_download += rx_diff
            total_upload += tx_diff
            if rx_diff > 0 or tx_diff > 0:
                active_count += 1
    
    # Thêm thống kê tổng
    return {
        'interfaces': bandwidth,
        'total_download_bps': total_download,
        'total_upload_bps': total_upload,
        'interface_count': len(bandwidth),
        'active_count': active_count
    }

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
    
    max_total_download = 0
    max_total_upload = 0
    
    for i in range(0, duration, interval):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Lấy bandwidth stats
        bandwidth = get_bandwidth_usage(cfg)
        if not bandwidth:
            print(f"[{timestamp}] ❌ Unable to get bandwidth stats")
            continue
        
        # Tính tổng bandwidth
        total_download = sum(data['download_bps'] for data in bandwidth.values())
        total_upload = sum(data['upload_bps'] for data in bandwidth.values())
        
        max_total_download = max(max_total_download, total_download)
        max_total_upload = max(max_total_upload, total_upload)
        
        # Hiển thị tổng
        total_down_str = format_bytes(total_download)
        total_up_str = format_bytes(total_upload)
        print(f"[{timestamp}] 📊 Total: ⬇️ {total_down_str} | ⬆️ {total_up_str}")
        
        # Hiển thị top interfaces có traffic
        active_interfaces = [(iface, data) for iface, data in bandwidth.items() 
                           if data['download_bps'] > 1024 or data['upload_bps'] > 1024]  # > 1KB/s
        
        if active_interfaces:
            active_interfaces.sort(key=lambda x: x[1]['download_bps'] + x[1]['upload_bps'], reverse=True)
            top_interfaces = active_interfaces[:3]  # Top 3
            
            if len(active_interfaces) > 1:
                print(f"         Active interfaces ({len(active_interfaces)} total):")
                for iface, data in top_interfaces:
                    down = format_bytes(data['download_bps'])
                    up = format_bytes(data['upload_bps'])
                    print(f"           {iface}: ⬇️ {down} | ⬆️ {up}")
        
        time.sleep(interval)
    
    print("=" * 80)
    print(f"📊 Max total speeds observed:")
    print(f"   ⬇️ Download: {format_bytes(max_total_download)}")
    print(f"   ⬆️ Upload: {format_bytes(max_total_upload)}")

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
    
    # Tính tổng
    total_download = sum(data['download_bps'] for data in bandwidth.values())
    total_upload = sum(data['upload_bps'] for data in bandwidth.values())
    
    print(f"\n📊 Total Bandwidth: ⬇️ {format_bytes(total_download)} | ⬆️ {format_bytes(total_upload)}")
    print(f"� Active Interfaces: {len([i for i, d in bandwidth.items() if d['download_bps'] > 0 or d['upload_bps'] > 0])}")
    
    print("\n�📡 Network Interfaces:")
    
    # Sắp xếp theo traffic
    sorted_interfaces = sorted(bandwidth.items(), 
                             key=lambda x: x[1]['download_bps'] + x[1]['upload_bps'], 
                             reverse=True)
    
    for interface, stats in sorted_interfaces:
        download_speed = format_bytes(stats['download_bps'])
        upload_speed = format_bytes(stats['upload_bps'])
        
        status = ""
        if stats['download_bps'] > 50 * 1024 * 1024:  # > 50MB/s
            status += " ⚠️ HIGH DOWNLOAD"
        if stats['upload_bps'] > 10 * 1024 * 1024:  # > 10MB/s
            status += " ⚠️ HIGH UPLOAD"
        
        print(f"   {interface}: ⬇️ {download_speed} | ⬆️ {upload_speed}{status}")
        print(f"            Total: ⬇️ {stats['total_rx_gb']:.2f}GB | ⬆️ {stats['total_tx_gb']:.2f}GB")
    
    # Cảnh báo tổng
    if total_download > 100 * 1024 * 1024:  # > 100MB/s
        print(f"\n⚠️  VERY HIGH TOTAL DOWNLOAD TRAFFIC!")
    if total_upload > 20 * 1024 * 1024:  # > 20MB/s  
        print(f"\n⚠️  HIGH TOTAL UPLOAD TRAFFIC!")

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
