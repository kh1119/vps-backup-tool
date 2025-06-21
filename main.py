# backup.py
import os
import yaml
import subprocess
import time
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

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
            
            # Skip loopback and docker interfaces
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
    """Format bytes thành đơn vị dễ đọc"""
    for unit in ['B/s', 'KB/s', 'MB/s', 'GB/s']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} TB/s"

def get_bandwidth_usage(cfg):
    """Lấy thông tin sử dụng băng thông hiện tại"""
    stats1 = get_network_stats(cfg)
    if not stats1:
        return None
    
    time.sleep(1)
    
    stats2 = get_network_stats(cfg)
    if not stats2:
        return None
    
    # Tìm interface chính
    main_interface = None
    for interface in stats1:
        if interface in stats2 and interface.startswith(('eth', 'ens', 'enp')):
            main_interface = interface
            break
    
    if not main_interface and stats1:
        for interface in stats1:
            if interface in stats2:
                main_interface = interface
                break
    
    if main_interface and main_interface in stats2:
        rx_diff = stats2[main_interface]['rx_bytes'] - stats1[main_interface]['rx_bytes']
        tx_diff = stats2[main_interface]['tx_bytes'] - stats1[main_interface]['tx_bytes']
        
        return {
            'interface': main_interface,
            'download_bps': rx_diff,
            'upload_bps': tx_diff,
            'total_rx_gb': stats2[main_interface]['rx_bytes'] / 1024 / 1024 / 1024,
            'total_tx_gb': stats2[main_interface]['tx_bytes'] / 1024 / 1024 / 1024
        }
    
    return None

class BandwidthMonitor:
    """Thread để monitor băng thông trong background"""
    def __init__(self, cfg, interval=10):
        self.cfg = cfg
        self.interval = interval
        self.running = False
        self.thread = None
        self.max_download = 0
        self.max_upload = 0
        self.current_download = 0
        self.current_upload = 0
    
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
        print(f"\n📊 Max bandwidth observed: ⬇️ {format_bytes(self.max_download)} | ⬆️ {format_bytes(self.max_upload)}")
    
    def _monitor_loop(self):
        """Loop chính của monitoring"""
        while self.running:
            try:
                bandwidth = get_bandwidth_usage(self.cfg)
                if bandwidth:
                    self.current_download = bandwidth['download_bps']
                    self.current_upload = bandwidth['upload_bps']
                    
                    self.max_download = max(self.max_download, self.current_download)
                    self.max_upload = max(self.max_upload, self.current_upload)
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    download_str = format_bytes(self.current_download)
                    upload_str = format_bytes(self.current_upload)
                    
                    print(f"[{timestamp}] 📡 {bandwidth['interface']}: ⬇️ {download_str} | ⬆️ {upload_str}")
                
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
    n = cfg['threads']
    for i in range(n):
        chunk_path = os.path.join(cfg['tmp_dir'], f'chunk_{i+1}.txt')
        chunks.append(chunk_path)
        with open(chunk_path, 'w') as out:
            for idx, line in enumerate(lines):
                if idx % n == i:
                    out.write(line + '\n')
    return chunks

# Step 3: Run rsync for a chunk
def rsync_chunk(chunk_path, cfg, idx):
    log_path = os.path.join(cfg['log_dir'], f'chunk_{idx+1}.log')
    os.makedirs(cfg['log_dir'], exist_ok=True)
    ssh_e = f"ssh -i {cfg['ssh_key']} -p {cfg.get('ssh_port', 22)}"
    cmd = [
        'rsync',
        *cfg['rsync_opts'],
        f"--bwlimit={cfg['bwlimit']}",
        f"--files-from={chunk_path}",
        '-e', ssh_e,
        f"{cfg['ssh_user']}@{cfg['ssh_host']}:/", cfg['local_root']
    ]
    with open(log_path, 'w') as logf:
        proc = subprocess.run(cmd, stdout=logf, stderr=subprocess.STDOUT)
        return proc.returncode == 0

# Step 4: Main orchestration
def main():
    import sys
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    cfg = load_config(config_file)
    
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
            print(f"📊 Current bandwidth: ⬇️ {format_bytes(monitor.current_download)} | ⬆️ {format_bytes(monitor.current_upload)}")
        
        print("💡 Consider running final mirror rsync if desired.")
        
    finally:
        # Dừng monitoring khi backup xong
        if monitor:
            monitor.stop()

if __name__ == '__main__':
    main()
