"""
Screen session management utilities
"""

import subprocess
import re
from typing import List, Dict, Any, Optional, Tuple

class ScreenManager:
    """Quản lý screen sessions cho long-running backups"""
    
    def __init__(self, session_prefix: str = "backup"):
        self.session_prefix = session_prefix
        
    def list_sessions(self) -> List[Dict[str, str]]:
        """List all screen sessions"""
        try:
            result = subprocess.run(
                ['screen', '-ls'],
                capture_output=True,
                text=True
            )
            
            sessions = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                # Parse screen -ls output
                # Example: "12345.backup_session	(Attached/Detached)"
                match = re.match(r'\s*(\d+)\.(\S+)\s+\((\w+)\)', line)
                if match:
                    pid, name, status = match.groups()
                    sessions.append({
                        'pid': pid,
                        'name': name,
                        'full_name': f"{pid}.{name}",
                        'status': status.lower(),
                        'is_backup_session': name.startswith(self.session_prefix)
                    })
                    
            return sessions
            
        except subprocess.CalledProcessError:
            return []
        except FileNotFoundError:
            raise RuntimeError("Screen command not found. Please install screen.")
            
    def get_backup_sessions(self) -> List[Dict[str, str]]:
        """Get only backup-related sessions"""
        all_sessions = self.list_sessions()
        return [s for s in all_sessions if s['is_backup_session']]
        
    def create_session(self, name: str, command: str = None) -> Tuple[bool, str]:
        """Create a new screen session with enhanced stability"""
        session_name = f"{self.session_prefix}_{name}"
        
        try:
            if command:
                # Create session and run command with better error handling
                # Use bash -l to ensure proper environment
                wrapped_command = f"bash -l -c '{command}; echo \"\\n\\n=== BACKUP COMPLETED ===\\n\"; echo \"Press Ctrl+A then D to detach, or type exit to close\"; exec bash'"
                
                result = subprocess.run([
                    'screen', '-dmS', session_name, 'bash', '-c', wrapped_command
                ], capture_output=True, text=True)
            else:
                # Create empty session
                result = subprocess.run([
                    'screen', '-dmS', session_name
                ], capture_output=True, text=True)
                
            if result.returncode == 0:
                # Verify session was created
                import time
                time.sleep(1)  # Give screen time to initialize
                
                sessions = self.list_sessions()
                session_exists = any(s['name'] == session_name for s in sessions)
                
                if session_exists:
                    return True, f"Session '{session_name}' created successfully"
                else:
                    return False, f"Session creation appeared successful but session not found"
            else:
                return False, f"Failed to create session: {result.stderr}"
                
        except Exception as e:
            return False, f"Error creating session: {str(e)}"
            
    def attach_session(self, session_name: str) -> Tuple[bool, str]:
        """Attach to an existing session"""
        try:
            # Check if session exists
            sessions = self.list_sessions()
            session_exists = any(
                s['name'] == session_name or s['full_name'] == session_name 
                for s in sessions
            )
            
            if not session_exists:
                return False, f"Session '{session_name}' not found"
                
            # Use subprocess.Popen to allow interactive session
            process = subprocess.Popen(['screen', '-r', session_name])
            process.wait()
            
            return True, f"Detached from session '{session_name}'"
            
        except Exception as e:
            return False, f"Error attaching to session: {str(e)}"
            
    def kill_session(self, session_name: str) -> Tuple[bool, str]:
        """Kill a screen session"""
        try:
            result = subprocess.run(
                ['screen', '-S', session_name, '-X', 'quit'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return True, f"Session '{session_name}' terminated"
            else:
                return False, f"Failed to kill session: {result.stderr}"
                
        except Exception as e:
            return False, f"Error killing session: {str(e)}"
            
    def send_command(self, session_name: str, command: str) -> Tuple[bool, str]:
        """Send command to a screen session"""
        try:
            result = subprocess.run([
                'screen', '-S', session_name, '-X', 'stuff', f"{command}\n"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, f"Command sent to session '{session_name}'"
            else:
                return False, f"Failed to send command: {result.stderr}"
                
        except Exception as e:
            return False, f"Error sending command: {str(e)}"
            
    def cleanup_dead_sessions(self) -> Tuple[int, List[str]]:
        """Clean up dead/zombie screen sessions"""
        try:
            # screen -wipe removes dead sessions
            result = subprocess.run(
                ['screen', '-wipe'],
                capture_output=True,
                text=True
            )
            
            # Parse output to see what was cleaned
            cleaned = []
            if result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Removed dead session' in line:
                        # Extract session name
                        match = re.search(r'(\d+\.\S+)', line)
                        if match:
                            cleaned.append(match.group(1))
                            
            return len(cleaned), cleaned
            
        except Exception as e:
            return 0, [f"Error during cleanup: {str(e)}"]
            
    def get_session_info(self, session_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a session"""
        sessions = self.list_sessions()
        
        for session in sessions:
            if session['name'] == session_name or session['full_name'] == session_name:
                # Try to get more details
                try:
                    # Get session window list
                    result = subprocess.run([
                        'screen', '-S', session_name, '-Q', 'windows'
                    ], capture_output=True, text=True)
                    
                    session['windows'] = result.stdout.strip() if result.returncode == 0 else "Unknown"
                    
                except:
                    session['windows'] = "Unknown"
                    
                return session
                
        return None
        
    def is_session_running(self, session_name: str) -> bool:
        """Check if a session is currently running"""
        sessions = self.list_sessions()
        return any(
            (s['name'] == session_name or s['full_name'] == session_name) and 
            s['status'] in ['attached', 'detached']
            for s in sessions
        )
        
    def get_available_session_name(self, base_name: str) -> str:
        """Get an available session name by adding suffix if needed"""
        sessions = self.list_sessions()
        existing_names = {s['name'] for s in sessions}
        
        candidate = f"{self.session_prefix}_{base_name}"
        if candidate not in existing_names:
            return candidate
            
        # Try with numeric suffix
        counter = 1
        while f"{candidate}_{counter}" in existing_names:
            counter += 1
            
        return f"{candidate}_{counter}"
