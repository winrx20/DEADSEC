#!/usr/bin/env python3
"""
Network Scanner - Post-Exploitation Module
Scans local network for hosts and open ports
For authorized penetration testing only
"""

import socket
import subprocess
import platform
import ipaddress
import concurrent.futures
from datetime import datetime

class NetworkScanner:
    def __init__(self):
        self.os_type = platform.system()
        self.local_ip = self.get_local_ip()
        self.network = self.get_network_range()
        
    def get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def get_network_range(self):
        """Calculate network range from local IP"""
        try:
            # Assume /24 network
            ip_parts = self.local_ip.split('.')
            network = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
            return ipaddress.ip_network(network, strict=False)
        except:
            return None
    
    def ping_host(self, ip):
        """Check if host is alive"""
        try:
            if self.os_type == "Windows":
                result = subprocess.run(
                    ['ping', '-n', '1', '-w', '1000', str(ip)],
                    capture_output=True,
                    timeout=2
                )
            else:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '1', str(ip)],
                    capture_output=True,
                    timeout=2
                )
            
            return result.returncode == 0
        except:
            return False
    
    def scan_port(self, ip, port, timeout=1):
        """Check if port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((str(ip), port))
            sock.close()
            return result == 0
        except:
            return False
    
    def get_hostname(self, ip):
        """Try to get hostname for IP"""
        try:
            return socket.gethostbyaddr(str(ip))[0]
        except:
            return None
    
    def scan_host_ports(self, ip, ports):
        """Scan multiple ports on a host"""
        open_ports = []
        
        for port in ports:
            if self.scan_port(ip, port):
                try:
                    service = socket.getservbyport(port)
                except:
                    service = "unknown"
                
                open_ports.append({
                    'port': port,
                    'service': service
                })
                print(f"    [+] Port {port} ({service}) is open")
        
        return open_ports
    
    def scan_network(self, common_ports=None):
        """Scan network for live hosts"""
        if not self.network:
            print("[!] Could not determine network range")
            return []
        
        if common_ports is None:
            # Common ports to scan
            common_ports = [21, 22, 23, 25, 80, 443, 445, 3389, 5900, 8080]
        
        print(f"[*] Scanning network: {self.network}")
        print(f"[*] Local IP: {self.local_ip}")
        print(f"[*] Ports to scan: {common_ports}\n")
        
        alive_hosts = []
        
        # Scan for live hosts
        print("[*] Discovering live hosts...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(self.ping_host, ip): ip for ip in self.network.hosts()}
            
            for future in concurrent.futures.as_completed(futures):
                ip = futures[future]
                try:
                    if future.result():
                        hostname = self.get_hostname(ip)
                        print(f"  [+] Live host: {ip}" + (f" ({hostname})" if hostname else ""))
                        alive_hosts.append({
                            'ip': str(ip),
                            'hostname': hostname,
                            'open_ports': []
                        })
                except:
                    pass
        
        print(f"\n[+] Found {len(alive_hosts)} live hosts\n")
        
        # Scan ports on live hosts
        print("[*] Scanning ports on live hosts...")
        for host in alive_hosts:
            print(f"\n  Scanning {host['ip']}...")
            host['open_ports'] = self.scan_host_ports(host['ip'], common_ports)
        
        return alive_hosts
    
    def scan_single_host(self, target_ip, ports=None):
        """Perform detailed scan on a single host"""
        if ports is None:
            # Extended port list for single host scan
            ports = list(range(1, 1025))  # Scan first 1024 ports
        
        print(f"[*] Scanning host: {target_ip}")
        print(f"[*] Scanning {len(ports)} ports...\n")
        
        hostname = self.get_hostname(target_ip)
        if hostname:
            print(f"[+] Hostname: {hostname}\n")
        
        open_ports = self.scan_host_ports(target_ip, ports)
        
        return {
            'ip': target_ip,
            'hostname': hostname,
            'open_ports': open_ports
        }
    
    def save_results(self, results, output_file='network_scan.txt'):
        """Save scan results to file"""
        with open(output_file, 'w') as f:
            f.write(f"Network Scan Results\n")
            f.write(f"Scan Date: {datetime.now()}\n")
            f.write(f"Network: {self.network}\n")
            f.write(f"="*60 + "\n\n")
            
            for host in results:
                f.write(f"Host: {host['ip']}\n")
                if host['hostname']:
                    f.write(f"Hostname: {host['hostname']}\n")
                f.write(f"Open Ports: {len(host['open_ports'])}\n")
                
                for port_info in host['open_ports']:
                    f.write(f"  - Port {port_info['port']}: {port_info['service']}\n")
                
                f.write("\n")
        
        print(f"\n[+] Results saved to: {output_file}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Network scanner for authorized pentesting')
    parser.add_argument('--target', help='Single target IP to scan')
    parser.add_argument('--ports', help='Comma-separated list of ports (e.g., 80,443,8080)')
    parser.add_argument('--full', action='store_true', help='Scan all ports (1-65535) on single target')
    parser.add_argument('--output', default='network_scan.txt', help='Output file for results')
    args = parser.parse_args()
    
    print("="*60)
    print("Network Scanner - Red Team Tool")
    print("For Authorized Penetration Testing Only")
    print("="*60 + "\n")
    
    scanner = NetworkScanner()
    
    # Parse port list if provided
    ports = None
    if args.ports:
        ports = [int(p.strip()) for p in args.ports.split(',')]
    elif args.full and args.target:
        ports = list(range(1, 65536))
    
    # Scan single target or network
    if args.target:
        results = [scanner.scan_single_host(args.target, ports)]
    else:
        results = scanner.scan_network(ports)
    
    # Save results
    scanner.save_results(results, args.output)
    
    print(f"\n[+] Scan complete!")
    print(f"[+] Total hosts scanned: {len(results)}")
    print(f"[+] Hosts with open ports: {sum(1 for h in results if h['open_ports'])}")

if __name__ == '__main__':
    main()
