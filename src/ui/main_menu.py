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
            elif choice == '0':
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
            choice = input("\nEnter session number to stop: ").strip()
            
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(sessions):
                    session = sessions[idx]
                    
                    if confirm_action(f"Stop session '{session['name']}'?"):
                        success, message = self.screen_manager.kill_session(session['name'])
                        if success:
                            print_success(message)
                        else:
                            print_error(message)
                else:
                    print_error("Invalid session number")
            else:
                print_error("Please enter a valid number")
                
        except ValueError:
            print_error("Invalid input")
            
    def cleanup_sessions(self):
        """Cleanup dead screen sessions"""
        print_section("CLEANUP DEAD SESSIONS")
        
        if confirm_action("Clean up all dead screen sessions?"):
            count, cleaned = self.screen_manager.cleanup_dead_sessions()
            
            if count > 0:
                print_success(f"Cleaned up {count} dead sessions:")
                for session in cleaned:
                    print(f"  - {session}")
            else:
                print_info("No dead sessions found to clean up")
                
    def show_configuration(self):
        """Show current configuration"""
        print_section("CONFIGURATION")
        
        # Connection info
        print("🔗 Connection:")
        print(f"  Host: {self.config['ssh_user']}@{self.config['ssh_host']}:{self.config['ssh_port']}")
        print(f"  SSH Key: {self.config['ssh_key']}")
        
        # Paths
        print("\n📂 Paths:")
        print(f"  Remote: {self.config['remote_root']}")
        print(f"  Local: {self.config['local_root']}")
        print(f"  Temp: {self.config.get('tmp_dir', 'tmp')}")
        print(f"  Logs: {self.config.get('log_dir', 'logs')}")
        
        # Performance
        print("\n⚡ Performance:")
        print(f"  Threads: {self.config.get('threads', 4)}")
        print(f"  Bandwidth Limit: {self.config.get('bwlimit', 0)} KB/s")
        print(f"  Monitoring Interval: {self.config.get('monitoring_interval', 10)}s")
        
        # Rsync options
        print("\n🔧 Rsync Options:")
        for opt in self.config.get('rsync_opts', []):
            print(f"  {opt}")
            
    def test_ssh_connection(self):
        """Test SSH connection"""
        print_section("SSH CONNECTION TEST")
        
        print_info("Testing SSH connection...")
        success, message = self.ssh_manager.test_connection()
        
        if success:
            print_success(message)
            
            # Get remote info
            print_info("Getting remote system information...")
            info = self.ssh_manager.get_remote_info()
            
            print("\n🖥️  Remote System Info:")
            for key, value in info.items():
                print(f"  {key.title()}: {value}")
                
        else:
            print_error(message)
            
    def test_network_interfaces(self):
        """Test network interfaces"""
        print_section("NETWORK INTERFACE TEST")
        
        monitor = NetworkInterfaceMonitor(self.ssh_manager)
        
        print_info("Testing network interfaces...")
        result = monitor.test_interfaces()
        
        if result['test_successful']:
            print_success("Network interface test completed successfully")
            
            print(f"\n📡 Found {result['total_interfaces']} network interfaces:")
            for interface in result['interfaces_found']:
                print(f"  - {interface}")
                
            if result['active_interfaces']:
                print(f"\n⚡ Active interfaces ({len(result['active_interfaces'])}):")
                for interface in result['active_interfaces']:
                    print(f"  - {interface}")
            else:
                print("\nℹ️  No active traffic detected during test")
                
            if 'bandwidth_data' in result:
                bandwidth = result['bandwidth_data']
                print(f"\n📊 Current bandwidth:")
                print(f"  Download: {format_bytes(bandwidth['total_download_bps'])}/s")
                print(f"  Upload: {format_bytes(bandwidth['total_upload_bps'])}/s")
                
        else:
            print_error("Network interface test failed")
            if 'error' in result:
                print_error(result['error'])
                
    def show_system_info(self):
        """Show system information"""
        print_section("SYSTEM INFORMATION")
        
        # Local system info
        import platform
        print("💻 Local System:")
        print(f"  OS: {platform.system()} {platform.release()}")
        print(f"  Python: {platform.python_version()}")
        print(f"  Architecture: {platform.machine()}")
        
        # Remote system info
        print("\n🖥️  Remote System:")
        success, message = self.ssh_manager.test_connection()
        
        if success:
            info = self.ssh_manager.get_remote_info()
            for key, value in info.items():
                if not value.startswith("Error"):
                    print(f"  {key.title()}: {value}")
        else:
            print_error(f"Cannot connect to remote system: {message}")
            
        # Configuration paths
        print("\n📂 Paths:")
        for path_name, path_value in [
            ("Config Dir", self.config_manager.config_dir),
            ("Local Root", self.config['local_root']),
            ("Temp Dir", self.config.get('tmp_dir', 'tmp')),
            ("Log Dir", self.config.get('log_dir', 'logs'))
        ]:
            path_obj = Path(path_value)
            exists = "✅" if path_obj.exists() else "❌"
            print(f"  {path_name}: {path_value} {exists}")
            
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
