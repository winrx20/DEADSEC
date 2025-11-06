<#
.SYNOPSIS
    DeadSec Ransomware Decryption Tool
    
.DESCRIPTION
    Use this to decrypt files after ransom payment or for recovery
    FOR AUTHORIZED USE ONLY
    
.PARAMETER KeyFile
    Path to victim key file (JSON format with encryption key)
    
.PARAMETER SingleFile
    Path to single file to decrypt (optional)
    
.PARAMETER RestoreWallpaper
    Restore default Windows wallpaper
    
.PARAMETER RemoveNote
    Remove ransom note from Desktop
    
.EXAMPLE
    .\decrypt_files.ps1 -KeyFile "ransom_keys\DS-809c627c-I5GXRTZCM2G8.key"
    
.EXAMPLE
    .\decrypt_files.ps1 -KeyFile "ransom_keys\DS-xxx.key" -SingleFile "C:\Users\victim\Documents\file.docx.deadsec"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$KeyFile,
    
    [Parameter(Mandatory=$false)]
    [string]$SingleFile,
    
    [switch]$RestoreWallpaper,
    [switch]$RemoveNote
)

Add-Type -AssemblyName System.Security

function Load-EncryptionKey {
    param([string]$KeyFilePath)
    
    try {
        if (-not (Test-Path $KeyFilePath)) {
            Write-Host "[!] Error: Key file not found: $KeyFilePath" -ForegroundColor Red
            return $null
        }
        
        $victimData = Get-Content $KeyFilePath -Raw | ConvertFrom-Json
        return $victimData
    }
    catch {
        Write-Host "[!] Error loading key file: $_" -ForegroundColor Red
        return $null
    }
}

function Decrypt-File {
    param(
        [string]$EncryptedFilePath,
        [string]$EncryptionKey
    )
    
    try {
        # Read encrypted data
        $encryptedData = [System.IO.File]::ReadAllBytes($EncryptedFilePath)
        
        # Decode base64 key
        $keyBytes = [System.Convert]::FromBase64String($EncryptionKey)
        
        # Create AES decryptor
        $aes = [System.Security.Cryptography.Aes]::Create()
        $aes.Key = $keyBytes
        $aes.Mode = [System.Security.Cryptography.CipherMode]::CBC
        $aes.Padding = [System.Security.Cryptography.PaddingMode]::PKCS7
        
        # Extract IV from first 16 bytes
        $iv = $encryptedData[0..15]
        $aes.IV = $iv
        $ciphertext = $encryptedData[16..($encryptedData.Length-1)]
        
        # Decrypt
        $decryptor = $aes.CreateDecryptor()
        $decryptedData = $decryptor.TransformFinalBlock($ciphertext, 0, $ciphertext.Length)
        
        # Get original filename
        $originalFile = $EncryptedFilePath -replace '\.deadsec$', ''
        
        # Write decrypted data
        [System.IO.File]::WriteAllBytes($originalFile, $decryptedData)
        
        # Remove encrypted file
        Remove-Item $EncryptedFilePath -Force
        
        Write-Host "[+] Decrypted: $originalFile" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "[!] Failed to decrypt ${EncryptedFilePath}: $_" -ForegroundColor Red
        return $false
    }
}

function Restore-DefaultWallpaper {
    try {
        $defaultWallpaper = "C:\Windows\Web\Wallpaper\Windows\img0.jpg"
        
        Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Wallpaper {
    [DllImport("user32.dll", CharSet = CharSet.Auto)]
    public static extern int SystemParametersInfo(int uAction, int uParam, string lpvParam, int fuWinIni);
}
"@
        
        [Wallpaper]::SystemParametersInfo(0x0014, 0, $defaultWallpaper, 0x0003)
        Write-Host "[+] Wallpaper restored" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "[!] Failed to restore wallpaper: $_" -ForegroundColor Yellow
        return $false
    }
}

function Remove-RansomNote {
    try {
        $desktop = [Environment]::GetFolderPath("Desktop")
        $ransomNote = Join-Path $desktop "DEADSEC_RANSOM_NOTE.txt"
        
        if (Test-Path $ransomNote) {
            Remove-Item $ransomNote -Force
            Write-Host "[+] Ransom note removed" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "[*] Ransom note not found (may have been deleted)" -ForegroundColor Yellow
            return $false
        }
    }
    catch {
        Write-Host "[!] Failed to remove ransom note: $_" -ForegroundColor Yellow
        return $false
    }
}

# Main execution
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  DEADSEC DECRYPTION TOOL" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Load victim data and key
$victimData = Load-EncryptionKey -KeyFilePath $KeyFile
if ($null -eq $victimData) {
    exit 1
}

Write-Host "[*] Victim ID: $($victimData.victim_id)"
Write-Host "[*] Hostname: $($victimData.hostname)"
Write-Host "[*] Username: $($victimData.username)"
Write-Host "[*] Encrypted: $($victimData.timestamp)"
Write-Host ""

$encryptionKey = $victimData.encryption_key

# Decrypt files
if ($SingleFile) {
    # Decrypt single file
    Write-Host "[*] Decrypting: $SingleFile"
    Write-Host ""
    
    if (Test-Path $SingleFile) {
        $success = Decrypt-File -EncryptedFilePath $SingleFile -EncryptionKey $encryptionKey
        Write-Host ""
        Write-Host "============================================================" -ForegroundColor Cyan
        if ($success) {
            Write-Host "[+] Decryption successful!" -ForegroundColor Green
        }
        else {
            Write-Host "[!] Decryption failed!" -ForegroundColor Red
        }
        Write-Host "============================================================" -ForegroundColor Cyan
        exit $(if ($success) { 0 } else { 1 })
    }
    else {
        Write-Host "[!] File not found: $SingleFile" -ForegroundColor Red
        exit 1
    }
}
else {
    # Decrypt all files
    Write-Host "[*] Files to decrypt: $($victimData.encrypted_files.Count)"
    Write-Host ""
    
    $successCount = 0
    $failCount = 0
    
    foreach ($encryptedFile in $victimData.encrypted_files) {
        if (Test-Path $encryptedFile) {
            if (Decrypt-File -EncryptedFilePath $encryptedFile -EncryptionKey $encryptionKey) {
                $successCount++
            }
            else {
                $failCount++
            }
        }
        else {
            Write-Host "[!] File not found (may have been moved): $encryptedFile" -ForegroundColor Yellow
            $failCount++
        }
    }
    
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "[+] Decryption Complete!" -ForegroundColor Green
    Write-Host "[+] Successfully decrypted: $successCount files" -ForegroundColor Green
    if ($failCount -gt 0) {
        Write-Host "[!] Failed: $failCount files" -ForegroundColor Yellow
    }
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Optional: Restore wallpaper
    if ($RestoreWallpaper) {
        Write-Host "[*] Restoring wallpaper..."
        Restore-DefaultWallpaper
        Write-Host ""
    }
    
    # Optional: Remove ransom note
    if ($RemoveNote) {
        Write-Host "[*] Removing ransom note..."
        Remove-RansomNote
        Write-Host ""
    }
    
    exit $(if ($failCount -eq 0) { 0 } else { 1 })
}
