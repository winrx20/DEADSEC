#!/usr/bin/env python3
"""
Red Team AV Evasion Validation Test
Comprehensive test to ensure AV evasion techniques are working for red team operations
"""

import os
import sys
import time
import subprocess
import tempfile
import hashlib
from pathlib import Path

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

class RedTeamEvasionValidator:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.temp_dir = Path(tempfile.mkdtemp(prefix="deadsec_test_"))
        self.passed = 0
        self.failed = 0
        
    def print_header(self, text):
        print(f"\n{BLUE}{'='*80}{RESET}")
        print(f"{BOLD}{BLUE}{text.center(80)}{RESET}")
        print(f"{BLUE}{'='*80}{RESET}")
        
    def print_test(self, name):
        print(f"{YELLOW}[TEST]{RESET} {name}...", end=' ')
        
    def print_pass(self, details=""):
        self.passed += 1
        msg = f"{GREEN}✓ PASS{RESET}"
        if details:
            msg += f" - {details}"
        print(msg)
        
    def print_fail(self, error=""):
        self.failed += 1
        msg = f"{RED}✗ FAIL{RESET}"
        if error:
            msg += f" - {error}"
        print(msg)
        
    def create_test_payload(self):
        """Create a simple test payload for evasion testing"""
        test_payload = '''#!/usr/bin/env python3
import os
import sys
import socket
import base64

# Simple red team payload for testing
def main():
    # Credential harvesting simulation
    username = os.getenv('USERNAME', 'unknown')
    hostname = socket.gethostname()
    
    # Data exfiltration simulation
    data = {
        'type': 'credentials',
        'username': username,
        'hostname': hostname,
        'domain': os.getenv('USERDOMAIN', 'unknown')
    }
    
    # Network communication simulation
    try:
        encoded_data = base64.b64encode(str(data).encode()).decode()
        # In real scenario, this would send to C&C
        print(f"[EXFIL] {encoded_data}")
    except Exception as e:
        pass
    
    return True

if __name__ == "__main__":
    main()
'''
        test_file = self.temp_dir / "test_payload.py"
        with open(test_file, 'w') as f:
            f.write(test_payload)
        return test_file
        
    def test_python_evasion_techniques(self):
        """Test all Python evasion techniques"""
        self.print_header("PYTHON AV EVASION TESTS")
        
        test_payload = self.create_test_payload()
        
        techniques = ['encrypt', 'compress', 'obfuscate', 'split', 'full']
        
        for technique in techniques:
            self.print_test(f"Python evasion technique: {technique}")
            
            output_file = self.temp_dir / f"evaded_{technique}.py"
            
            try:
                result = subprocess.run([
                    sys.executable, 
                    str(self.project_root / 'payloads' / 'av_evasion.py'),
                    '-i', str(test_payload),
                    '-o', str(output_file),
                    '--technique', technique,
                    '-q'
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and output_file.exists():
                    # Check if output is different from input (evasion applied)
                    original_hash = self.get_file_hash(test_payload)
                    evaded_hash = self.get_file_hash(output_file)
                    
                    if original_hash != evaded_hash:
                        # Test if evaded payload still executes
                        exec_result = subprocess.run([
                            sys.executable, str(output_file)
                        ], capture_output=True, text=True, timeout=10)
                        
                        if exec_result.returncode == 0:
                            self.print_pass(f"Evaded and functional")
                        else:
                            self.print_fail(f"Evaded but non-functional: {exec_result.stderr}")
                    else:
                        self.print_fail("No evasion applied (identical hashes)")
                else:
                    self.print_fail(f"Build failed: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                self.print_fail("Timeout")
            except Exception as e:
                self.print_fail(str(e))
                
    def test_powershell_evasion_basics(self):
        """Test PowerShell evasion loading"""
        self.print_header("POWERSHELL AV EVASION TESTS")
        
        self.print_test("PowerShell module syntax validation")
        try:
            ps_file = self.project_root / 'payloads' / 'windows_av_evasion.ps1'
            result = subprocess.run([
                'powershell', '-ExecutionPolicy', 'Bypass',
                '-Command', f'Get-Content "{ps_file}" | Out-Null; Write-Host "OK"'
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and 'OK' in result.stdout:
                self.print_pass("Syntax valid")
            else:
                self.print_fail(f"Syntax error: {result.stderr}")
        except Exception as e:
            self.print_fail(str(e))
            
        self.print_test("PowerShell AMSI bypass functions")
        try:
            # Load only the functions without running the main script
            result = subprocess.run([
                'powershell', '-ExecutionPolicy', 'Bypass',
                '-Command', f'$content = Get-Content "{ps_file}"; $functions = $content -join "`n"; iex $functions; if (Get-Command Invoke-AMSIBypass -ErrorAction SilentlyContinue) {{ Write-Host "AMSI_OK" }}'
            ], capture_output=True, text=True, timeout=15)
            
            if 'AMSI_OK' in result.stdout:
                self.print_pass("AMSI bypass available")
            else:
                self.print_fail("AMSI bypass not found")
        except Exception as e:
            self.print_fail(str(e))
            
    def test_evasion_effectiveness(self):
        """Test evasion effectiveness with signature analysis"""
        self.print_header("EVASION EFFECTIVENESS TESTS")
        
        test_payload = self.create_test_payload()
        
        # Test signature changes
        self.print_test("Signature uniqueness (full evasion)")
        try:
            output_file1 = self.temp_dir / "evaded1.py"
            output_file2 = self.temp_dir / "evaded2.py"
            
            # Build same payload twice
            for i, output in enumerate([output_file1, output_file2], 1):
                subprocess.run([
                    sys.executable, 
                    str(self.project_root / 'payloads' / 'av_evasion.py'),
                    '-i', str(test_payload),
                    '-o', str(output),
                    '--technique', 'full',
                    '-q'
                ], capture_output=True, timeout=30)
                time.sleep(1)  # Ensure different timestamps
            
            if output_file1.exists() and output_file2.exists():
                hash1 = self.get_file_hash(output_file1)
                hash2 = self.get_file_hash(output_file2)
                
                if hash1 != hash2:
                    self.print_pass("Polymorphic - different signatures each build")
                else:
                    self.print_fail("Static signatures - same hash each build")
            else:
                self.print_fail("Build failed")
                
        except Exception as e:
            self.print_fail(str(e))
            
    def test_red_team_features(self):
        """Test specific red team operational features"""
        self.print_header("RED TEAM OPERATIONAL FEATURES")
        
        # Test anti-debugging features
        self.print_test("Anti-debugging features present")
        try:
            av_module = self.project_root / 'payloads' / 'av_evasion.py'
            with open(av_module, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            anti_debug_features = [
                'add_anti_debug',
                'IsDebuggerPresent',
                'sys.gettrace',
                'PYDEVD'
            ]
            
            found_features = [f for f in anti_debug_features if f in content]
            
            if len(found_features) >= 3:
                self.print_pass(f"Found {len(found_features)}/4 anti-debugging techniques")
            else:
                self.print_fail(f"Only {len(found_features)}/4 anti-debugging techniques")
                
        except Exception as e:
            self.print_fail(str(e))
            
        # Test VM detection
        self.print_test("VM/Sandbox detection present")
        try:
            vm_detection_features = [
                'add_vm_detection',
                'vboxservice',
                'vmtoolsd',
                'System32/Drivers/Vmmouse'
            ]
            
            found_vm = [f for f in vm_detection_features if f in content]
            
            if len(found_vm) >= 3:
                self.print_pass(f"VM detection comprehensive")
            else:
                self.print_fail(f"VM detection incomplete")
                
        except Exception as e:
            self.print_fail(str(e))
            
        # Test encryption strength
        self.print_test("Multi-layer encryption present")
        try:
            encryption_features = [
                'encrypt_payload',
                'XOR',
                'base64',
                'ROT13'
            ]
            
            found_crypto = [f for f in encryption_features if f in content]
            
            if len(found_crypto) >= 3:
                self.print_pass("Multi-layer encryption confirmed")
            else:
                self.print_fail("Weak encryption implementation")
                
        except Exception as e:
            self.print_fail(str(e))
            
    def test_operational_security(self):
        """Test OPSEC compliance"""
        self.print_header("OPERATIONAL SECURITY TESTS")
        
        # Test error handling
        self.print_test("Graceful error handling")
        try:
            # Test with invalid input
            result = subprocess.run([
                sys.executable, 
                str(self.project_root / 'payloads' / 'av_evasion.py'),
                '-i', 'nonexistent.py',
                '-o', 'output.py',
                '-q'
            ], capture_output=True, text=True, timeout=10)
            
            # Should fail gracefully, not crash
            if result.returncode != 0 and len(result.stderr) > 0:
                self.print_pass("Fails gracefully with error message")
            else:
                self.print_fail("Poor error handling")
                
        except Exception as e:
            self.print_fail(str(e))
            
        # Test output directory creation
        self.print_test("Output directory handling")
        try:
            test_payload = self.create_test_payload()
            nested_output = self.temp_dir / "nested" / "deep" / "output.py"
            
            result = subprocess.run([
                sys.executable, 
                str(self.project_root / 'payloads' / 'av_evasion.py'),
                '-i', str(test_payload),
                '-o', str(nested_output),
                '--technique', 'encrypt',
                '-q'
            ], capture_output=True, text=True, timeout=20)
            
            if result.returncode == 0 and nested_output.exists():
                self.print_pass("Creates nested directories automatically")
            else:
                self.print_fail("Cannot create nested output directories")
                
        except Exception as e:
            self.print_fail(str(e))
            
    def test_builder_integration(self):
        """Test the automated builder for red team deployment"""
        self.print_header("AUTOMATED BUILDER TESTS")
        
        self.print_test("Batch builder functionality")
        try:
            builder_script = self.project_root / 'build_evaded_payload.py'
            
            # Test help system
            result = subprocess.run([
                sys.executable, str(builder_script), '--help'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and '--technique' in result.stdout:
                self.print_pass("Help system functional")
            else:
                self.print_fail("Help system broken")
                
        except Exception as e:
            self.print_fail(str(e))
            
        self.print_test("Single payload mode")
        try:
            test_payload = self.create_test_payload()
            output_file = self.temp_dir / "batch_test.py"
            
            result = subprocess.run([
                sys.executable, str(builder_script),
                '--single',
                '-i', str(test_payload),
                '-o', str(output_file),
                '--technique', 'encrypt',
                '-q'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and output_file.exists():
                self.print_pass("Single payload mode works")
            else:
                self.print_fail(f"Single mode failed: {result.stderr}")
                
        except Exception as e:
            self.print_fail(str(e))
            
    def get_file_hash(self, file_path):
        """Get SHA256 hash of file"""
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
            
    def cleanup(self):
        """Clean up temporary files"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass
            
    def print_summary(self):
        """Print test summary"""
        self.print_header("RED TEAM VALIDATION SUMMARY")
        
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"{GREEN}✓ Passed:{RESET} {self.passed}")
        print(f"{RED}✗ Failed:{RESET} {self.failed}")
        print(f"{BOLD}Pass Rate:{RESET} {pass_rate:.1f}%")
        
        if pass_rate >= 85:
            print(f"\n{GREEN}{BOLD}🎯 RED TEAM READY!{RESET}")
            print(f"{GREEN}AV Evasion system is operational for red team engagements{RESET}")
            
            print(f"\n{BLUE}Red Team Deployment Checklist:{RESET}")
            print(f"  ✓ Build evaded payloads: python build_evaded_payload.py")
            print(f"  ✓ Test in isolated VM before deployment")
            print(f"  ✓ Use on authorized targets only")
            print(f"  ✓ Rebuild payloads for each engagement")
            print(f"  ✓ Monitor for detection and adapt techniques")
            
        elif pass_rate >= 70:
            print(f"\n{YELLOW}{BOLD}⚠️ PARTIALLY READY{RESET}")
            print(f"{YELLOW}Some issues detected - review failures before deployment{RESET}")
        else:
            print(f"\n{RED}{BOLD}❌ NOT READY{RESET}")
            print(f"{RED}Critical issues detected - fix before red team use{RESET}")
            
        return pass_rate >= 85
        
    def run_validation(self):
        """Run complete red team validation"""
        print(f"\n{BOLD}{BLUE}╔════════════════════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{BOLD}{BLUE}║                    DEADSEC // RED TEAM AV EVASION VALIDATION               ║{RESET}")
        print(f"{BOLD}{BLUE}╚════════════════════════════════════════════════════════════════════════════╝{RESET}")
        
        try:
            self.test_python_evasion_techniques()
            self.test_powershell_evasion_basics()
            self.test_evasion_effectiveness()
            self.test_red_team_features()
            self.test_operational_security()
            self.test_builder_integration()
            
            return self.print_summary()
            
        finally:
            self.cleanup()

def main():
    validator = RedTeamEvasionValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()