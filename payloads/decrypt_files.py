#!/usr/bin/env python3
"""
DeadSec Ransomware Decryption Tool
Use this to decrypt files after ransom payment or for recovery
FOR AUTHORIZED USE ONLY
"""

import os
import sys
import json
import argparse
from pathlib import Path
from cryptography.fernet import Fernet

class DeadSecDecryptor:
    """Decryption tool for ransomware victims"""
    
    def __init__(self, key_file):
        self.key_file = key_file
        self.victim_data = None
        self.encryption_key = None
        self.cipher = None
        
    def load_key(self):
        """Load encryption key from stored key file"""
        try:
            with open(self.key_file, 'r') as f:
                self.victim_data = json.load(f)
                self.encryption_key = self.victim_data['encryption_key']
                self.cipher = Fernet(self.encryption_key.encode())
                return True
        except FileNotFoundError:
            print(f"[!] Error: Key file not found: {self.key_file}")
            return False
        except json.JSONDecodeError:
            print(f"[!] Error: Invalid key file format")
            return False
        except Exception as e:
            print(f"[!] Error loading key: {e}")
            return False
    
    def decrypt_file(self, encrypted_file_path):
        """Decrypt a single file"""
        try:
            # Read encrypted data
            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            # Remove .deadsec extension
            original_file_path = encrypted_file_path.replace('.deadsec', '')
            
            # Write decrypted data
            with open(original_file_path, 'wb') as f:
                f.write(decrypted_data)
            
            # Remove encrypted file
            os.remove(encrypted_file_path)
            
            print(f"[+] Decrypted: {original_file_path}")
            return True
            
        except Exception as e:
            print(f"[!] Failed to decrypt {encrypted_file_path}: {e}")
            return False
    
    def decrypt_all(self):
        """Decrypt all files listed in victim data"""
        print("\n" + "="*60)
        print("  DEADSEC DECRYPTION TOOL")
        print("="*60)
        print(f"\n[*] Victim ID: {self.victim_data['victim_id']}")
        print(f"[*] Hostname: {self.victim_data['hostname']}")
        print(f"[*] Username: {self.victim_data['username']}")
        print(f"[*] Encrypted: {self.victim_data['timestamp']}")
        print(f"[*] Files to decrypt: {len(self.victim_data['encrypted_files'])}")
        print()
        
        success_count = 0
        fail_count = 0
        
        for encrypted_file in self.victim_data['encrypted_files']:
            if os.path.exists(encrypted_file):
                if self.decrypt_file(encrypted_file):
                    success_count += 1
                else:
                    fail_count += 1
            else:
                print(f"[!] File not found (may have been moved): {encrypted_file}")
                fail_count += 1
        
        print("\n" + "="*60)
        print(f"[+] Decryption Complete!")
        print(f"[+] Successfully decrypted: {success_count} files")
        if fail_count > 0:
            print(f"[!] Failed: {fail_count} files")
        print("="*60 + "\n")
        
        return success_count, fail_count
    
    def decrypt_single_file(self, file_path):
        """Decrypt a single specific file"""
        print("\n" + "="*60)
        print("  DEADSEC DECRYPTION TOOL")
        print("="*60)
        print(f"\n[*] Victim ID: {self.victim_data['victim_id']}")
        print(f"[*] Decrypting: {file_path}\n")
        
        if os.path.exists(file_path):
            success = self.decrypt_file(file_path)
            print("\n" + "="*60)
            if success:
                print("[+] Decryption successful!")
            else:
                print("[!] Decryption failed!")
            print("="*60 + "\n")
            return success
        else:
            print(f"[!] File not found: {file_path}")
            return False
    
    def restore_wallpaper(self):
        """Restore default wallpaper (Windows only)"""
        try:
            import ctypes
            # Set to default Windows 10 wallpaper
            default_wallpaper = r"C:\Windows\Web\Wallpaper\Windows\img0.jpg"
            ctypes.windll.user32.SystemParametersInfoW(20, 0, default_wallpaper, 3)
            print("[+] Wallpaper restored")
            return True
        except Exception as e:
            print(f"[!] Failed to restore wallpaper: {e}")
            return False
    
    def remove_ransom_note(self):
        """Remove ransom note from Desktop"""
        try:
            desktop = Path.home() / "Desktop"
            ransom_note = desktop / "DEADSEC_RANSOM_NOTE.txt"
            if ransom_note.exists():
                os.remove(ransom_note)
                print("[+] Ransom note removed")
                return True
            else:
                print("[*] Ransom note not found (may have been deleted)")
                return False
        except Exception as e:
            print(f"[!] Failed to remove ransom note: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description='DeadSec Ransomware Decryption Tool')
    parser.add_argument('--key', required=True, help='Path to victim key file (e.g., ransom_keys/DS-xxx.key)')
    parser.add_argument('--file', help='Decrypt single file instead of all files')
    parser.add_argument('--restore-wallpaper', action='store_true', help='Restore default wallpaper (Windows)')
    parser.add_argument('--remove-note', action='store_true', help='Remove ransom note from Desktop')
    
    args = parser.parse_args()
    
    # Initialize decryptor
    decryptor = DeadSecDecryptor(args.key)
    
    # Load encryption key
    if not decryptor.load_key():
        sys.exit(1)
    
    # Decrypt files
    if args.file:
        # Decrypt single file
        success = decryptor.decrypt_single_file(args.file)
        sys.exit(0 if success else 1)
    else:
        # Decrypt all files
        success_count, fail_count = decryptor.decrypt_all()
        
        # Optional: Restore wallpaper
        if args.restore_wallpaper:
            print("\n[*] Restoring wallpaper...")
            decryptor.restore_wallpaper()
        
        # Optional: Remove ransom note
        if args.remove_note:
            print("\n[*] Removing ransom note...")
            decryptor.remove_ransom_note()
        
        sys.exit(0 if fail_count == 0 else 1)


if __name__ == "__main__":
    main()
