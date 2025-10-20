# Fix Hackathon AWS Credentials
# This script helps update the hackathon AWS profile with valid credentials

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "        Fix Hackathon AWS Profile Credentials" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check current profile status
Write-Info "Checking current hackathon profile status..."

try {
    aws configure list --profile hackathon
    Write-Info "Profile exists, checking if credentials work..."
    
    $testResult = aws sts get-caller-identity --profile hackathon 2>&1
    
    if ($testResult -match "InvalidClientTokenId") {
        Write-Error-Custom "Current credentials are invalid or expired"
    } elseif ($testResult -match "error") {
        Write-Error-Custom "Credentials error: $testResult"
    } else {
        Write-Success "Current credentials are working!"
        Write-Info "If credentials are working, you can run: .\deploy-complete.ps1"
        exit 0
    }
} catch {
    Write-Info "Profile may not exist or has issues"
}

Write-Host ""
Write-Info "The hackathon profile needs to be configured with valid credentials."
Write-Info "You'll need:"
Write-Info "  - Your Hackathon AWS Access Key ID"
Write-Info "  - Your Hackathon AWS Secret Access Key"
Write-Host ""

$continue = Read-Host "Do you want to configure the hackathon profile now? (y/n)"

if ($continue -ne "y" -and $continue -ne "Y") {
    Write-Info "Configuration cancelled. Please configure manually:"
    Write-Info "  aws configure --profile hackathon"
    exit 0
}

Write-Host ""
Write-Info "Configuring hackathon AWS profile..."
Write-Info "Please enter your hackathon AWS credentials when prompted."
Write-Host ""

try {
    # Run AWS configure for hackathon profile
    aws configure --profile hackathon
    
    Write-Host ""
    Write-Info "Testing the updated credentials..."
    
    $testResult = aws sts get-caller-identity --profile hackathon 2>&1
    
    if ($testResult -match "InvalidClientTokenId") {
        Write-Error-Custom "The credentials you entered are still invalid"
        Write-Info "Please double-check your Access Key ID and Secret Access Key"
        Write-Info "Make sure they are for the hackathon AWS account"
    } elseif ($testResult -match "error") {
        Write-Error-Custom "Credentials test failed: $testResult"
    } else {
        try {
            $identity = $testResult | ConvertFrom-Json
            Write-Success "Credentials are working!"
            Write-Success "Account: $($identity.Account)"
            Write-Success "User: $($identity.Arn)"
            Write-Host ""
            Write-Host "=====================================================================" -ForegroundColor Green
            Write-Host "        Hackathon Profile Successfully Configured!" -ForegroundColor Green
            Write-Host "=====================================================================" -ForegroundColor Green
            Write-Host ""
            Write-Info "You can now run the deployment script:"
            Write-Info "  .\deploy-complete.ps1"
        } catch {
            Write-Success "Credentials appear to be working (JSON parsing issue)"
            Write-Info "You can try running the deployment script:"
            Write-Info "  .\deploy-complete.ps1"
        }
    }
    
} catch {
    Write-Error-Custom "Configuration failed: $_"
    Write-Info ""
    Write-Info "Please try configuring manually:"
    Write-Info "  aws configure --profile hackathon"
}

Write-Host ""