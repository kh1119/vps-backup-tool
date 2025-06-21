#!/usr/bin/env python3
"""
Demo script để hiển thị multi-interface monitoring improvements
Sử dụng mock data để demo khi không có SSH connection
"""

def format_bytes(bytes_val):
    """Format bytes thành đơn vị dễ đọc"""
    for unit in ['B/s', 'KB/s', 'MB/s', 'GB/s']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} TB/s"

def demo_multi_interface_monitoring():
    """Demo multi-interface monitoring với mock data"""
    print("🔍 Demo: Multi-Interface Bandwidth Monitoring")
    print("=" * 60)
    print("📍 Trước khi cải thiện (chỉ theo dõi 1 interface chính):")
    print("   ❌ Chỉ hiển thị tổng bandwidth")
    print("   ❌ Không biết interface nào đang active")
    print("   ❌ Có thể bỏ sót traffic trên interface phụ")
    print("")
    
    print("📍 Sau khi cải thiện (theo dõi tất cả interfaces):")
    print("   ✅ Hiển thị tổng bandwidth từ TẤT CẢ interfaces")
    print("   ✅ Đếm số interfaces active/total")
    print("   ✅ Hiển thị chi tiết từng interface có traffic")
    print("   ✅ Loại bỏ interfaces ảo (docker, bridge, tunnel)")
    print("   ✅ Phân loại interface types")
    print("")
    
    # Mock data for demo
    mock_interfaces = {
        'eth0': {
            'download_bps': 52428800,  # 50MB/s
            'upload_bps': 10485760,    # 10MB/s
            'total_rx_gb': 125.5,
            'total_tx_gb': 89.2,
            'is_active': True
        },
        'eth1': {
            'download_bps': 1048576,   # 1MB/s
            'upload_bps': 524288,      # 512KB/s
            'total_rx_gb': 25.8,
            'total_tx_gb': 12.4,
            'is_active': True
        },
        'wlan0': {
            'download_bps': 0,
            'upload_bps': 0,
            'total_rx_gb': 5.2,
            'total_tx_gb': 2.1,
            'is_active': False
        }
    }
    
    mock_data = {
        'interfaces': mock_interfaces,
        'total_download_bps': 53477376,  # Total từ tất cả
        'total_upload_bps': 11010048,
        'interface_count': 3,
        'active_count': 2
    }
    
    print("🧪 Demo Output - NEW Format:")
    print("-" * 60)
    
    # Simulate monitoring output
    total_down = format_bytes(mock_data['total_download_bps'])
    total_up = format_bytes(mock_data['total_upload_bps'])
    interface_info = f"({mock_data['active_count']}/{mock_data['interface_count']} active)"
    
    print(f"[12:34:56] 📊 Total: ⬇️ {total_down} | ⬆️ {total_up} {interface_info}")
    print(f"         Active interfaces:")
    
    # Show active interfaces sorted by traffic
    active_interfaces = [(iface, data) for iface, data in mock_interfaces.items() if data['is_active']]
    for iface, data in sorted(active_interfaces, 
                            key=lambda x: x[1]['download_bps'] + x[1]['upload_bps'], 
                            reverse=True):
        down = format_bytes(data['download_bps'])
        up = format_bytes(data['upload_bps'])
        print(f"           {iface}: ⬇️ {down} | ⬆️ {up}")
    
    # High traffic warning
    if mock_data['total_download_bps'] > 50 * 1024 * 1024:
        print(f"         ⚠️  HIGH DOWNLOAD TRAFFIC!")
    
    print("")
    print("📊 Detailed View (monitor_bandwidth.py):")
    print("-" * 60)
    print(f"📊 Total Bandwidth: ⬇️ {total_down} | ⬆️ {total_up}")
    print(f"🔌 Network Interfaces: {mock_data['active_count']}/{mock_data['interface_count']} active")
    print("")
    print("📡 Network Interface Details:")
    
    # Show all interfaces with status
    for interface, stats in sorted(mock_interfaces.items(), 
                                 key=lambda x: x[1]['download_bps'] + x[1]['upload_bps'], 
                                 reverse=True):
        download_speed = format_bytes(stats['download_bps'])
        upload_speed = format_bytes(stats['upload_bps'])
        
        status = ""
        if stats['download_bps'] > 50 * 1024 * 1024:
            status += " ⚠️ HIGH DOWNLOAD"
        if stats['upload_bps'] > 10 * 1024 * 1024:
            status += " ⚠️ HIGH UPLOAD"
        
        activity = "🟢" if stats['is_active'] else "⚫"
        print(f"   {activity} {interface}: ⬇️ {download_speed} | ⬆️ {upload_speed}{status}")
        print(f"            Total: ⬇️ {stats['total_rx_gb']:.2f}GB | ⬆️ {stats['total_tx_gb']:.2f}GB")
    
    # Interface classification
    print("")
    print("🏷️  Interface Types: Ethernet: 2, WiFi: 1")
    
    print("")
    print("=" * 60)
    print("✅ Improvements implemented:")
    print("  1. Loại bỏ interfaces ảo (lo, docker*, br-*, veth*, virbr*, tun*, tap*)")
    print("  2. Tính tổng bandwidth chính xác từ TẤT CẢ interfaces")
    print("  3. Hiển thị số lượng interfaces active/total")
    print("  4. Sắp xếp interfaces theo traffic (cao nhất trước)")
    print("  5. Phân biệt interfaces active/inactive bằng icons")
    print("  6. Cảnh báo thông minh cho high traffic")
    print("  7. Phân loại interface types (Ethernet, WiFi, etc.)")
    print("  8. Error handling tốt hơn cho malformed data")

