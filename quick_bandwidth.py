#!/usr/bin/env python3
"""
Quick bandwidth checker - sử dụng code từ main.py để kiểm tra nhanh băng thông
"""
import sys
import time
import yaml
import subprocess
from datetime import datetime

def load_config(path="config.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)

def run_ssh_command(cfg, command):
    ssh_cmd = [
        'ssh',
        '-i', cfg['ssh_key'],
        '-p', str(cfg.get('ssh_port', 22)),
        f"{cfg['ssh_user']}@{cfg['ssh_host']}"
    ]
    
    try:
        result = subprocess.run(ssh_cmd + [command], 
                              capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    except:
        return None

def get_network_stats(cfg):
    command = "cat /proc/net/dev"
    output = run_ssh_command(cfg, command)
    
    if not output:
        return None
    
    lines = output.split('\n')
    stats = {}
    
    for line in lines[2:]:
        if ':' in line:
            parts = line.split(':')
            interface = parts[0].strip()
            
            if interface in ['lo'] or interface.startswith('docker'):
                continue
                
            data = parts[1].split()
            if len(data) >= 16:
                stats[interface] = {
                    'rx_bytes': int(data[0]),
                    'tx_bytes': int(data[8])
                }
    
    return stats

def format_bytes(bytes_val):
    for unit in ['B/s', 'KB/s', 'MB/s', 'GB/s']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} TB/s"

def quick_check(cfg):
    """Kiểm tra băng thông nhanh"""
    print(f"📡 Checking bandwidth for {cfg['ssh_host']}...")
    
    stats1 = get_network_stats(cfg)
    if not stats1:
        print("❌ Cannot get network stats")
        return
    
    time.sleep(2)  # Đợi 2 giây
    
    stats2 = get_network_stats(cfg)
    if not stats2:
        print("❌ Cannot get network stats")
        return
    
    interfaces_data = {}
    total_download = 0
    total_upload = 0
    
    for interface in stats1:
        if interface in stats2:
            rx_diff = (stats2[interface]['rx_bytes'] - stats1[interface]['rx_bytes']) / 2
            tx_diff = (stats2[interface]['tx_bytes'] - stats1[interface]['tx_bytes']) / 2
            
            total_rx_gb = stats2[interface]['rx_bytes'] / 1024 / 1024 / 1024
            total_tx_gb = stats2[interface]['tx_bytes'] / 1024 / 1024 / 1024
            
            interfaces_data[interface] = {
                'download_bps': rx_diff,
                'upload_bps': tx_diff,
                'total_rx_gb': total_rx_gb,
                'total_tx_gb': total_tx_gb
            }
            
            total_download += rx_diff
            total_upload += tx_diff
    
    # Hiển thị tổng bandwidth
    print(f"📊 Total Bandwidth: ⬇️ {format_bytes(total_download)} | ⬆️ {format_bytes(total_upload)}")
    print(f"📈 Active Interfaces: {len([i for i, d in interfaces_data.items() if d['download_bps'] > 0 or d['upload_bps'] > 0])}")
    
    # Hiển thị từng interface
    print(f"\n🔌 Interface Details:")
    active_interfaces = [(iface, data) for iface, data in interfaces_data.items()]
    
    # Sắp xếp theo total traffic
    active_interfaces.sort(key=lambda x: x[1]['download_bps'] + x[1]['upload_bps'], reverse=True)
    
    for iface, data in active_interfaces:
        download_speed = format_bytes(data['download_bps'])
        upload_speed = format_bytes(data['upload_bps'])
        
        status = ""
        if data['download_bps'] > 50 * 1024 * 1024:  # > 50MB/s
            status += " ⚠️ HIGH DOWNLOAD"
        if data['upload_bps'] > 10 * 1024 * 1024:  # > 10MB/s
            status += " ⚠️ HIGH UPLOAD"
        
        print(f"   {iface}: ⬇️ {download_speed} | ⬆️ {upload_speed}")
        print(f"             Total: ⬇️ {data['total_rx_gb']:.2f}GB | ⬆️ {data['total_tx_gb']:.2f}GB{status}")
    
    # Cảnh báo tổng băng thông
    if total_download > 100 * 1024 * 1024:  # > 100MB/s total
        print(f"\n⚠️  VERY HIGH TOTAL DOWNLOAD TRAFFIC!")
    elif total_download > 50 * 1024 * 1024:  # > 50MB/s total
        print(f"\n⚠️  HIGH TOTAL DOWNLOAD TRAFFIC!")
    
    if total_upload > 20 * 1024 * 1024:  # > 20MB/s total
        print(f"\n⚠️  HIGH TOTAL UPLOAD TRAFFIC!")

def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    
    try:
        cfg = load_config(config_file)
        quick_check(cfg)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
