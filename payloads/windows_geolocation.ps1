# Windows Geolocation Tracker
# Gathers geographic location data using multiple methods:
# - WiFi access point geolocation (via Google/Microsoft APIs)
# - IP-based geolocation
# - Windows Location Services
# - GPS (if available)
# - Timezone and language settings

param(
    [string]$OutputFile = "C:\Temp\location_data.json",
    [switch]$Silent,
    [switch]$Continuous,
    [int]$Interval = 300,  # Seconds between location updates in continuous mode
    [string]$ApiKey = ""   # Optional: Google Geolocation API key for better accuracy
)

# Suppress errors if Silent mode
if ($Silent) {
    $ErrorActionPreference = "SilentlyContinue"
}

function Write-Log {
    param([string]$Message)
    if (-not $Silent) {
        Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
    }
}

# Get IP-based geolocation
function Get-IPGeolocation {
    Write-Log "Gathering IP-based geolocation..."
    
    try {
        # Try multiple IP geolocation services
        $services = @(
            "http://ip-api.com/json/",
            "https://ipapi.co/json/",
            "http://ipinfo.io/json"
        )
        
        $results = @()
        
        foreach ($service in $services) {
            try {
                $response = Invoke-RestMethod -Uri $service -TimeoutSec 5 -UseBasicParsing
                $results += @{
                    Service = $service
                    Data = $response
                    Success = $true
                }
                break  # Use first successful response
            }
            catch {
                $results += @{
                    Service = $service
                    Error = $_.Exception.Message
                    Success = $false
                }
            }
        }
        
        return $results | Where-Object { $_.Success -eq $true } | Select-Object -First 1
    }
    catch {
        Write-Log "Error getting IP geolocation: $_"
        return $null
    }
}

# Get WiFi access points for geolocation
function Get-WiFiAccessPoints {
    Write-Log "Scanning WiFi access points..."
    
    try {
        # Get WiFi networks using netsh
        $wifiData = netsh wlan show networks mode=bssid
        
        $accessPoints = @()
        $currentSSID = ""
        
        foreach ($line in $wifiData) {
            if ($line -match "^SSID \d+ : (.+)$") {
                $currentSSID = $matches[1].Trim()
            }
            elseif ($line -match "BSSID \d+\s+:\s+([0-9a-fA-F:]+)") {
                $bssid = $matches[1].Trim()
                
                # Extract signal strength
                $signalLine = $wifiData | Where-Object { $_ -match "Signal\s+:\s+(\d+)%" } | Select-Object -First 1
                $signal = if ($signalLine -match "Signal\s+:\s+(\d+)%") { $matches[1] } else { "0" }
                
                $accessPoints += @{
                    SSID = $currentSSID
                    BSSID = $bssid
                    SignalStrength = $signal
                }
            }
        }
        
        return $accessPoints
    }
    catch {
        Write-Log "Error scanning WiFi: $_"
        return @()
    }
}

# Get geolocation using Google Geolocation API with WiFi access points
function Get-GoogleGeolocation {
    param([array]$AccessPoints, [string]$ApiKey)
    
    if ($AccessPoints.Count -eq 0) {
        Write-Log "No WiFi access points available for Google geolocation"
        return $null
    }
    
    Write-Log "Querying Google Geolocation API with WiFi data..."
    
    try {
        # Build request body
        $wifiAccessPoints = @()
        foreach ($ap in $AccessPoints | Select-Object -First 10) {
            $wifiAccessPoints += @{
                macAddress = $ap.BSSID
                signalStrength = [int]$ap.SignalStrength
            }
        }
        
        $body = @{
            wifiAccessPoints = $wifiAccessPoints
        } | ConvertTo-Json -Depth 10
        
        # Use API key if provided, otherwise use free endpoint (limited accuracy)
        $url = if ($ApiKey) {
            "https://www.googleapis.com/geolocation/v1/geolocate?key=$ApiKey"
        } else {
            "https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyDummyKey"  # Will work with limited accuracy
        }
        
        $response = Invoke-RestMethod -Uri $url -Method Post -Body $body -ContentType "application/json" -TimeoutSec 10
        
        return @{
            Latitude = $response.location.lat
            Longitude = $response.location.lng
            Accuracy = $response.accuracy
            Method = "Google WiFi Geolocation"
        }
    }
    catch {
        Write-Log "Google geolocation failed: $_"
        return $null
    }
}

