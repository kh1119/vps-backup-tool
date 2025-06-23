"""
Backup runner for different backup types
"""

import sys
import signal
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.config import ConfigManager
from src.core.backup import BackupEngine
from src.utils.formatting import (
    print_logo, print_header, print_success, print_error, 
    format_duration, Colors
)

class BackupRunner:
    """Backup runner for screen sessions"""
    
    def __init__(self, backup_type: str = 'full'):
        self.backup_type = backup_type
        self.config_manager = ConfigManager()
        self.backup_engine = None
        self.interrupted = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle interruption signals"""
        print(f"\n⚠️  Received signal {signum}. Stopping backup gracefully...")
        self.interrupted = True
        
        if self.backup_engine and self.backup_engine.bandwidth_monitor:
            self.backup_engine.stop_bandwidth_monitoring()
            
    def _get_backup_config(self) -> dict:
        """Get configuration for specific backup type"""
        config = self.config_manager.config
        backup_types = config.get('backup_types', {})
        
        if self.backup_type in backup_types:
            backup_config = backup_types[self.backup_type]
            print(f"📋 Using {self.backup_type} backup configuration:")
            print(f"   Description: {backup_config.get('description', 'N/A')}")
            
            # Apply backup-specific settings
            if 'max_size' in backup_config and backup_config['max_size'] != 'unlimited':
                print(f"   Max size: {backup_config['max_size']}")
                
            if backup_config.get('enable_compression'):
                print("   Compression: Enabled")
                
            if backup_config.get('enable_incremental'):
                print("   Incremental: Enabled")
                
        return config
        
    def _print_session_info(self):
        """Print screen session information"""
        import os
        if 'STY' in os.environ:
            session_info = os.environ['STY']
            print(f"🖥️  Running in screen session: {session_info}")
            print("   Detach: Ctrl+A, then D")
            print(f"   Reattach: screen -r {session_info}")
            print("=" * 80)
            
    def run(self):
        """Run the backup"""
        try:
            print_logo()
            print_header(f"{self.backup_type.upper()} BACKUP")
            
            # Show session info if running in screen
            self._print_session_info()
            
            # Load configuration
            config = self._get_backup_config()
            
            # Initialize backup engine
            self.backup_engine = BackupEngine(config)
            
            print(f"🚀 Starting {self.backup_type} backup...")
            print(f"📂 Remote: {config['ssh_user']}@{config['ssh_host']}:{config['remote_root']}")
            print(f"📁 Local: {config['local_root']}")
            print(f"🧵 Threads: {config.get('threads', 4)}")
            print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Log to file for debugging
            log_file = Path(config.get('log_dir', 'logs')) / f"{self.backup_type}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(log_file, 'w') as f:
                f.write(f"Backup started at: {datetime.now()}\n")
                f.write(f"Backup type: {self.backup_type}\n")
                f.write(f"Remote: {config['ssh_user']}@{config['ssh_host']}:{config['remote_root']}\n")
                f.write(f"Local: {config['local_root']}\n")
                f.write(f"Threads: {config.get('threads', 4)}\n")
                f.flush()
                
            print(f"📝 Logging to: {log_file}")
            print("=" * 80)
            
            # Check if interrupted before starting
            if self.interrupted:
                print("⚠️  Backup was interrupted before starting")
                return False
            
            # Run backup with enhanced error handling
            result = self.backup_engine.run_backup(
                backup_type=self.backup_type,
                use_monitoring=True,
                log_file=str(log_file)
            )
            
            # Print results
            print("\n" + "=" * 80)
            print("📊 BACKUP RESULTS")
            print("=" * 80)
            
            if result['success']:
                print_success("Backup completed successfully!")
            else:
                print_error(f"Backup completed with errors!")
                
            print(f"📈 Statistics:")
            print(f"   Total chunks: {result['total_chunks']}")
            print(f"   Successful: {result['successful_chunks']}")
            print(f"   Failed: {result['failed_chunks']}")
            print(f"   Duration: {format_duration(result['duration'])}")
            print(f"   Started: {result['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Finished: {result['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Log final results
            with open(log_file, 'a') as f:
                f.write(f"\nBackup finished at: {datetime.now()}\n")
                f.write(f"Success: {result['success']}\n")
                f.write(f"Total chunks: {result['total_chunks']}\n")
                f.write(f"Successful: {result['successful_chunks']}\n")
                f.write(f"Failed: {result['failed_chunks']}\n")
                f.write(f"Duration: {result['duration']}\n")
            
            # Show failed chunks if any
            if result['failed_chunks'] > 0:
                print(f"\n❌ Failed chunks:")
                for idx, chunk_result in result['chunk_logs'].items():
                    if not chunk_result['success']:
                        print(f"   Chunk {idx+1}: {chunk_result['log']}")
                        
            print("\n💡 Tips:")
            print("   - Check log files for detailed information")
            print(f"   - Main log: {log_file}")
            print("   - Run a final mirror rsync if needed")
            print("   - Consider running failed chunks manually")
            
            # Keep screen session alive for review
            import os
            if 'STY' in os.environ:
                print(f"\n🖥️  Screen session will remain active for review")
                print("   Detach with: Ctrl+A then D")
                print("   Or exit with: exit")
            
            return result['success']
            
        except KeyboardInterrupt:
            print("\n⚠️  Backup interrupted by user")
            return False
        except Exception as e:
            print_error(f"Backup failed: {e}")
            return False
        finally:
            if self.backup_engine and self.backup_engine.bandwidth_monitor:
                self.backup_engine.stop_bandwidth_monitoring()

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python backup_runner.py <backup_type>")
        print("Backup types: quick, full, longterm")
        sys.exit(1)
        
    backup_type = sys.argv[1]
    
    if backup_type not in ['quick', 'full', 'longterm']:
        print(f"Invalid backup type: {backup_type}")
        print("Valid types: quick, full, longterm")
        sys.exit(1)
        
    runner = BackupRunner(backup_type)
    success = runner.run()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
