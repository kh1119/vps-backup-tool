# backup.py
import os
import yaml
import subprocess
import time
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

def detect_screen_session():
    """Phát hiện nếu đang chạy trong screen session"""
    if 'STY' in os.environ:
        session_info = os.environ['STY']
        return session_info
    return None

def print_session_info():
    """Hiển thị thông tin session nếu đang chạy trong screen"""
    session = detect_screen_session()
    if session:
        print("🖥️  Running in screen session:", session)
        print("   Detach: Ctrl+A, then D")
        print("   Attach: screen -r", session)
        print("=" * 50)
    return session

# Load configuration
def load_config(path="config.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)

# Bandwidth monitoring functions
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
                              capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    except:
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

def format_bytes(bytes_val):
    """Format bytes thành đơn vị dễ đọc"""
    for unit in ['B/s', 'KB/s', 'MB/s', 'GB/s']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} TB/s"

def get_bandwidth_usage(cfg):
    """Lấy thông tin sử dụng băng thông hiện tại cho tất cả interfaces"""
    stats1 = get_network_stats(cfg)
    if not stats1:
        return None
    
    time.sleep(1)
    
    stats2 = get_network_stats(cfg)
    if not stats2:
        return None
    
    interfaces_data = {}
    total_download = 0
    total_upload = 0
    
    for interface in stats1:
        if interface in stats2:
            rx_diff = stats2[interface]['rx_bytes'] - stats1[interface]['rx_bytes']
            tx_diff = stats2[interface]['tx_bytes'] - stats1[interface]['tx_bytes']
            
            # Lưu tất cả interfaces, kể cả không có traffic
            interfaces_data[interface] = {
                'download_bps': max(0, rx_diff),  # Đảm bảo không âm
                'upload_bps': max(0, tx_diff),
                'total_rx_gb': stats2[interface]['rx_bytes'] / 1024 / 1024 / 1024,
                'total_tx_gb': stats2[interface]['tx_bytes'] / 1024 / 1024 / 1024,
                'is_active': rx_diff > 0 or tx_diff > 0
            }
            
            total_download += max(0, rx_diff)
            total_upload += max(0, tx_diff)
    
    if interfaces_data:
        # Tìm interface có traffic cao nhất
        active_interfaces = {k: v for k, v in interfaces_data.items() if v['is_active']}
        main_interface = None
        
        if active_interfaces:
            main_interface = max(active_interfaces.keys(), 
                               key=lambda x: active_interfaces[x]['download_bps'] + active_interfaces[x]['upload_bps'])
        
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

