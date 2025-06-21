"""
Backup engine core functionality
"""

import os
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from .ssh import SSHManager, NetworkInterfaceMonitor

class BackupEngine:
    """Core backup engine với rsync và monitoring"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ssh_manager = SSHManager(config)
        self.network_monitor = NetworkInterfaceMonitor(self.ssh_manager)
        self.bandwidth_monitor = None
        self._setup_directories()
        
    def _setup_directories(self):
        """Tạo các thư mục cần thiết"""
        directories = [
            self.config['local_root'],
            self.config.get('tmp_dir', 'tmp'),
            self.config.get('log_dir', 'logs')
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            
    def build_file_list(self) -> str:
        """Build full file list from remote server"""
        tmp_all = Path(self.config.get('tmp_dir', 'tmp')) / 'all_files.txt'
        
        # SSH command to find files
        find_cmd = f'find "{self.config["remote_root"]}" -type f'
        success, stdout, stderr = self.ssh_manager.run_command(find_cmd)
        
        if not success:
            raise RuntimeError(f"Failed to build file list: {stderr}")
            
        # Write file list to temp file
        with open(tmp_all, 'w') as f:
            f.write(stdout)
            
        return str(tmp_all)
        
    def chunk_file_list(self, all_files: str) -> List[str]:
        """Chunk file list into N parts for parallel processing"""
        with open(all_files) as f:
            lines = [line.strip() for line in f if line.strip()]
            
        # Remove remote_root prefix from paths
        remote_root = self.config['remote_root'].rstrip('/')
        processed_lines = []
        
        for line in lines:
            if line.startswith(remote_root):
                relative_path = line[len(remote_root):].lstrip('/')
                if relative_path:
                    processed_lines.append(relative_path)
            else:
                processed_lines.append(line)
                
        # Create chunks
        n_threads = self.config.get('threads', 4)
        chunks = []
        tmp_dir = Path(self.config.get('tmp_dir', 'tmp'))
        
        for i in range(n_threads):
            chunk_path = tmp_dir / f'chunk_{i+1}.txt'
            chunks.append(str(chunk_path))
            
            with open(chunk_path, 'w') as f:
                for idx, line in enumerate(processed_lines):
                    if idx % n_threads == i:
                        f.write(line + '\n')
                        
        return chunks
        
    def rsync_chunk(self, chunk_path: str, chunk_idx: int) -> Tuple[bool, str]:
        """Execute rsync for a specific chunk"""
        log_path = Path(self.config.get('log_dir', 'logs')) / f'chunk_{chunk_idx+1}.log'
        
        # Build rsync command
        ssh_cmd = f"ssh -i {Path(self.config['ssh_key']).expanduser()} -p {self.config.get('ssh_port', 22)}"
        remote_root = self.config['remote_root'].rstrip('/') + '/'
        
        rsync_cmd = [
            'rsync',
            f"--files-from={chunk_path}",
            '-e', ssh_cmd,
            f"--bwlimit={self.config.get('bwlimit', 0)}"
        ]
        
        # Add rsync options
        rsync_opts = self.config.get('rsync_opts', ['--archive', '--compress'])
        rsync_cmd.extend(rsync_opts)
        
        # Add source and destination
        rsync_cmd.extend([
            f"{self.config['ssh_user']}@{self.config['ssh_host']}:{remote_root}",
            self.config['local_root']
        ])
        
        try:
            with open(log_path, 'w') as log_file:
                result = subprocess.run(
                    rsync_cmd,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    timeout=self.config.get('rsync_timeout', 3600)
                )
                
            return result.returncode == 0, str(log_path)
            
        except subprocess.TimeoutExpired:
            return False, f"Timeout: {log_path}"
        except Exception as e:
            return False, f"Error: {e}"
            
    def run_backup(self, backup_type: str = 'full', use_monitoring: bool = True) -> Dict[str, Any]:
        """Run the main backup process"""
        start_time = datetime.now()
        
        print(f"🚀 Starting {backup_type} backup...")
        print(f"📂 Remote: {self.config['ssh_user']}@{self.config['ssh_host']}:{self.config['remote_root']}")
        print(f"📁 Local: {self.config['local_root']}")
        print(f"🧵 Threads: {self.config.get('threads', 4)}")
        print("=" * 80)
        
        # Start bandwidth monitoring
        if use_monitoring and self.config.get('enable_bandwidth_monitoring', True):
            self.start_bandwidth_monitoring()
            
        try:
            # Build file list
            print("📋 Building file list from remote server...")
            all_files = self.build_file_list()
            
            # Chunk files
            print("🔀 Creating file chunks for parallel processing...")
            chunks = self.chunk_file_list(all_files)
            
            # Execute rsync in parallel
            print(f"🔄 Starting rsync with {len(chunks)} chunks...")
            results = {}
            
            with ThreadPoolExecutor(max_workers=len(chunks)) as executor:
                futures = {
                    executor.submit(self.rsync_chunk, chunks[i], i): i 
                    for i in range(len(chunks))
                }
                
                for future in as_completed(futures):
                    chunk_idx = futures[future]
                    success, log_info = future.result()
                    results[chunk_idx] = {
                        'success': success,
                        'log': log_info
                    }
                    
                    status = "✅ OK" if success else "❌ FAILED"
                    print(f"Chunk {chunk_idx+1}: {status}")
                    
            # Retry failed chunks
            failed_chunks = [idx for idx, result in results.items() if not result['success']]
            
            if failed_chunks:
                print(f"\n🔄 Retrying {len(failed_chunks)} failed chunks...")
                for idx in failed_chunks:
                    success, log_info = self.rsync_chunk(chunks[idx], idx)
                    results[idx] = {
                        'success': success,
                        'log': log_info
                    }
                    
                    status = "✅ OK" if success else "❌ FAILED"
                    print(f"Chunk {idx+1} retry: {status}")
                    
            # Calculate results
            success_count = sum(1 for result in results.values() if result['success'])
            total_count = len(results)
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            backup_result = {
                'success': success_count == total_count,
                'total_chunks': total_count,
                'successful_chunks': success_count,
                'failed_chunks': total_count - success_count,
                'start_time': start_time,
                'end_time': end_time,
                'duration': duration,
                'backup_type': backup_type,
                'chunk_logs': results
            }
            
            # Print summary
            print("=" * 80)
            if backup_result['success']:
                print(f"✅ Backup completed successfully!")
            else:
                print(f"⚠️  Backup completed with errors!")
                
            print(f"📊 Results: {success_count}/{total_count} chunks successful")
            print(f"⏱️  Duration: {duration}")
            
            if self.bandwidth_monitor:
                print(f"📡 Max bandwidth observed: "
                     f"⬇️ {self._format_bytes(self.bandwidth_monitor.max_download)} | "
                     f"⬆️ {self._format_bytes(self.bandwidth_monitor.max_upload)}")
                     
            return backup_result
            
        finally:
            if self.bandwidth_monitor:
                self.stop_bandwidth_monitoring()
                
    def start_bandwidth_monitoring(self, interval: int = None):
        """Start bandwidth monitoring in background"""
        if interval is None:
            interval = self.config.get('monitoring_interval', 10)
            
        self.bandwidth_monitor = BandwidthMonitor(
            self.network_monitor, 
            interval=interval
        )
        self.bandwidth_monitor.start()
        
    def stop_bandwidth_monitoring(self):
        """Stop bandwidth monitoring"""
        if self.bandwidth_monitor:
            self.bandwidth_monitor.stop()
            self.bandwidth_monitor = None
            
    def _format_bytes(self, bytes_val: float) -> str:
        """Format bytes to human readable format"""
        for unit in ['B/s', 'KB/s', 'MB/s', 'GB/s']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f} TB/s"

class BandwidthMonitor:
    """Background bandwidth monitoring thread"""
    
    def __init__(self, network_monitor: NetworkInterfaceMonitor, interval: int = 10):
        self.network_monitor = network_monitor
        self.interval = interval
        self.running = False
        self.thread = None
        self.max_download = 0
        self.max_upload = 0
        self.current_download = 0
        self.current_upload = 0
        
    def start(self):
        """Start monitoring thread"""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print(f"🔍 Bandwidth monitoring started (interval: {self.interval}s)")
        
    def stop(self):
        """Stop monitoring thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print(f"\n📊 Max bandwidth observed: "
             f"⬇️ {self._format_bytes(self.max_download)} | "
             f"⬆️ {self._format_bytes(self.max_upload)}")
             
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                bandwidth = self.network_monitor.get_bandwidth_usage()
                
                if bandwidth:
                    self.current_download = bandwidth['total_download_bps']
                    self.current_upload = bandwidth['total_upload_bps']
                    
                    self.max_download = max(self.max_download, self.current_download)
                    self.max_upload = max(self.max_upload, self.current_upload)
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    # Display current bandwidth
                    download_str = self._format_bytes(self.current_download)
                    upload_str = self._format_bytes(self.current_upload)
                    interface_info = f"({bandwidth['active_count']}/{bandwidth['interface_count']} active)"
                    
                    print(f"[{timestamp}] 📊 Total: ⬇️ {download_str} | ⬆️ {upload_str} {interface_info}")
                    
                    # Show active interfaces
                    if bandwidth['active_interfaces']:
                        if len(bandwidth['active_interfaces']) > 1:
                            print("         Active interfaces:")
                            for iface, data in sorted(
                                bandwidth['active_interfaces'].items(),
                                key=lambda x: x[1]['download_bps'] + x[1]['upload_bps'],
                                reverse=True
                            )[:3]:  # Top 3
                                down = self._format_bytes(data['download_bps'])
                                up = self._format_bytes(data['upload_bps'])
                                print(f"           {iface}: ⬇️ {down} | ⬆️ {up}")
                        elif bandwidth['main_interface']:
                            print(f"         Main interface: {bandwidth['main_interface']}")
                            
                    # High traffic warnings
                    if self.current_download > 100 * 1024 * 1024:  # > 100MB/s
                        print("         ⚠️  HIGH DOWNLOAD TRAFFIC!")
                    if self.current_upload > 50 * 1024 * 1024:  # > 50MB/s
                        print("         ⚠️  HIGH UPLOAD TRAFFIC!")
                        
                time.sleep(self.interval)
                
            except Exception as e:
                if self.running:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Monitoring error: {e}")
                time.sleep(self.interval)
                
    def _format_bytes(self, bytes_val: float) -> str:
        """Format bytes to human readable format"""
        for unit in ['B/s', 'KB/s', 'MB/s', 'GB/s']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f} TB/s"
