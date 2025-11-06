#!/usr/bin/env python3
"""
Compatibility Test Script
Tests integration between C&C server and Windows native payloads
"""

import os
import sys
from pathlib import Path

def test_cnc_server_endpoints():
    """Test that C&C server has required endpoints"""
    print("[*] Testing C&C server structure...")
    
    cnc_path = Path("src/cnc_server.py")
    if not cnc_path.exists():
        print("[!] ERROR: cnc_server.py not found")
        return False
    
    with open(cnc_path, 'r') as f:
        content = f.read()
    
    required_endpoints = [
        "'/add_bot'",
        "'/send_command'",
        "'/upload_file'",
        "'/download_file'"
    ]
    
    missing = []
    for endpoint in required_endpoints:
        if endpoint not in content:
            missing.append(endpoint)
    
    if missing:
        print(f"[!] ERROR: Missing endpoints: {', '.join(missing)}")
        return False
    
    print("[+] C&C server has all required endpoints")
    return True

def test_bot_class():
    """Test that Bot class has required methods"""
    print("[*] Testing Bot class structure...")
    
    bot_path = Path("src/bot.py")
    if not bot_path.exists():
        print("[!] ERROR: bot.py not found")
        return False
    
    with open(bot_path, 'r') as f:
        content = f.read()
    
    required_methods = [
        "def connect(",
        "def execute_command(",
        "def download_file(",
        "def upload_file("
    ]
    
    missing = []
    for method in required_methods:
        if method not in content:
            missing.append(method)
    
    if missing:
        print(f"[!] ERROR: Missing methods: {', '.join(missing)}")
        return False
    
    print("[+] Bot class has all required methods")
    return True

def test_windows_agent():
    """Test that Windows agent exists and has SSH support"""
    print("[*] Testing Windows agent...")
    
    agent_path = Path("payloads/windows_agent.ps1")
    if not agent_path.exists():
        print("[!] ERROR: windows_agent.ps1 not found")
        return False
    
    with open(agent_path, 'r') as f:
        content = f.read()
    
    required_elements = [
        "$CncServer",
        "add_bot",
        "$SshPassword"
    ]
    
    missing = []
    for element in required_elements:
        if element not in content:
            missing.append(element)
    
    if missing:
        print(f"[!] ERROR: Missing elements: {', '.join(missing)}")
        return False
    
    print("[+] Windows agent is properly configured")
    return True

def test_native_windows_payloads():
    """Test that all native Windows payloads exist"""
    print("[*] Testing native Windows payloads...")
    
    payloads = [
        "windows_credential_harvester.ps1",
        "windows_keylogger.ps1",
        "windows_screenshot.ps1",
        "windows_network_scanner.ps1",
        "windows_file_exfiltrator.ps1",
        "windows_privesc_checker.ps1"
    ]
    
    missing = []
    for payload in payloads:
        payload_path = Path(f"payloads/{payload}")
        if not payload_path.exists():
            missing.append(payload)
        else:
            # Check if payload outputs to files (required for exfiltration)
            with open(payload_path, 'r') as f:
                content = f.read()
                if "$OutputFile" not in content and "$OutputDir" not in content:
                    print(f"[!] WARNING: {payload} may not output to files properly")
    
    if missing:
        print(f"[!] ERROR: Missing payloads: {', '.join(missing)}")
        return False
    
    print(f"[+] All {len(payloads)} native Windows payloads exist")
    return True

def test_documentation():
    """Test that integration documentation exists"""
    print("[*] Testing documentation...")
    
    docs = [
        "Readme.md",
        "RED_TEAM_GUIDE.md",
        "WINDOWS_PAYLOADS_GUIDE.md",
        "CNC_INTEGRATION_GUIDE.md",
        "ENGAGEMENT_CHECKLIST.md"
    ]
    
    missing = []
    for doc in docs:
        if not Path(doc).exists():
            missing.append(doc)
    
    if missing:
        print(f"[!] ERROR: Missing documentation: {', '.join(missing)}")
        return False
    
    print(f"[+] All {len(docs)} documentation files exist")
    return True

def test_payload_output_compatibility():
    """Test that payloads output in a format compatible with C&C exfiltration"""
    print("[*] Testing payload output compatibility...")
    
    payloads_info = {
        "windows_credential_harvester.ps1": ["$OutputDir", "harvested_credentials"],
        "windows_keylogger.ps1": ["$OutputFile", "keylog.txt"],
        "windows_screenshot.ps1": ["$OutputDir", "screenshots"],
        "windows_network_scanner.ps1": ["$OutputFile", "network_scan.txt"],
        "windows_file_exfiltrator.ps1": ["$OutputDir", "exfiltrated_data"],
        "windows_privesc_checker.ps1": ["$OutputFile", "privesc_findings.txt"]
    }
    
    issues = []
    for payload, checks in payloads_info.items():
        payload_path = Path(f"payloads/{payload}")
        if payload_path.exists():
            with open(payload_path, 'r') as f:
                content = f.read()
                for check in checks:
                    if check not in content:
                        issues.append(f"{payload}: missing '{check}'")
    
    if issues:
        print("[!] WARNING: Potential compatibility issues:")
        for issue in issues:
            print(f"    - {issue}")
        return False
    
    print("[+] All payloads have compatible output mechanisms")
    return True

def main():
    print("="*60)
    print("C&C and Native Windows Payload Compatibility Test")
    print("="*60 + "\n")
    
    tests = [
        ("C&C Server Endpoints", test_cnc_server_endpoints),
        ("Bot Class Methods", test_bot_class),
        ("Windows Agent", test_windows_agent),
        ("Native Windows Payloads", test_native_windows_payloads),
        ("Documentation", test_documentation),
        ("Payload Output Compatibility", test_payload_output_compatibility)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print()
        except Exception as e:
            print(f"[!] ERROR in {test_name}: {e}")
            results.append((test_name, False))
            print()
    
    print("="*60)
    print("Test Results Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[+] All compatibility tests PASSED!")
        print("[+] Framework is ready for deployment")
        return 0
    else:
        print(f"\n[!] {total - passed} test(s) FAILED")
        print("[!] Review errors above and fix issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())