class BandwidthMonitor:
    """Thread để monitor băng thông trong background"""
    def __init__(self, cfg, interval=10):
        self.cfg = cfg
        self.interval = interval
        self.running = False
        self.thread = None
        self.max_total_download = 0
        self.max_total_upload = 0
        self.current_total_download = 0
        self.current_total_upload = 0
        self.current_interfaces = {}
    
    def start(self):
        """Bắt đầu monitoring"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print(f"🔍 Bandwidth monitoring started for {self.cfg['ssh_host']} (interval: {self.interval}s)")
    
    def stop(self):
        """Dừng monitoring"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print(f"\n📊 Max total bandwidth observed: ⬇️ {format_bytes(self.max_total_download)} | ⬆️ {format_bytes(self.max_total_upload)}")
    
    def _monitor_loop(self):
        """Loop chính của monitoring"""
        while self.running:
            try:
                bandwidth = get_bandwidth_usage(self.cfg)
                if bandwidth:
                    self.current_total_download = bandwidth['total_download_bps']
                    self.current_total_upload = bandwidth['total_upload_bps']
                    self.current_interfaces = bandwidth['interfaces']
                    
                    self.max_total_download = max(self.max_total_download, self.current_total_download)
                    self.max_total_upload = max(self.max_total_upload, self.current_total_upload)
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    # Hiển thị tổng bandwidth
                    total_down = format_bytes(self.current_total_download)
                    total_up = format_bytes(self.current_total_upload)
                    interface_info = f"({bandwidth['active_count']}/{bandwidth['interface_count']} active)"
                    print(f"[{timestamp}] 📊 Total: ⬇️ {total_down} | ⬆️ {total_up} {interface_info}")
                    
                    # Hiển thị interfaces có traffic cao
                    active_interfaces = [(iface, data) for iface, data in bandwidth['active_interfaces'].items()]
                    
                    if active_interfaces:
                        if len(active_interfaces) > 1:
                            print(f"         Active interfaces:")
                            for iface, data in sorted(active_interfaces, 
                                                    key=lambda x: x[1]['download_bps'] + x[1]['upload_bps'], 
                                                    reverse=True)[:3]:  # Top 3
                                down = format_bytes(data['download_bps'])
                                up = format_bytes(data['upload_bps'])
                                print(f"           {iface}: ⬇️ {down} | ⬆️ {up}")
                        elif bandwidth['main_interface']:
                            # Chỉ có 1 interface active, hiển thị tên
                            print(f"         Main interface: {bandwidth['main_interface']}")
                    
                    # Cảnh báo nếu traffic cao
                    if self.current_total_download > 100 * 1024 * 1024:  # > 100MB/s
                        print(f"         ⚠️  HIGH DOWNLOAD TRAFFIC!")
                    if self.current_total_upload > 50 * 1024 * 1024:  # > 50MB/s
                        print(f"         ⚠️  HIGH UPLOAD TRAFFIC!")
                
                time.sleep(self.interval)
            except Exception as e:
                if self.running:  # Chỉ print lỗi nếu vẫn đang chạy
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Bandwidth monitoring error: {e}")
                time.sleep(self.interval)

# Step 1: Build full file list from remote
def build_file_list(cfg):
    tmp_all = os.path.join(cfg['tmp_dir'], 'all_files.txt')
    os.makedirs(cfg['tmp_dir'], exist_ok=True)
    ssh_cmd = [
        'ssh',
        '-i', cfg['ssh_key'],
        '-p', str(cfg.get('ssh_port', 22)),
        f"{cfg['ssh_user']}@{cfg['ssh_host']}"
    ]
    # find files remotely
    cmd = ssh_cmd + ['find', cfg['remote_root'], '-type', 'f']
    with open(tmp_all, 'w') as outf:
        subprocess.run(cmd, check=True, stdout=outf)
    return tmp_all

# Step 2: Chunk file list into N parts
def chunk_file_list(all_files, cfg):
    chunks = []
    with open(all_files) as f:
        lines = [l.strip() for l in f if l.strip()]
    
    # Remove remote_root prefix from paths để tránh duplicate paths
    remote_root = cfg['remote_root'].rstrip('/')
    processed_lines = []
    for line in lines:
        if line.startswith(remote_root):
            # Remove remote_root prefix, keeping the relative path
            relative_path = line[len(remote_root):].lstrip('/')
            if relative_path:  # Skip empty paths
                processed_lines.append(relative_path)
        else:
            # If line doesn't start with remote_root, keep as is
            processed_lines.append(line)
    
    n = cfg['threads']
    for i in range(n):
        chunk_path = os.path.join(cfg['tmp_dir'], f'chunk_{i+1}.txt')
        chunks.append(chunk_path)
        with open(chunk_path, 'w') as out:
            for idx, line in enumerate(processed_lines):
                if idx % n == i:
                    out.write(line + '\n')
    return chunks

