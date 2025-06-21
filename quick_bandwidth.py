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
    
    # Tìm interface chính
    main_interface = None
    max_traffic = 0
    
    for interface in stats1:
        if interface in stats2:
            total_traffic = (stats2[interface]['rx_bytes'] + stats2[interface]['tx_bytes']) - \
                          (stats1[interface]['rx_bytes'] + stats1[interface]['tx_bytes'])
            if total_traffic > max_traffic:
                max_traffic = total_traffic
                main_interface = interface
    
    if main_interface:
        rx_diff = (stats2[main_interface]['rx_bytes'] - stats1[main_interface]['rx_bytes']) / 2
        tx_diff = (stats2[main_interface]['tx_bytes'] - stats1[main_interface]['tx_bytes']) / 2
        
        total_rx_gb = stats2[main_interface]['rx_bytes'] / 1024 / 1024 / 1024
        total_tx_gb = stats2[main_interface]['tx_bytes'] / 1024 / 1024 / 1024
        
        print(f"🔌 Interface: {main_interface}")
        print(f"⬇️  Download: {format_bytes(rx_diff)}")
        print(f"⬆️  Upload: {format_bytes(tx_diff)}")
        print(f"📊 Total: ⬇️ {total_rx_gb:.2f}GB | ⬆️ {total_tx_gb:.2f}GB")
        
        # Cảnh báo nếu băng thông cao
        if rx_diff > 50 * 1024 * 1024:  # > 50MB/s
            print("⚠️  HIGH DOWNLOAD TRAFFIC!")
        if tx_diff > 10 * 1024 * 1024:  # > 10MB/s
            print("⚠️  HIGH UPLOAD TRAFFIC!")
    else:
        print("❌ No active network interface found")

def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    
    try:
        cfg = load_config(config_file)
        quick_check(cfg)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
