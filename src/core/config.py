"""
Core configuration management module
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """Quản lý cấu hình ứng dụng"""
    
    def __init__(self, config_dir: str = None):
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Default to configs directory relative to script location
            script_dir = Path(__file__).parent.parent.parent
            self.config_dir = script_dir / 'configs'
            
        self.config_file = self.config_dir / 'config.yaml'
        self.template_file = self.config_dir / 'config.yaml.template'
        self._config = None
        
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file"""
        if config_path:
            config_file = Path(config_path)
        else:
            config_file = self.config_file
            
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
            
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
                
            # Validate config
            self._validate_config()
            
            return self._config
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading config: {e}")
            
    def _validate_config(self):
        """Validate configuration values"""
        if not self._config:
            raise ValueError("No configuration loaded")
            
        required_fields = [
            'ssh_user', 'ssh_host', 'ssh_key',
            'remote_root', 'local_root'
        ]
        
        for field in required_fields:
            if field not in self._config:
                raise ValueError(f"Required field missing in config: {field}")
                
        # Validate paths
        ssh_key = Path(self._config['ssh_key']).expanduser()
        if not ssh_key.exists():
            raise FileNotFoundError(f"SSH key not found: {ssh_key}")
            
        # Ensure numeric values
        numeric_fields = {
            'ssh_port': 22,
            'threads': 4,
            'bwlimit': 0,
            'monitoring_interval': 10
        }
        
        for field, default in numeric_fields.items():
            if field in self._config:
                try:
                    self._config[field] = int(self._config[field])
                except (ValueError, TypeError):
                    self._config[field] = default
            else:
                self._config[field] = default
                
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        if not self._config:
            self.load_config()
            
        return self._config.get(key, default)
        
    def get_nested(self, keys: str, default: Any = None) -> Any:
        """Get nested configuration value using dot notation"""
        if not self._config:
            self.load_config()
            
        value = self._config
        for key in keys.split('.'):
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
        
    def create_default_config(self) -> bool:
        """Create default config from template"""
        try:
            if not self.template_file.exists():
                raise FileNotFoundError(f"Template file not found: {self.template_file}")
                
            # Create config directory if it doesn't exist
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy template to config
            import shutil
            shutil.copy2(self.template_file, self.config_file)
            
            return True
            
        except Exception as e:
            print(f"Error creating default config: {e}")
            return False
            
    def config_exists(self) -> bool:
        """Check if config file exists"""
        return self.config_file.exists()
        
    @property
    def config(self) -> Dict[str, Any]:
        """Get full configuration"""
        if not self._config:
            self.load_config()
        return self._config
        
    def get_ssh_command_base(self) -> list:
        """Get base SSH command with authentication"""
        return [
            'ssh',
            '-i', str(Path(self.get('ssh_key')).expanduser()),
            '-p', str(self.get('ssh_port', 22)),
            '-o', 'ConnectTimeout=30',
            '-o', 'ServerAliveInterval=60',
            '-o', 'ServerAliveCountMax=3'
        ]
        
    def get_rsync_command_base(self) -> list:
        """Get base rsync command with options"""
        ssh_cmd = f"ssh -i {Path(self.get('ssh_key')).expanduser()} -p {self.get('ssh_port', 22)}"
        
        base_cmd = [
            'rsync',
            '-e', ssh_cmd,
            f"--bwlimit={self.get('bwlimit', 0)}"
        ]
        
        # Add rsync options
        rsync_opts = self.get('rsync_opts', [])
        base_cmd.extend(rsync_opts)
        
        return base_cmd
        
    def get_remote_connection_string(self) -> str:
        """Get remote connection string for rsync"""
        return f"{self.get('ssh_user')}@{self.get('ssh_host')}"
        
    def setup_directories(self):
        """Create necessary directories"""
        directories = [
            self.get('local_root'),
            self.get('tmp_dir', 'tmp'),
            self.get('log_dir', 'logs')
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