# Step 3: Run rsync for a chunk
def rsync_chunk(chunk_path, cfg, idx):
    log_path = os.path.join(cfg['log_dir'], f'chunk_{idx+1}.log')
    os.makedirs(cfg['log_dir'], exist_ok=True)
    ssh_e = f"ssh -i {cfg['ssh_key']} -p {cfg.get('ssh_port', 22)}"
    
    # Ensure remote_root ends with / for rsync
    remote_root = cfg['remote_root'].rstrip('/') + '/'
    
    cmd = [
        'rsync',
        *cfg['rsync_opts'],
        f"--bwlimit={cfg['bwlimit']}",
        f"--files-from={chunk_path}",
        '-e', ssh_e,
        f"{cfg['ssh_user']}@{cfg['ssh_host']}:{remote_root}", cfg['local_root']
    ]
    with open(log_path, 'w') as logf:
        proc = subprocess.run(cmd, stdout=logf, stderr=subprocess.STDOUT)
        return proc.returncode == 0

# Step 4: Main orchestration
def main():
    import sys
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    cfg = load_config(config_file)
    
    print("🚀 VPS Backup Tool - Multi-Interface Monitoring")
    print("=" * 50)
    
    # Hiển thị thông tin screen session nếu có
    session = print_session_info()
    
    print(f"📋 Config: {config_file}")
    print(f"🖥️  VPS: {cfg['ssh_user']}@{cfg['ssh_host']}:{cfg['ssh_port']}")
    print(f"📁 Source: {cfg['remote_root']}")
    print(f"💾 Destination: {cfg['local_root']}")
    print(f"🧵 Threads: {cfg['threads']}")
    
    if session:
        print(f"🖥️  Screen Session: {session}")
        print("   💡 This backup will continue running even if you disconnect SSH")
    
    print("=" * 50)
    
    # Kiểm tra xem có enable monitoring không
    enable_monitoring = cfg.get('enable_bandwidth_monitoring', True)
    monitoring_interval = cfg.get('monitoring_interval', 10)
    
    # Khởi tạo bandwidth monitor
    monitor = None
    if enable_monitoring:
        try:
            monitor = BandwidthMonitor(cfg, monitoring_interval)
            monitor.start()
        except Exception as e:
            print(f"⚠️  Warning: Could not start bandwidth monitoring: {e}")
    
    try:
        print(f"🚀 Starting backup with {cfg['threads']} threads...")
        print(f"📂 Remote: {cfg['ssh_user']}@{cfg['ssh_host']}:{cfg['remote_root']}")
        print(f"📁 Local: {cfg['local_root']}")
        print("=" * 80)
        
        all_files = build_file_list(cfg)
        chunks = chunk_file_list(all_files, cfg)

        results = {}
        with ThreadPoolExecutor(max_workers=cfg['threads']) as executor:
            futures = {executor.submit(rsync_chunk, chunks[i], cfg, i): i for i in range(len(chunks))}
            for fut in as_completed(futures):
                idx = futures[fut]
                success = fut.result()
                results[idx] = success
                status = "✅ OK" if success else "❌ FAILED"
                print(f"Chunk {idx+1}: {status}")

        # Retry failures
        failed = [i for i, ok in results.items() if not ok]
        if failed:
            print(f"\n🔄 Retrying failed chunks: {failed}")
            for i in failed:
                ok = rsync_chunk(chunks[i], cfg, i)
                status = "✅ OK" if ok else "❌ FAILED"
                print(f"Chunk {i+1} retry: {status}")

        # Summary
        success_count = sum(1 for ok in results.values() if ok)
        total_count = len(results)
        print("=" * 80)
        print(f"✅ Backup complete! {success_count}/{total_count} chunks successful")
        
        if monitor:
            print(f"📊 Current total bandwidth: ⬇️ {format_bytes(monitor.current_total_download)} | ⬆️ {format_bytes(monitor.current_total_upload)}")
            if monitor.current_interfaces:
                print(f"📡 Active interfaces: {len(monitor.current_interfaces)}")
        
        print("💡 Consider running final mirror rsync if desired.")
        
    finally:
        # Dừng monitoring khi backup xong
        if monitor:
            monitor.stop()

if __name__ == '__main__':
    main()
