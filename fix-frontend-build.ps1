# Fix Frontend Build Issues
$ErrorActionPreference = "Continue"

Write-Host "Fixing Frontend Build Issues..." -ForegroundColor Yellow

# Navigate to frontend directory
Set-Location frontend

Write-Host "Step 1: Cleaning node_modules and package-lock..." -ForegroundColor Blue
if (Test-Path "node_modules") {
    Remove-Item -Recurse -Force node_modules
    Write-Host "✓ Removed node_modules" -ForegroundColor Green
}

if (Test-Path "package-lock.json") {
    Remove-Item package-lock.json
    Write-Host "✓ Removed package-lock.json" -ForegroundColor Green
}

Write-Host "Step 2: Installing fresh dependencies..." -ForegroundColor Blue
npm install
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Dependency installation failed" -ForegroundColor Red
    exit 1
}

Write-Host "Step 3: Checking critical files..." -ForegroundColor Blue
$criticalFiles = @(
    "src/App.tsx",
    "src/index.tsx", 
    "tsconfig.json",
    "public/index.html"
)

foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Host "✓ $file exists" -ForegroundColor Green
    } else {
        Write-Host "✗ $file missing" -ForegroundColor Red
    }
}

Write-Host "Step 4: Building frontend..." -ForegroundColor Blue
npm run build

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Frontend build successful!" -ForegroundColor Green
    Write-Host "Build files are in: build/" -ForegroundColor Green
} else {
    Write-Host "✗ Frontend build failed" -ForegroundColor Red
    Write-Host "Check the error messages above for details" -ForegroundColor Yellow
}

Set-Location ..
Write-Host "Frontend fix completed." -ForegroundColor Yellow