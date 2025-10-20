# PowerShell script to install Python and generate architecture diagrams
# Run as Administrator for best results

Write-Host "🐍 Installing Python via PowerShell..." -ForegroundColor Green

# Method 1: Try to install via winget (Windows Package Manager)
Write-Host "Attempting to install Python via winget..." -ForegroundColor Yellow
try {
    winget install Python.Python.3.12
    Write-Host "✅ Python installed via winget" -ForegroundColor Green
} catch {
    Write-Host "⚠️ winget not available or failed, trying alternative method..." -ForegroundColor Yellow
    
    # Method 2: Download and install Python manually
    Write-Host "Downloading Python installer..." -ForegroundColor Yellow
    
    $pythonUrl = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
    $installerPath = "$env:TEMP\python-installer.exe"
    
    # Download Python installer
    Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath
    
    Write-Host "Installing Python..." -ForegroundColor Yellow
    # Install Python with PATH addition
    Start-Process -FilePath $installerPath -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_test=0" -Wait
    
    Write-Host "✅ Python installation completed" -ForegroundColor Green
    
    # Clean up installer
    Remove-Item $installerPath -Force
}

# Refresh environment variables
Write-Host "Refreshing environment variables..." -ForegroundColor Yellow
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Wait a moment for installation to complete
Start-Sleep -Seconds 5

# Verify Python installation
Write-Host "Verifying Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python installed: $pythonVersion" -ForegroundColor Green
} catch {
    try {
        $pythonVersion = py --version 2>&1
        Write-Host "✅ Python installed: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Python installation verification failed" -ForegroundColor Red
        Write-Host "Please restart PowerShell and try again" -ForegroundColor Yellow
        exit 1
    }
}

# Install required packages
Write-Host "📦 Installing required Python packages..." -ForegroundColor Green

try {
    python -m pip install --upgrade pip
    Write-Host "✅ pip upgraded" -ForegroundColor Green
} catch {
    py -m pip install --upgrade pip
    Write-Host "✅ pip upgraded" -ForegroundColor Green
}

try {
    python -m pip install diagrams
    Write-Host "✅ diagrams package installed" -ForegroundColor Green
} catch {
    py -m pip install diagrams
    Write-Host "✅ diagrams package installed" -ForegroundColor Green
}

# Try to install graphviz (optional but recommended)
Write-Host "Installing Graphviz (optional)..." -ForegroundColor Yellow
try {
    winget install graphviz
    Write-Host "✅ Graphviz installed" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Graphviz installation failed - diagrams may still work" -ForegroundColor Yellow
}

Write-Host "🎨 Generating SnapStudy AWS Architecture Diagrams..." -ForegroundColor Green

# Generate architecture diagrams
try {
    python create_architecture_diagram.py
    Write-Host "✅ Architecture diagrams generated successfully!" -ForegroundColor Green
    Write-Host "Check for these files:" -ForegroundColor Cyan
    Write-Host "- snapstudy_architecture.png" -ForegroundColor Cyan
    Write-Host "- snapstudy_data_flow.png" -ForegroundColor Cyan
} catch {
    try {
        py create_architecture_diagram.py
        Write-Host "✅ Architecture diagrams generated successfully!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to generate diagrams" -ForegroundColor Red
        Write-Host "You may need to restart PowerShell and run the script again" -ForegroundColor Yellow
    }
}

Write-Host "🎉 Installation and setup complete!" -ForegroundColor Green
Write-Host "If diagrams were not generated, try running: python create_architecture_diagram.py" -ForegroundColor Yellow