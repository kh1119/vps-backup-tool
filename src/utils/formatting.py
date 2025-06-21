"""
Utility functions for formatting and display
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List

def format_bytes(bytes_val: float) -> str:
    """Format bytes to human readable format"""
    if bytes_val < 0:
        return "0 B"
        
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            if unit == 'B':
                return f"{int(bytes_val)} {unit}"
            else:
                return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} PB"

def format_bytes_per_second(bytes_val: float) -> str:
    """Format bytes per second to human readable format"""
    if bytes_val < 0:
        return "0 B/s"
        
    for unit in ['B/s', 'KB/s', 'MB/s', 'GB/s', 'TB/s']:
        if bytes_val < 1024.0:
            if unit == 'B/s':
                return f"{int(bytes_val)} {unit}"
            else:
                return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} PB/s"

def format_duration(duration: timedelta) -> str:
    """Format timedelta to human readable format"""
    total_seconds = int(duration.total_seconds())
    
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
        
    return " ".join(parts)

def format_timestamp(dt: datetime, include_date: bool = True) -> str:
    """Format datetime to readable string"""
    if include_date:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return dt.strftime("%H:%M:%S")

def print_header(title: str, width: int = 80, char: str = "="):
    """Print a formatted header"""
    print(char * width)
    print(f"{title:^{width}}")
    print(char * width)

def print_section(title: str, width: int = 80, char: str = "-"):
    """Print a formatted section header"""
    print(f"\n{char * width}")
    print(f"{title}")
    print(char * width)

def print_table(headers: List[str], rows: List[List[str]], min_width: int = 10):
    """Print a formatted table"""
    if not rows:
        return
        
    # Calculate column widths
    col_widths = [max(len(header), min_width) for header in headers]
    
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
                
    # Print header
    header_line = " | ".join(header.ljust(col_widths[i]) for i, header in enumerate(headers))
    print(header_line)
    print("-" * len(header_line))
    
    # Print rows
    for row in rows:
        row_line = " | ".join(str(row[i]).ljust(col_widths[i]) if i < len(row) else "".ljust(col_widths[i]) 
                             for i in range(len(headers)))
        print(row_line)

def print_key_value_pairs(data: Dict[str, Any], indent: int = 0):
    """Print key-value pairs in a formatted way"""
    prefix = " " * indent
    for key, value in data.items():
        if isinstance(value, dict):
            print(f"{prefix}{key}:")
            print_key_value_pairs(value, indent + 2)
        elif isinstance(value, list):
            print(f"{prefix}{key}:")
            for item in value:
                print(f"{prefix}  - {item}")
        else:
            print(f"{prefix}{key}: {value}")

def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string if it's too long"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def center_text(text: str, width: int, fill_char: str = " ") -> str:
    """Center text within a given width"""
    return text.center(width, fill_char)

def status_symbol(success: bool, success_symbol: str = "✅", fail_symbol: str = "❌") -> str:
    """Return status symbol based on success"""
    return success_symbol if success else fail_symbol

def progress_bar(current: int, total: int, width: int = 50, fill: str = "█", empty: str = "░") -> str:
    """Create a text progress bar"""
    if total == 0:
        percentage = 0
    else:
        percentage = min(current / total, 1.0)
        
    filled_width = int(width * percentage)
    bar = fill * filled_width + empty * (width - filled_width)
    percent_str = f"{percentage * 100:.1f}%"
    
    return f"[{bar}] {percent_str} ({current}/{total})"

class Colors:
    """ANSI color codes for terminal output"""
    
    # Regular colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Styles
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    
    @classmethod
    def colored(cls, text: str, color: str) -> str:
        """Return colored text"""
        return f"{color}{text}{cls.RESET}"

def colored_status(success: bool, success_text: str = "SUCCESS", fail_text: str = "FAILED") -> str:
    """Return colored status text"""
    if success:
        return Colors.colored(success_text, Colors.GREEN)
    else:
        return Colors.colored(fail_text, Colors.RED)

def print_logo():
    """Print application logo"""
    logo = """
    ╔══════════════════════════════════════╗
    ║        VPS Backup Tool v2.0          ║
    ║     Multi-Interface Monitoring       ║
    ║        + Screen Session Support      ║
    ╚══════════════════════════════════════╝
    """
    print(Colors.colored(logo, Colors.CYAN))

def print_warning(message: str):
    """Print warning message"""
    print(f"⚠️  {Colors.colored('Warning:', Colors.YELLOW)} {message}")

def print_error(message: str):
    """Print error message"""
    print(f"❌ {Colors.colored('Error:', Colors.RED)} {message}")

def print_success(message: str):
    """Print success message"""
    print(f"✅ {Colors.colored('Success:', Colors.GREEN)} {message}")

def print_info(message: str):
    """Print info message"""
    print(f"ℹ️  {Colors.colored('Info:', Colors.BLUE)} {message}")

def confirm_action(message: str, default: bool = False) -> bool:
    """Ask user for confirmation"""
    default_str = "Y/n" if default else "y/N"
    response = input(f"{message} [{default_str}]: ").lower().strip()
    
    if not response:
        return default
    
    return response in ['y', 'yes', 'true', '1']
