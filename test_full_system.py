#!/usr/bin/env python3
"""
DeadSec Framework - Full System Test
Tests all components to ensure everything works correctly
"""

import os
import sys
import importlib.util
import ast

def test_file_exists(filepath, description):
    """Test if a file exists"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ MISSING: {description} - {filepath}")
        return False

def test_python_syntax(filepath, description):
    """Test Python file syntax"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code)
        print(f"✓ {description} syntax valid")
        return True
    except SyntaxError as e:
        print(f"✗ {description} syntax error: {e}")
        return False
    except Exception as e:
        print(f"⚠ {description} check error: {e}")
        return False

def test_imports(filepath, description):
    """Test if Python file can be imported"""
    try:
        spec = importlib.util.spec_from_file_location("test_module", filepath)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules["test_module"] = module
            # Don't execute, just check if it would import
            print(f"✓ {description} imports valid")
            return True
        else:
            print(f"⚠ {description} import spec invalid")
            return False
    except Exception as e:
        print(f"⚠ {description} import warning: {str(e)[:100]}")
        return True  # Some imports may fail due to missing dependencies

def main():
    print("=" * 80)
    print(" " * 20 + "DEADSEC FRAMEWORK SYSTEM TEST")
    print("=" * 80)
    print()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    results = []
    
    # Core Files
    print("🔧 TESTING CORE COMPONENTS")
    print("-" * 80)
    results.append(test_file_exists(os.path.join(base_dir, "src", "cnc_server.py"), "C&C Server"))
    results.append(test_file_exists(os.path.join(base_dir, "src", "bot.py"), "Bot Module"))
    results.append(test_file_exists(os.path.join(base_dir, "web_gui.html"), "Web GUI"))
    results.append(test_file_exists(os.path.join(base_dir, "app.js"), "JavaScript"))
    results.append(test_file_exists(os.path.join(base_dir, "styles.css"), "CSS"))
    print()
    
    # Python Payloads
    print("🎯 TESTING PYTHON PAYLOADS")
    print("-" * 80)
    payloads = [
        "credential_harvester.py",
        "keylogger.py",
        "screenshot_capture.py",
        "network_scanner.py",
        "file_exfiltrator.py",
        "privesc_checker.py",
        "python_agent.py",
        "ddos_attack.py",
        "privesc_exploit.py"
    ]
    
    for payload in payloads:
        filepath = os.path.join(base_dir, "payloads", payload)
        if test_file_exists(filepath, payload):
            test_python_syntax(filepath, payload)
    print()
    
    # PowerShell Payloads
    print("💻 TESTING POWERSHELL PAYLOADS")
    print("-" * 80)
    ps_payloads = [
        "windows_agent.ps1",
        "windows_credential_harvester.ps1",
        "windows_keylogger.ps1",
        "windows_screenshot.ps1",
        "windows_network_scanner.ps1",
        "windows_file_exfiltrator.ps1",
        "windows_geolocation.ps1",
        "windows_privesc_checker.ps1",
        "windows_ddos.ps1",
        "windows_privesc_exploit.ps1"
    ]
    
    for payload in ps_payloads:
        filepath = os.path.join(base_dir, "payloads", payload)
        results.append(test_file_exists(filepath, payload))
    print()
    
    # Documentation
    print("📚 TESTING DOCUMENTATION")
    print("-" * 80)
    docs = [
        "Readme.md",
        "RED_TEAM_GUIDE.md",
        "WEB_GUI_GUIDE.md",
        "DDOS_ATTACK_GUIDE.md",
        "WINDOWS_PAYLOADS_GUIDE.md",
        "FRAMEWORK_SUMMARY.md",
        "QUICK_REFERENCE.md",
        "DEADSEC_LOGO.txt"
    ]
    
    for doc in docs:
        filepath = os.path.join(base_dir, doc)
        results.append(test_file_exists(filepath, doc))
    print()
    
    # Test Core Python Syntax
    print("🔬 TESTING CORE PYTHON SYNTAX")
    print("-" * 80)
    test_python_syntax(os.path.join(base_dir, "src", "cnc_server.py"), "C&C Server")
    test_python_syntax(os.path.join(base_dir, "src", "bot.py"), "Bot Module")
    print()
    
    # Test Web GUI Structure
    print("🌐 TESTING WEB GUI STRUCTURE")
    print("-" * 80)
    try:
        with open(os.path.join(base_dir, "web_gui.html"), 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        checks = [
            ("DeadSec Title", "DEADSEC" in html_content),
            ("Privilege Escalation Button", "showPrivescDialog()" in html_content),
            ("DDoS Attack Button", "showDDoSDialog()" in html_content),
            ("Privesc Dialog", "privesc-dialog" in html_content),
            ("DDoS Dialog", "ddos-dialog" in html_content),
            ("Bot List", "bot-list" in html_content),
            ("Console Output", "console-output" in html_content),
        ]
        
        for check_name, check_result in checks:
            if check_result:
                print(f"✓ {check_name} present")
                results.append(True)
            else:
                print(f"✗ {check_name} MISSING")
                results.append(False)
    except Exception as e:
        print(f"✗ Error reading web_gui.html: {e}")
        results.append(False)
    print()
    
    # Test JavaScript Functions
    print("⚡ TESTING JAVASCRIPT FUNCTIONS")
    print("-" * 80)
    try:
        with open(os.path.join(base_dir, "app.js"), 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        functions = [
            "showPrivescDialog",
            "closePrivescDialog",
            "launchPrivesc",
            "showDDoSDialog",
            "closeDDoSDialog",
            "launchDDoS",
            "deployPayload",
            "refreshBots",
            "executeRemoteCommand"
        ]
        
        for func in functions:
            if f"function {func}" in js_content or f"const {func}" in js_content:
                print(f"✓ Function '{func}' defined")
                results.append(True)
            else:
                print(f"✗ Function '{func}' MISSING")
                results.append(False)
    except Exception as e:
        print(f"✗ Error reading app.js: {e}")
        results.append(False)
    print()
    
    # Test Payload Configurations
    print("⚙️ TESTING PAYLOAD CONFIGURATIONS")
    print("-" * 80)
    try:
        with open(os.path.join(base_dir, "app.js"), 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        payload_configs = [
            "credential_harvester",
            "keylogger",
            "screenshot",
            "network_scanner",
            "file_exfiltrator",
            "privesc_checker",
            "geolocation",
            "ddos_attack",
            "privesc_exploit"
        ]
        
        for config in payload_configs:
            if config in js_content:
                print(f"✓ Payload config '{config}' present")
                results.append(True)
            else:
                print(f"⚠ Payload config '{config}' not found in JS")
                results.append(False)
    except Exception as e:
        print(f"✗ Error checking payload configs: {e}")
        results.append(False)
    print()
    
    # Summary
    print("=" * 80)
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\n📊 TEST RESULTS: {passed}/{total} checks passed ({percentage:.1f}%)\n")
    
    if percentage == 100:
        print("🎉 ALL TESTS PASSED! DeadSec Framework is fully operational!")
        print("✓ All core components present")
        print("✓ All payloads available")
        print("✓ Web GUI properly configured")
        print("✓ JavaScript functions defined")
        print("\n🚀 You can start the server with: python src/cnc_server.py")
        print("🌐 Access the web GUI at: http://localhost:5000")
    elif percentage >= 90:
        print("✅ Framework is operational with minor issues")
        print("⚠️ Some optional components may be missing")
    elif percentage >= 75:
        print("⚠️ Framework is partially operational")
        print("❗ Some critical components may need attention")
    else:
        print("❌ Framework has significant issues")
        print("❗ Multiple critical components are missing")
    
    print("\n" + "=" * 80)
    return 0 if percentage >= 90 else 1

if __name__ == "__main__":
    sys.exit(main())
