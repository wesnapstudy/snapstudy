# Quick Frontend Build Test
$ErrorActionPreference = "Continue"

Write-Host "Testing Frontend Build with Minimal App..." -ForegroundColor Yellow

Set-Location frontend

# Backup original App.tsx
Write-Host "Backing up original App.tsx..." -ForegroundColor Blue
Copy-Item "src\App.tsx" "src\App.original.tsx"

# Use minimal App.tsx
Write-Host "Using minimal App component..." -ForegroundColor Blue
Copy-Item "src\App.minimal.tsx" "src\App.tsx"

# Try build
Write-Host "Testing build..." -ForegroundColor Blue
npm run build

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Build successful with minimal App!" -ForegroundColor Green
    Write-Host "The issue is with the original App component dependencies" -ForegroundColor Yellow
    
    # Restore original and try to fix dependencies
    Write-Host "Restoring original App and checking dependencies..." -ForegroundColor Blue
    Copy-Item "src\App.original.tsx" "src\App.tsx"
    
} else {
    Write-Host "✗ Build failed even with minimal App" -ForegroundColor Red
    Write-Host "The issue is with the build configuration" -ForegroundColor Yellow
    
    # Restore original
    Copy-Item "src\App.original.tsx" "src\App.tsx"
}

Set-Location ..
Write-Host "Build test completed." -ForegroundColor Yellow