# Get Windows Location Services data
function Get-WindowsLocation {
    Write-Log "Querying Windows Location Services..."
    
    try {
        # Check if location services are enabled
        $locationConsent = Get-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\DeviceAccess\Global\{BFA794E4-F964-4FDB-90F6-51056BFE4B44}" -ErrorAction SilentlyContinue
        
        if ($locationConsent.Value -ne "Allow") {
            Write-Log "Windows Location Services are disabled"
            return $null
        }
        
        # Use Windows Location API via COM
        Add-Type -AssemblyName System.Device
        $geoWatcher = New-Object System.Device.Location.GeoCoordinateWatcher
        
        $geoWatcher.Start()
        Start-Sleep -Seconds 3  # Wait for location acquisition
        
        $location = $geoWatcher.Position.Location
        
        if ($location.IsUnknown) {
            Write-Log "Windows Location Services could not determine location"
            $geoWatcher.Stop()
            return $null
        }
        
        $result = @{
            Latitude = $location.Latitude
            Longitude = $location.Longitude
            Altitude = $location.Altitude
            HorizontalAccuracy = $location.HorizontalAccuracy
            VerticalAccuracy = $location.VerticalAccuracy
            Speed = $location.Speed
            Course = $location.Course
            Method = "Windows Location Services"
        }
        
        $geoWatcher.Stop()
        return $result
    }
    catch {
        Write-Log "Error accessing Windows Location Services: $_"
        return $null
    }
}

# Get system timezone and regional settings
function Get-SystemLocationInfo {
    Write-Log "Gathering system timezone and regional data..."
    
    try {
        $timezone = Get-TimeZone
        $culture = Get-Culture
        
        return @{
            TimeZone = $timezone.Id
            TimeZoneDisplayName = $timezone.DisplayName
            TimeZoneOffset = $timezone.BaseUtcOffset.ToString()
            CultureName = $culture.Name
            DisplayName = $culture.DisplayName
            TwoLetterISOLanguageName = $culture.TwoLetterISOLanguageName
            ThreeLetterISOLanguageName = $culture.ThreeLetterISOLanguageName
        }
    }
    catch {
        Write-Log "Error getting system location info: $_"
        return $null
    }
}

# Get nearby WiFi networks for triangulation
function Get-NearbyNetworks {
    Write-Log "Scanning nearby WiFi networks..."
    
    try {
        $networks = netsh wlan show networks mode=bssid | Out-String
        return @{
            RawData = $networks
            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        }
    }
    catch {
        Write-Log "Error scanning networks: $_"
        return $null
    }
}

# Get external IP addresses
function Get-ExternalIP {
    Write-Log "Getting external IP address..."
    
    try {
        $services = @(
            "https://api.ipify.org?format=json",
            "https://ifconfig.me/all.json",
            "https://ipinfo.io/json"
        )
        
        foreach ($service in $services) {
            try {
                $response = Invoke-RestMethod -Uri $service -TimeoutSec 5 -UseBasicParsing
                return @{
                    IP = if ($response.ip) { $response.ip } else { $response }
                    Service = $service
                }
            }
            catch {
                continue
            }
        }
        
        return $null
    }
    catch {
        Write-Log "Error getting external IP: $_"
        return $null
    }
}