def demo_filtering_logic():
    """Demo interface filtering logic"""
    print("\n🎯 Interface Filtering Logic:")
    print("=" * 60)
    
    all_interfaces = [
        'lo',           # ❌ Loopback - skip
        'eth0',         # ✅ Physical Ethernet - monitor
        'eth1',         # ✅ Physical Ethernet - monitor
        'wlan0',        # ✅ WiFi - monitor
        'docker0',      # ❌ Docker bridge - skip
        'br-1234abc',   # ❌ Custom bridge - skip
        'veth123456',   # ❌ Virtual ethernet - skip
        'virbr0',       # ❌ Virtual bridge - skip
        'tun0',         # ❌ Tunnel - skip
        'tap0',         # ❌ TAP interface - skip
        'enp2s0',       # ✅ Network interface - monitor
    ]
    
    skip_patterns = ['lo', 'docker', 'br-', 'veth', 'virbr', 'tun', 'tap']
    
    print("📋 All interfaces found:")
    monitored = []
    skipped = []
    
    for iface in all_interfaces:
        if any(iface.startswith(pattern) for pattern in skip_patterns):
            print(f"   ❌ {iface} - Skipped (virtual/container)")
            skipped.append(iface)
        else:
            print(f"   ✅ {iface} - Will monitor")
            monitored.append(iface)
    
    print(f"\n📊 Result: {len(monitored)} monitored, {len(skipped)} skipped")
    print(f"   Monitored: {', '.join(monitored)}")
    print(f"   Skipped: {', '.join(skipped)}")

def main():
    demo_multi_interface_monitoring()
    demo_filtering_logic()
    
    print("\n" + "=" * 60)
    print("🚀 Ready to test on VPS:")
    print("   1. Fix SSH connection first: ./test_ssh.sh config.yaml")
    print("   2. Test interface detection: python3 test_multi_interface.py config.yaml")
    print("   3. Quick bandwidth check: python3 monitor_bandwidth.py config.yaml")
    print("   4. Live monitoring: python3 monitor_bandwidth.py config.yaml monitor 60 5")
    print("   5. Backup with monitoring: python3 main.py config.yaml")

if __name__ == '__main__':
    main()
