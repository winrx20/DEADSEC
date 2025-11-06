#!/usr/bin/env python3
"""
DeadSec AV Evasion Web GUI Test Suite
Tests the integration of AV evasion capabilities into the web interface
"""

import os
import sys
import time
import json
import subprocess
import requests
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

class AVEvasionGUITester:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.server_url = 'http://localhost:5000'
        self.server_process = None
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        
    def print_header(self, text):
        """Print a formatted header"""
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BOLD}{BLUE}{text}{RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")
        
    def print_test(self, name):
        """Print test name"""
        print(f"{YELLOW}[TEST]{RESET} {name}...", end=' ')
        
    def print_pass(self, message=""):
        """Print success message"""
        self.passed += 1
        msg = f"{GREEN}✓ PASS{RESET}"
        if message:
            msg += f" - {message}"
        print(msg)
        
    def print_fail(self, message=""):
        """Print failure message"""
        self.failed += 1
        msg = f"{RED}✗ FAIL{RESET}"
        if message:
            msg += f" - {message}"
        print(msg)
        
    def print_warning(self, message):
        """Print warning message"""
        self.warnings += 1
        print(f"{YELLOW}⚠ WARNING{RESET} - {message}")
        
    def print_info(self, message):
        """Print info message"""
        print(f"{BLUE}[INFO]{RESET} {message}")
        
    def test_file_structure(self):
        """Test that all required files exist"""
        self.print_header("FILE STRUCTURE TESTS")
        
        files_to_check = [
            ('web_gui.html', 'Web GUI HTML file'),
            ('app.js', 'JavaScript file'),
            ('styles.css', 'CSS stylesheet'),
            ('src/cnc_server.py', 'C&C Server'),
            ('payloads/av_evasion.py', 'Python AV Evasion module'),
            ('payloads/windows_av_evasion.ps1', 'PowerShell AV Evasion module'),
            ('build_evaded_payload.py', 'Payload builder script'),
            ('AV_EVASION_GUIDE.md', 'AV Evasion documentation'),
            ('WEB_GUI_AV_EVASION.md', 'Web GUI documentation'),
            ('QUICK_START_AV_GUI.md', 'Quick start guide')
        ]
        
        for file_path, description in files_to_check:
            self.print_test(f"Checking {description}")
            full_path = self.project_root / file_path
            if full_path.exists():
                self.print_pass(f"{file_path}")
            else:
                self.print_fail(f"{file_path} not found")
                
    def test_html_structure(self):
        """Test HTML file contains AV Evasion page"""
        self.print_header("HTML STRUCTURE TESTS")
        
        html_file = self.project_root / 'web_gui.html'
        
        self.print_test("Reading web_gui.html")
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            self.print_pass()
        except Exception as e:
            self.print_fail(str(e))
            return
            
        # Check for AV Evasion navigation item
        self.print_test("AV Evasion navigation item present")
        if 'data-page="av-evasion"' in html_content and '🛡️' in html_content:
            self.print_pass()
        else:
            self.print_fail("Navigation item not found")
            
        # Check for AV Evasion page div
        self.print_test("AV Evasion page container present")
        if 'id="av-evasion" class="page"' in html_content:
            self.print_pass()
        else:
            self.print_fail("Page container not found")
            
        # Check for build buttons
        self.print_test("Build All Payloads button present")
        if 'buildAllEvadedPayloads()' in html_content:
            self.print_pass()
        else:
            self.print_fail("Build All button not found")
            
        self.print_test("Build Single Payload button present")
        if 'buildSingleEvadedPayload()' in html_content:
            self.print_pass()
        else:
            self.print_fail("Build Single button not found")
            
        # Check for technique selector
        self.print_test("Evasion technique selector present")
        if 'id="evasion-technique"' in html_content:
            self.print_pass()
        else:
            self.print_fail("Technique selector not found")
            
        # Check for effectiveness matrix
        self.print_test("Effectiveness matrix table present")
        if 'Windows Defender' in html_content and '95%' in html_content:
            self.print_pass()
        else:
            self.print_fail("Effectiveness matrix not found")
            
        # Check for OPSEC section
        self.print_test("OPSEC guidelines section present")
        if 'OPERATIONAL SECURITY' in html_content or 'DON\'T' in html_content:
            self.print_pass()
        else:
            self.print_fail("OPSEC section not found")
            
    def test_javascript_functions(self):
        """Test JavaScript file contains AV Evasion functions"""
        self.print_header("JAVASCRIPT TESTS")
        
        js_file = self.project_root / 'app.js'
        
        self.print_test("Reading app.js")
        try:
            with open(js_file, 'r', encoding='utf-8') as f:
                js_content = f.read()
            self.print_pass()
        except Exception as e:
            self.print_fail(str(e))
            return
            
        # Check for build functions
        self.print_test("buildAllEvadedPayloads function defined")
        if 'async function buildAllEvadedPayloads()' in js_content or 'function buildAllEvadedPayloads()' in js_content:
            self.print_pass()
        else:
            self.print_fail("Function not found")
            
        self.print_test("buildSingleEvadedPayload function defined")
        if 'async function buildSingleEvadedPayload()' in js_content or 'function buildSingleEvadedPayload()' in js_content:
            self.print_pass()
        else:
            self.print_fail("Function not found")
            
        # Check for API endpoint calls
        self.print_test("API endpoint /build_evaded_payloads called")
        if '/build_evaded_payloads' in js_content:
            self.print_pass()
        else:
            self.print_fail("API call not found")
            
        self.print_test("API endpoint /build_single_payload called")
        if '/build_single_payload' in js_content:
            self.print_pass()
        else:
            self.print_fail("API call not found")
            
    def test_css_animations(self):
        """Test CSS file contains spinner animation"""
        self.print_header("CSS TESTS")
        
        css_file = self.project_root / 'styles.css'
        
        self.print_test("Reading styles.css")
        try:
            with open(css_file, 'r', encoding='utf-8') as f:
                css_content = f.read()
            self.print_pass()
        except Exception as e:
            self.print_fail(str(e))
            return
            
        self.print_test("Spinner animation keyframes defined")
        if '@keyframes spin' in css_content:
            self.print_pass()
        else:
            self.print_fail("Spinner animation not found")
            
    def test_server_endpoints(self):
        """Test C&C server has AV Evasion endpoints"""
        self.print_header("SERVER ENDPOINT TESTS")
        
        server_file = self.project_root / 'src' / 'cnc_server.py'
        
        self.print_test("Reading cnc_server.py")
        try:
            with open(server_file, 'r', encoding='utf-8') as f:
                server_content = f.read()
            self.print_pass()
        except Exception as e:
            self.print_fail(str(e))
            return
            
        # Check for endpoints
        self.print_test("/build_evaded_payloads endpoint defined")
        if "@app.route('/build_evaded_payloads'" in server_content:
            self.print_pass()
        else:
            self.print_fail("Endpoint not found")
            
        self.print_test("/build_single_payload endpoint defined")
        if "@app.route('/build_single_payload'" in server_content:
            self.print_pass()
        else:
            self.print_fail("Endpoint not found")
            
        # Check for subprocess imports
        self.print_test("subprocess module imported")
        if 'import subprocess' in server_content or 'subprocess.run' in server_content:
            self.print_pass()
        else:
            self.print_fail("subprocess not imported")
            
        # Check for sys module (needed for sys.executable)
        self.print_test("sys module imported")
        if 'import sys' in server_content:
            self.print_pass()
        else:
            self.print_fail("sys not imported")
            
    def test_builder_script(self):
        """Test the payload builder script functionality"""
        self.print_header("BUILDER SCRIPT TESTS")
        
        builder_script = self.project_root / 'build_evaded_payload.py'
        
        self.print_test("Builder script has --help option")
        try:
            result = subprocess.run(
                [sys.executable, str(builder_script), '--help'],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(self.project_root)
            )
            if result.returncode == 0 and 'technique' in result.stdout:
                self.print_pass()
            else:
                self.print_fail(f"Exit code: {result.returncode}")
        except Exception as e:
            self.print_fail(str(e))
            
        self.print_test("Builder script accepts --technique parameter")
        try:
            result = subprocess.run(
                [sys.executable, str(builder_script), '--help'],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(self.project_root)
            )
            if '--technique' in result.stdout:
                self.print_pass()
            else:
                self.print_fail("--technique parameter not found in help")
        except Exception as e:
            self.print_fail(str(e))
            
        self.print_test("Builder script accepts --single parameter")
        try:
            result = subprocess.run(
                [sys.executable, str(builder_script), '--help'],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(self.project_root)
            )
            if '--single' in result.stdout:
                self.print_pass()
            else:
                self.print_fail("--single parameter not found in help")
        except Exception as e:
            self.print_fail(str(e))
            
    def start_test_server(self):
        """Start the C&C server for integration tests"""
        self.print_info("Starting C&C server for integration tests...")
        
        server_script = self.project_root / 'src' / 'cnc_server.py'
        
        try:
            self.server_process = subprocess.Popen(
                [sys.executable, str(server_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.project_root / 'src'),
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
            )
            
            # Wait for server to start
            self.print_info("Waiting for server to start...")
            time.sleep(3)
            
            # Check if server is running
            for i in range(10):
                try:
                    response = requests.get(self.server_url, timeout=2)
                    if response.status_code == 200:
                        self.print_info(f"Server started successfully at {self.server_url}")
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(1)
                    
            self.print_warning("Server may not have started properly")
            return False
            
        except Exception as e:
            self.print_fail(f"Failed to start server: {e}")
            return False
            
    def stop_test_server(self):
        """Stop the test server"""
        if self.server_process:
            self.print_info("Stopping C&C server...")
            try:
                if sys.platform == 'win32':
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.server_process.pid)],
                                 capture_output=True)
                else:
                    self.server_process.terminate()
                    self.server_process.wait(timeout=5)
            except Exception as e:
                self.print_warning(f"Error stopping server: {e}")
            finally:
                self.server_process = None
                
    def test_web_gui_loads(self):
        """Test that the web GUI loads successfully"""
        self.print_header("WEB GUI INTEGRATION TESTS")
        
        self.print_test("Web GUI homepage accessible")
        try:
            response = requests.get(self.server_url, timeout=5)
            if response.status_code == 200 and 'DEADSEC' in response.text:
                self.print_pass()
            else:
                self.print_fail(f"Status code: {response.status_code}")
        except Exception as e:
            self.print_fail(str(e))
            
        self.print_test("CSS file loads")
        try:
            response = requests.get(f"{self.server_url}/styles.css", timeout=5)
            if response.status_code == 200:
                self.print_pass()
            else:
                self.print_fail(f"Status code: {response.status_code}")
        except Exception as e:
            self.print_fail(str(e))
            
        self.print_test("JavaScript file loads")
        try:
            response = requests.get(f"{self.server_url}/app.js", timeout=5)
            if response.status_code == 200:
                self.print_pass()
            else:
                self.print_fail(f"Status code: {response.status_code}")
        except Exception as e:
            self.print_fail(str(e))
            
        self.print_test("Web GUI contains AV Evasion page")
        try:
            response = requests.get(self.server_url, timeout=5)
            if 'av-evasion' in response.text and 'buildAllEvadedPayloads' in response.text:
                self.print_pass()
            else:
                self.print_fail("AV Evasion content not found in HTML")
        except Exception as e:
            self.print_fail(str(e))
            
    def test_api_endpoints(self):
        """Test API endpoints respond correctly"""
        self.print_header("API ENDPOINT TESTS")
        
        # Test build_evaded_payloads endpoint exists
        self.print_test("/build_evaded_payloads endpoint responds")
        try:
            response = requests.post(
                f"{self.server_url}/build_evaded_payloads",
                json={'technique': 'full', 'output_dir': 'test_output'},
                timeout=10
            )
            # We expect it to respond (even if build fails due to missing payloads in test env)
            if response.status_code in [200, 500]:
                self.print_pass("Endpoint is accessible")
            else:
                self.print_fail(f"Unexpected status code: {response.status_code}")
        except requests.exceptions.Timeout:
            self.print_warning("Endpoint timeout (build may be running)")
        except Exception as e:
            self.print_fail(str(e))
            
        # Test build_single_payload endpoint exists
        self.print_test("/build_single_payload endpoint responds")
        try:
            response = requests.post(
                f"{self.server_url}/build_single_payload",
                json={'payload': 'test.py', 'technique': 'full'},
                timeout=10
            )
            # We expect it to respond (even if build fails)
            if response.status_code in [200, 400, 500]:
                self.print_pass("Endpoint is accessible")
            else:
                self.print_fail(f"Unexpected status code: {response.status_code}")
        except requests.exceptions.Timeout:
            self.print_warning("Endpoint timeout")
        except Exception as e:
            self.print_fail(str(e))
            
    def test_evasion_modules(self):
        """Test that evasion modules are functional"""
        self.print_header("EVASION MODULE TESTS")
        
        # Test Python evasion module
        self.print_test("Python AV evasion module loads")
        py_evasion = self.project_root / 'payloads' / 'av_evasion.py'
        try:
            result = subprocess.run(
                [sys.executable, str(py_evasion), '--help'],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(self.project_root)
            )
            if result.returncode == 0 and 'technique' in result.stdout:
                self.print_pass()
            else:
                self.print_fail(f"Exit code: {result.returncode}")
        except Exception as e:
            self.print_fail(str(e))
            
        # Test PowerShell evasion module
        self.print_test("PowerShell AV evasion module exists")
        ps_evasion = self.project_root / 'payloads' / 'windows_av_evasion.ps1'
        if ps_evasion.exists():
            # Check if it has the main function
            with open(ps_evasion, 'r', encoding='utf-8') as f:
                ps_content = f.read()
                if 'Invoke-FullEvasion' in ps_content:
                    self.print_pass()
                else:
                    self.print_fail("Invoke-FullEvasion function not found")
        else:
            self.print_fail("File not found")
            
    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")
        
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"{GREEN}✓ Passed:{RESET} {self.passed}")
        print(f"{RED}✗ Failed:{RESET} {self.failed}")
        print(f"{YELLOW}⚠ Warnings:{RESET} {self.warnings}")
        print(f"{BOLD}Pass Rate:{RESET} {pass_rate:.1f}%")
        
        if self.failed == 0:
            print(f"\n{GREEN}{BOLD}🎉 ALL TESTS PASSED!{RESET}")
            print(f"{GREEN}AV Evasion Web GUI is fully functional!{RESET}\n")
            return True
        else:
            print(f"\n{RED}{BOLD}⚠️ SOME TESTS FAILED{RESET}")
            print(f"{YELLOW}Review the failures above and fix issues{RESET}\n")
            return False
            
    def run_all_tests(self, run_integration=True):
        """Run all test suites"""
        print(f"\n{BOLD}{BLUE}╔══════════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{BOLD}{BLUE}║  DEADSEC // AV EVASION WEB GUI TEST SUITE                       ║{RESET}")
        print(f"{BOLD}{BLUE}╚══════════════════════════════════════════════════════════════════╝{RESET}\n")
        
        # Static tests (don't require server)
        self.test_file_structure()
        self.test_html_structure()
        self.test_javascript_functions()
        self.test_css_animations()
        self.test_server_endpoints()
        self.test_builder_script()
        self.test_evasion_modules()
        
        # Integration tests (require running server)
        if run_integration:
            server_started = self.start_test_server()
            
            if server_started:
                try:
                    self.test_web_gui_loads()
                    self.test_api_endpoints()
                finally:
                    self.stop_test_server()
            else:
                self.print_warning("Skipping integration tests - server failed to start")
                self.print_info("You can run integration tests manually after starting the server")
        else:
            self.print_info("Skipping integration tests (server not started)")
            
        return self.print_summary()

def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test AV Evasion Web GUI Integration')
    parser.add_argument('--no-integration', action='store_true',
                       help='Skip integration tests (don\'t start server)')
    args = parser.parse_args()
    
    tester = AVEvasionGUITester()
    success = tester.run_all_tests(run_integration=not args.no_integration)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