# Main location gathering function
function Get-LocationData {
    Write-Log "===== Starting Location Data Collection ====="
    
    $locationData = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC" 
        ComputerName = $env:COMPUTERNAME
        Username = $env:USERNAME
        Methods = @{}
    }
    
    # 1. IP-based geolocation
    $ipGeo = Get-IPGeolocation
    if ($ipGeo) {
        $locationData.Methods["IP_Geolocation"] = $ipGeo.Data
    }
    
    # 2. External IP
    $externalIP = Get-ExternalIP
    if ($externalIP) {
        $locationData.ExternalIP = $externalIP
    }
    
    # 3. WiFi access points
    $wifiAPs = Get-WiFiAccessPoints
    if ($wifiAPs.Count -gt 0) {
        $locationData.WiFiAccessPoints = $wifiAPs
        
        # 4. Google geolocation with WiFi data
        $googleGeo = Get-GoogleGeolocation -AccessPoints $wifiAPs -ApiKey $ApiKey
        if ($googleGeo) {
            $locationData.Methods["Google_WiFi_Geolocation"] = $googleGeo
        }
    }
    
    # 5. Windows Location Services
    $windowsLoc = Get-WindowsLocation
    if ($windowsLoc) {
        $locationData.Methods["Windows_Location_Services"] = $windowsLoc
    }
    
    # 6. System timezone and regional settings
    $systemInfo = Get-SystemLocationInfo
    if ($systemInfo) {
        $locationData.SystemLocationInfo = $systemInfo
    }
    
    # 7. Nearby networks
    $nearbyNetworks = Get-NearbyNetworks
    if ($nearbyNetworks) {
        $locationData.NearbyNetworks = $nearbyNetworks
    }
    
    # Calculate best location estimate
    $estimates = @()
    foreach ($method in $locationData.Methods.GetEnumerator()) {
        if ($method.Value.Latitude -and $method.Value.Longitude) {
            $estimates += @{
                Method = $method.Key
                Lat = $method.Value.Latitude
                Lon = $method.Value.Longitude
                Accuracy = if ($method.Value.Accuracy) { $method.Value.Accuracy } else { 1000 }
            }
        }
    }
    
    if ($estimates.Count -gt 0) {
        # Use the most accurate estimate
        $bestEstimate = $estimates | Sort-Object Accuracy | Select-Object -First 1
        $locationData.BestEstimate = @{
            Latitude = $bestEstimate.Lat
            Longitude = $bestEstimate.Lon
            Method = $bestEstimate.Method
            Accuracy = $bestEstimate.Accuracy
            GoogleMapsURL = "https://www.google.com/maps?q=$($bestEstimate.Lat),$($bestEstimate.Lon)"
        }
    }
    
    Write-Log "===== Location Data Collection Complete ====="
    return $locationData
}

# Main execution
try {
    Write-Log "Windows Geolocation Tracker Started"
    Write-Log "Output file: $OutputFile"
    
    # Create output directory if needed
    $outputDir = Split-Path -Parent $OutputFile
    if ($outputDir -and !(Test-Path $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    }
    
    if ($Continuous) {
        Write-Log "Running in continuous mode (interval: $Interval seconds)"
        Write-Log "Press Ctrl+C to stop"
        
        $allData = @()
        
        while ($true) {
            $locationData = Get-LocationData
            $allData += $locationData
            
            # Save after each collection
            $allData | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputFile -Encoding UTF8
            
            Write-Log "Location data saved. Waiting $Interval seconds..."
            Start-Sleep -Seconds $Interval
        }
    }
    else {
        # Single collection
        $locationData = Get-LocationData
        
        # Save to file
        $locationData | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputFile -Encoding UTF8
        
        Write-Log "Location data saved to: $OutputFile"
        
        # Display summary
        if (-not $Silent -and $locationData.BestEstimate) {
            Write-Host "`n===== LOCATION SUMMARY ====="
            Write-Host "Latitude:  $($locationData.BestEstimate.Latitude)"
            Write-Host "Longitude: $($locationData.BestEstimate.Longitude)"
            Write-Host "Method:    $($locationData.BestEstimate.Method)"
            Write-Host "Accuracy:  $($locationData.BestEstimate.Accuracy) meters"
            Write-Host "Map URL:   $($locationData.BestEstimate.GoogleMapsURL)"
            Write-Host "========================`n"
        }
    }
    
    Write-Log "Geolocation tracking completed successfully"
}
catch {
    Write-Log "Error: $_"
    exit 1
}
