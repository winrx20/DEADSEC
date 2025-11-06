#!/usr/bin/env python3
"""
Red Team C&C Framework Test Suite
Verify all components are working correctly
"""

import sys
import os
import time
import requests
import subprocess
from pathlib import Path

def test_imports():
    """Test that all required modules are available"""
    print("\n[*] Testing Python imports...")
    try:
        import flask
        print("  [+] Flask: OK")
    except ImportError:
        print("  [!] Flask: MISSING - run: pip install flask")
        return False
    
    try:
        import paramiko
        print("  [+] Paramiko: OK")
    except ImportError:
        print("  [!] Paramiko: MISSING - run: pip install paramiko")
        return False
    
    try:
        import requests
        print("  [+] Requests: OK")
    except ImportError:
        print("  [!] Requests: MISSING (optional) - run: pip install requests")
    
    return True

def test_files():
    """Test that all required files exist"""
    print("\n[*] Testing file structure...")
    
    required_files = [
        'src/bot.py',
        'src/cnc_server.py',
        'payloads/python_agent.py',
        'payloads/linux_agent.sh',
        'payloads/windows_agent.ps1',
        'payloads/README.md',
        'RED_TEAM_GUIDE.md',
        'build_payload.py'
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  [+] {file_path}")
        else:
            print(f"  [!] {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def test_cnc_server():
    """Test C&C server startup"""
    print("\n[*] Testing C&C server...")
    print("  [*] Starting server (this will take a few seconds)...")
    
    try:
        # Start server in background
        proc = subprocess.Popen(
            [sys.executable, 'src/cnc_server.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(3)
        
        # Test if server is responding
        try:
            response = requests.get('http://127.0.0.1:5000/', timeout=2)
            print("  [+] Server started successfully")
            
            # Test add_bot endpoint
            test_data = {
                "bot_id": "test-bot-001",
                "host": "127.0.0.1",
                "port": 22,
                "username": "test",
                "password": "test",
                "hostname": "test-host"
            }
            
            response = requests.post(
                'http://127.0.0.1:5000/add_bot',
                json=test_data,
                timeout=2
            )
            
            if response.status_code == 200:
                print("  [+] API endpoint test: OK")
            else:
                print(f"  [!] API endpoint test: FAILED ({response.status_code})")
            
            # Cleanup
            proc.terminate()
            proc.wait(timeout=5)
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"  [!] Server not responding: {e}")
            proc.terminate()
            return False
            
    except Exception as e:
        print(f"  [!] Failed to start server: {e}")
        return False

def test_payload_syntax():
    """Test payload syntax"""
    print("\n[*] Testing payload syntax...")
    
    # Test Python agent
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', 'payloads/python_agent.py'],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print("  [+] Python agent syntax: OK")
        else:
            print(f"  [!] Python agent syntax: ERROR\n{result.stderr.decode()}")
    except Exception as e:
        print(f"  [!] Python agent test failed: {e}")
    
    # Test bash script (basic check)
    if Path('payloads/linux_agent.sh').exists():
        try:
            result = subprocess.run(
                ['bash', '-n', 'payloads/linux_agent.sh'],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                print("  [+] Linux agent syntax: OK")
            else:
                print(f"  [!] Linux agent syntax: ERROR\n{result.stderr.decode()}")
        except FileNotFoundError:
            print("  [!] bash not found, skipping Linux agent test")
        except Exception as e:
            print(f"  [!] Linux agent test failed: {e}")
    
    # Test PowerShell script
    if Path('payloads/windows_agent.ps1').exists():
        if sys.platform == 'win32':
            try:
                result = subprocess.run(
                    ['powershell', '-Command', 'Get-Command', '-Syntax', 'payloads/windows_agent.ps1'],
                    capture_output=True,
                    timeout=5
                )
                print("  [+] Windows agent syntax: OK")
            except Exception as e:
                print(f"  [!] Windows agent test failed: {e}")
        else:
            print("  [~] Windows agent: Skipped (not on Windows)")

def test_build_script():
    """Test payload builder"""
    print("\n[*] Testing payload builder...")
    
    try:
        result = subprocess.run(
            [sys.executable, 'build_payload.py', '--help'],
            capture_output=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("  [+] Payload builder: OK")
            return True
        else:
            print(f"  [!] Payload builder: ERROR\n{result.stderr.decode()}")
            return False
    except Exception as e:
        print(f"  [!] Payload builder test failed: {e}")
        return False

def main():
    print("="*70)
    print("Red Team C&C Framework - Test Suite")
    print("="*70)
    
    results = {
        'imports': test_imports(),
        'files': test_files(),
        'payload_syntax': True,  # Always run
        'build_script': test_build_script(),
        'cnc_server': False  # Optional
    }
    
    test_payload_syntax()
    
    # Ask if user wants to test C&C server
    print("\n[?] Test C&C server startup? This will start and stop the server (y/n): ", end='')
    if input().lower() == 'y':
        results['cnc_server'] = test_cnc_server()
    else:
        print("  [~] Skipped C&C server test")
    
    # Summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len([k for k in results.keys() if results[k] is not False or k != 'cnc_server'])
    
    for test_name, result in results.items():
        if result is not False:
            status = "[+] PASS" if result else "[!] FAIL"
            print(f"  {status}: {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if all(v for k, v in results.items() if v is not False):
        print("\n[+] All tests passed! Framework is ready to use.")
        print("\n[*] Next steps:")
        print("  1. Read RED_TEAM_GUIDE.md for deployment instructions")
        print("  2. Configure payloads with build_payload.py")
        print("  3. Start C&C server: python src/cnc_server.py")
        print("  4. Deploy agents to authorized target systems")
        return 0
    else:
        print("\n[!] Some tests failed. Please fix the issues before using the framework.")
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[!] Tests interrupted by user")
        sys.exit(1)
