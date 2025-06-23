"""
Main application menu and UI
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import ConfigManager
from core.ssh import SSHManager, NetworkInterfaceMonitor
from core.backup import BackupEngine
from utils.screen import ScreenManager
from utils.formatting import (
    print_logo, print_header, print_section, print_table,
    print_success, print_error, print_warning, print_info,
    format_bytes, format_duration, colored_status, confirm_action,
    Colors
)

class BackupApplication:
    """Main backup application with menu interface"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config = None
        self.ssh_manager = None
        self.backup_engine = None
        self.screen_manager = ScreenManager()
        
    def initialize(self) -> bool:
        """Initialize application components"""
        try:
            # Load configuration
            if not self.config_manager.config_exists():
                print_error("Configuration file not found!")
                print_info("Please run the application launcher first to set up configuration.")
                return False
                
            self.config = self.config_manager.load_config()
            
            # Initialize components
            self.ssh_manager = SSHManager(self.config)
            self.backup_engine = BackupEngine(self.config)
            
            return True
            
        except Exception as e:
            print_error(f"Failed to initialize application: {e}")
            return False
            
    def show_main_menu(self):
        """Display main menu"""
        print_logo()
        print_header("MAIN MENU")
        
        print("\n📦 BACKUP OPTIONS:")
        print("  1) 🚀 Quick Backup (với screen session)")
        print("  2) 💾 Full Backup (production)")
        print("  3) 🕐 Long-term Backup (multi-day)")
        print("  4) 📊 Bandwidth Monitoring Only")
        
        print("\n🖥️  SESSION MANAGEMENT:")
        print("  5) 📋 List Active Sessions")
        print("  6) 🔗 Attach to Session")
        print("  7) ⏹️  Stop Session")
        print("  8) 🧹 Cleanup Dead Sessions")
        
        print("\n🔧 SETUP & TESTING:")
        print("  9) ⚙️  Show Configuration")
        print(" 10) 🔍 Test SSH Connection")
        print(" 11) 📡 Test Network Interfaces")
        print(" 12) 🖥️  System Information")
        print(" 13) 📋 View Backup Logs")
        print(" 14) 🔍 Debug Backup Status")
        
        print("\n 0) 🚪 Exit")
        print("\n" + "=" * 80)
        
    def handle_menu_choice(self, choice: str) -> bool:
        """Handle menu choice, return False to exit"""
        try:
            if choice == '1':
                self.quick_backup()
            elif choice == '2':
                self.full_backup()
            elif choice == '3':
                self.longterm_backup()
            elif choice == '4':
                self.bandwidth_monitoring_only()
            elif choice == '5':
                self.list_sessions()
            elif choice == '6':
                self.attach_session()
            elif choice == '7':
                self.stop_session()
            elif choice == '8':
                self.cleanup_sessions()
            elif choice == '9':
                self.show_configuration()
            elif choice == '10':
                self.test_ssh_connection()
            elif choice == '11':
                self.test_network_interfaces()
            elif choice == '12':
                self.show_system_info()
            elif choice == '13':
                self.view_backup_logs()
            elif choice == '14':
                self.debug_backup_status()
            elif choice in ['q', 'Q', '0']:
                return False
            else:
                print_warning("Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Operation cancelled by user")
        except Exception as e:
            print_error(f"An error occurred: {e}")
            
        return True
        
    def quick_backup(self):
        """Run quick backup with screen session"""
        print_section("QUICK BACKUP")
        
        if not confirm_action("Start quick backup in screen session?", True):
            return
            
        session_name = self.screen_manager.get_available_session_name("quick")
        
        # Create screen session
        command = f"cd {Path(__file__).parent.parent.parent} && python -m src.core.backup_runner quick"
        success, message = self.screen_manager.create_session(session_name, command)
        
        if success:
            print_success(f"Quick backup started in screen session: {session_name}")
            print_info("Use 'List Active Sessions' to monitor progress")
            print_info(f"Attach with: screen -r {session_name}")
        else:
            print_error(f"Failed to start backup: {message}")
            
    def full_backup(self):
        """Run full backup"""
        print_section("FULL BACKUP")
        
        use_screen = confirm_action("Run in screen session? (recommended for long backups)", True)
        
        if use_screen:
            session_name = self.screen_manager.get_available_session_name("full")
            command = f"cd {Path(__file__).parent.parent.parent} && python -m src.core.backup_runner full"
            success, message = self.screen_manager.create_session(session_name, command)
            
            if success:
                print_success(f"Full backup started in screen session: {session_name}")
                print_info(f"Attach with: screen -r {session_name}")
            else:
                print_error(f"Failed to start backup: {message}")
        else:
            # Run backup directly
            print_info("Starting full backup...")
            result = self.backup_engine.run_backup('full')
            
            if result['success']:
                print_success(f"Backup completed successfully in {format_duration(result['duration'])}")
            else:
                print_error(f"Backup completed with errors: {result['failed_chunks']} chunks failed")
                
    def longterm_backup(self):
        """Run long-term backup"""
        print_section("LONG-TERM BACKUP")
        
        print_warning("Long-term backup may take hours or days to complete!")
        if not confirm_action("Continue with long-term backup?"):
            return
            
        session_name = self.screen_manager.get_available_session_name("longterm")
        command = f"cd {Path(__file__).parent.parent.parent} && python -m src.core.backup_runner longterm"
        success, message = self.screen_manager.create_session(session_name, command)
        
        if success:
            print_success(f"Long-term backup started in screen session: {session_name}")
            print_info("This backup will continue running even if you disconnect")
            print_info(f"Monitor with: screen -r {session_name}")
        else:
            print_error(f"Failed to start backup: {message}")
            
    def bandwidth_monitoring_only(self):
        """Run bandwidth monitoring only"""
        print_section("BANDWIDTH MONITORING")
        
        try:
            print_info("Starting bandwidth monitoring... Press Ctrl+C to stop")
            self.backup_engine.start_bandwidth_monitoring()
            
            # Keep running until interrupted
            import time
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\nStopping bandwidth monitoring...")
            self.backup_engine.stop_bandwidth_monitoring()
            
    def list_sessions(self):
        """List all screen sessions"""
        print_section("ACTIVE SCREEN SESSIONS")
        
        sessions = self.screen_manager.list_sessions()
        backup_sessions = self.screen_manager.get_backup_sessions()
        
        if not sessions:
            print_info("No active screen sessions found")
            return
            
        # Show all sessions
        headers = ["PID", "Name", "Status", "Type"]
        rows = []
        
        for session in sessions:
            session_type = "Backup" if session['is_backup_session'] else "Other"
            rows.append([
                session['pid'],
                session['name'],
                session['status'].title(),
                session_type
            ])
            
        print_table(headers, rows)
        
        if backup_sessions:
            print(f"\n📊 Found {len(backup_sessions)} backup sessions")
        else:
            print("\nℹ️  No backup sessions currently running")
            
    def attach_session(self):
        """Attach to a screen session"""
        print_section("ATTACH TO SESSION")
        
        sessions = self.screen_manager.list_sessions()
        if not sessions:
            print_info("No screen sessions available to attach")
            return
            
        # Show available sessions
        print("Available sessions:")
        for i, session in enumerate(sessions, 1):
            status_color = Colors.GREEN if session['status'] == 'detached' else Colors.YELLOW
            status_text = Colors.colored(session['status'].title(), status_color)
            print(f"  {i}) {session['name']} ({session['pid']}) - {status_text}")
            
        try:
            choice = input("\nEnter session number (or name): ").strip()
            
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(sessions):
                    session_name = sessions[idx]['name']
                else:
                    print_error("Invalid session number")
                    return
            else:
                session_name = choice
                
            print_info(f"Attaching to session: {session_name}")
            print_info("Use Ctrl+A then D to detach from session")
            
            success, message = self.screen_manager.attach_session(session_name)
            if success:
                print_success(message)
            else:
                print_error(message)
                
        except ValueError:
            print_error("Invalid input")
            
    def stop_session(self):
        """Stop a screen session"""
        print_section("STOP SESSION")
        
        sessions = self.screen_manager.get_backup_sessions()
        if not sessions:
            print_info("No backup sessions to stop")
            return
            
        print("Backup sessions:")
        for i, session in enumerate(sessions, 1):
            print(f"  {i}) {session['name']} ({session['pid']}) - {session['status'].title()}")
            
        try:
            choice = input("\nEnter session number to stop: ")
            if choice.isdigit():
                session_idx = int(choice) - 1
                if 0 <= session_idx < len(sessions):
                    session_name = sessions[session_idx]['name']
                    if self.screen_manager.stop_session(session_name):
                        print_success(f"Session '{session_name}' stopped successfully")
                    else:
                        print_error(f"Failed to stop session '{session_name}'")
                else:
                    print_error("Invalid session number")
            else:
                print_error("Please enter a valid number")
        except KeyboardInterrupt:
            print_info("\nOperation cancelled")
        except Exception as e:
            print_error(f"Error stopping session: {e}")
            
        input("\nPress Enter to continue...")
        
    def view_backup_logs(self):
        """Xem log backup local trên VPS này"""
        print_section("BACKUP LOGS")
        
        log_dir = Path(self.config.get('log_dir', 'logs'))
        
        if not log_dir.exists():
            print_error("Log directory not found!")
            return
            
        # List all log files
        log_files = list(log_dir.glob("*.log"))
        
        if not log_files:
            print_info("No log files found")
            return
            
        # Sort by modification time (newest first)
        log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        print("📋 Available log files:")
        headers = ["#", "File", "Size", "Modified"]
        rows = []
        
        for i, log_file in enumerate(log_files, 1):
            stat = log_file.stat()
            size = format_bytes(stat.st_size)
            modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            rows.append([str(i), log_file.name, size, modified])
            
        print_table(headers, rows)
        
        try:
            choice = input("\nEnter log file number to view (or 'latest' for most recent): ").strip()
            
            if choice.lower() == 'latest':
                selected_file = log_files[0]
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(log_files):
                    selected_file = log_files[idx]
                else:
                    print_error("Invalid file number")
                    return
            else:
                print_error("Invalid choice")
                return
                
            print_section(f"LOG: {selected_file.name}")
            
            # Show last 50 lines
            try:
                with open(selected_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                if len(lines) > 50:
                    print_info(f"Showing last 50 lines of {len(lines)} total lines")
                    print_info("Use 'tail -f' command to follow log in real-time")
                    print("-" * 80)
                    for line in lines[-50:]:
                        print(line.rstrip())
                else:
                    print_info(f"Showing all {len(lines)} lines")
                    print("-" * 80)
                    for line in lines:
                        print(line.rstrip())
                        
            except Exception as e:
                print_error(f"Error reading log file: {e}")
                
        except KeyboardInterrupt:
            print_info("\nOperation cancelled")
        except Exception as e:
            print_error(f"Error: {e}")
            
    def debug_backup_status(self):
        """Debug trạng thái backup trên VPS này"""
        print_section("BACKUP STATUS DEBUG")
        
        # System info
        print("🖥️  System Information:")
        import platform, os
        try:
            import psutil
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('.')
        except ImportError:
            print_warning("psutil not installed, limited system info available")
            cpu_usage = memory = disk = None
            
        print(f"  Hostname: {platform.node()}")
        print(f"  OS: {platform.system()} {platform.release()}")
        print(f"  Python: {platform.python_version()}")
        
        if cpu_usage is not None:
            print(f"  CPU Usage: {cpu_usage:.1f}%")
            print(f"  Memory: {memory.percent:.1f}% used")
            print(f"  Disk: {disk.percent:.1f}% used")
        else:
            # Fallback to basic commands
            try:
                import subprocess
                uptime_result = subprocess.run(['uptime'], capture_output=True, text=True)
                if uptime_result.returncode == 0:
                    print(f"  Uptime: {uptime_result.stdout.strip()}")
            except:
                pass
        
        # Screen sessions
        print("\n📺 Screen Sessions:")
        sessions = self.screen_manager.list_sessions()
        if sessions:
            for session in sessions:
                status_color = Colors.GREEN if session['status'] == 'detached' else Colors.YELLOW
                status_text = Colors.colored(session['status'].title(), status_color)
                session_type = "Backup" if session['is_backup_session'] else "Other"
                print(f"  - {session['name']} ({session['pid']}) - {status_text} [{session_type}]")
        else:
            print("  No screen sessions found")
            
        # Running processes
        print("\n🔄 Backup Related Processes:")
        backup_processes = []
        try:
            if 'psutil' in globals():
                for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
                    try:
                        cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else proc.info['name']
                        if any(keyword in cmdline.lower() for keyword in ['backup', 'rsync', 'python.*backup']):
                            backup_processes.append(proc.info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            else:
                # Fallback to ps command
                import subprocess
                ps_result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                if ps_result.returncode == 0:
                    for line in ps_result.stdout.split('\n'):
                        if any(keyword in line.lower() for keyword in ['backup', 'rsync']):
                            if 'grep' not in line.lower():
                                backup_processes.append({'cmdline': line.strip()})
        except Exception as e:
            print_error(f"Error getting process info: {e}")
                
        if backup_processes:
            for proc in backup_processes:
                if 'cmdline' in proc and isinstance(proc['cmdline'], str):
                    print(f"  {proc['cmdline'][:80]}...")
                else:
                    cmdline = ' '.join(proc['cmdline']) if proc['cmdline'] else proc['name']
                    print(f"  PID {proc['pid']}: {cmdline[:80]}...")
                    if 'cpu_percent' in proc:
                        print(f"    CPU: {proc['cpu_percent']:.1f}%, Memory: {proc['memory_percent']:.1f}%")
        else:
            print("  No backup processes running")
            
        # Directory status
        print("\n📂 Directory Status:")
        directories = [
            ("logs", self.config.get('log_dir', 'logs')),
            ("tmp", self.config.get('tmp_dir', 'tmp')),
            ("backup_data", self.config.get('local_root', 'backup_data')),
            ("configs", "configs")
        ]
        
        for name, path in directories:
            path_obj = Path(path)
            if path_obj.exists():
                if path_obj.is_dir():
                    file_count = len(list(path_obj.iterdir()))
                    try:
                        size = sum(f.stat().st_size for f in path_obj.rglob('*') if f.is_file())
                        size_str = format_bytes(size)
                    except:
                        size_str = "Unknown"
                    print(f"  ✅ {name}: {file_count} items, {size_str}")
                else:
                    print(f"  ⚠️  {name}: exists but not a directory")
            else:
                print(f"  ❌ {name}: not found")
                
        # Recent log files
        print("\n📋 Recent Log Activity:")
        log_dir = Path(self.config.get('log_dir', 'logs'))
        if log_dir.exists():
            recent_logs = sorted(log_dir.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]
            if recent_logs:
                for log_file in recent_logs:
                    stat = log_file.stat()
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    size = format_bytes(stat.st_size)
                    print(f"  - {log_file.name}: {size}, modified {modified}")
            else:
                print("  No log files found")
        else:
            print("  Log directory not found")
            
        # Chunk status
        print("\n📦 Chunk Status:")
        tmp_dir = Path(self.config.get('tmp_dir', 'tmp'))
        if tmp_dir.exists():
            chunk_files = list(tmp_dir.glob("chunk_*.txt"))
            if chunk_files:
                print(f"  Found {len(chunk_files)} chunk files")
                chunk_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                for chunk_file in chunk_files[:3]:  # Show latest 3
                    stat = chunk_file.stat()
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    size = format_bytes(stat.st_size)
                    print(f"    - {chunk_file.name}: {size}, modified {modified}")
            else:
                print("  No chunk files found")
        else:
            print("  Temp directory not found")
            
        # SSH connection test
        print("\n🔗 SSH Connection Test:")
        try:
            success, message = self.ssh_manager.test_connection()
            if success:
                print_success(f"  {message}")
            else:
                print_error(f"  {message}")
        except Exception as e:
            print_error(f"  Connection test failed: {e}")
            
        print("\n" + "=" * 80)
        
    def run(self):
        """Main application loop"""
        if not self.initialize():
            print_error("Failed to initialize application")
            return
            
        try:
            while True:
                self.show_main_menu()
                
                try:
                    choice = input("Enter your choice: ").strip()
                    print()  # Add spacing
                    
                    if not self.handle_menu_choice(choice):
                        break
                        
                except KeyboardInterrupt:
                    print("\n\n👋 Goodbye!")
                    break
                    
                # Wait for user input before showing menu again
                if choice != '0':
                    input("\nPress Enter to continue...")
                    print("\n" * 2)  # Clear screen a bit
                    
        except Exception as e:
            print_error(f"Application error: {e}")
            
        print("\n👋 Thank you for using VPS Backup Tool!")

def main():
    """Entry point for the application"""
    app = BackupApplication()
    app.run()

if __name__ == '__main__':
    main()

