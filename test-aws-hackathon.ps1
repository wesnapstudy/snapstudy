# Test Hackathon AWS Profile Configuration
# This script helps verify your hackathon AWS profile is set up correctly

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "        Hackathon AWS Profile Test" -ForegroundColor Cyan
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

# Step 1: Check if hackathon profile exists
Write-Info "Checking for hackathon AWS profile..."

try {
    $profiles = aws configure list-profiles 2>&1
    Write-Info "Available profiles: $($profiles -join ', ')"
    
    if ($profiles -match "hackathon") {
        Write-Success "Hackathon profile found"
    } else {
        Write-Error-Custom "Hackathon profile not found"
        Write-Host ""
        Write-Host "To create the hackathon profile:" -ForegroundColor Yellow
        Write-Host "  aws configure --profile hackathon" -ForegroundColor White
        Write-Host "  Enter your Hackathon Access Key ID" -ForegroundColor White
        Write-Host "  Enter your Hackathon Secret Access Key" -ForegroundColor White
        Write-Host "  Enter region: us-east-1" -ForegroundColor White
        Write-Host "  Enter output: json" -ForegroundColor White
        exit 1
    }
} catch {
    Write-Error-Custom "Failed to check profiles: $_"
    exit 1
}

# Step 2: Test hackathon profile credentials
Write-Info "Testing hackathon profile credentials..."

try {
    $env:AWS_PROFILE = "hackathon"
    $identity = aws sts get-caller-identity 2>&1
    
    if ($identity -match "error" -or $identity -match "Unable") {
        throw "Credential error: $identity"
    }
    
    $identityObj = $identity | ConvertFrom-Json
    
    Write-Success "Hackathon credentials are working!"
    Write-Host ""
    Write-Host "Account Details:" -ForegroundColor Cyan
    Write-Host "  Account ID: $($identityObj.Account)" -ForegroundColor White
    Write-Host "  User ARN: $($identityObj.Arn)" -ForegroundColor White
    Write-Host "  Profile: hackathon" -ForegroundColor White
    
} catch {
    Write-Error-Custom "Hackathon credentials failed: $_"
    Write-Host ""
    Write-Host "Solutions:" -ForegroundColor Yellow
    Write-Host "1. Reconfigure the hackathon profile:" -ForegroundColor White
    Write-Host "   aws configure --profile hackathon" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Or use environment variables:" -ForegroundColor White
    Write-Host "   `$env:AWS_ACCESS_KEY_ID='your_hackathon_access_key'" -ForegroundColor Gray
    Write-Host "   `$env:AWS_SECRET_ACCESS_KEY='your_hackathon_secret_key'" -ForegroundColor Gray
    Write-Host "   `$env:AWS_REGION='us-east-1'" -ForegroundColor Gray
    exit 1
}

# Step 3: Test basic AWS services access
Write-Info "Testing basic AWS services access..."

try {
    # Test S3 access
    $buckets = aws s3 ls 2>&1
    if ($buckets -notmatch "error" -and $buckets -notmatch "Unable") {
        Write-Success "S3 access confirmed"
    } else {
        Write-Info "S3 access limited (this may be normal)"
    }
    
    # Test Bedrock access
    $models = aws bedrock list-foundation-models --region us-east-1 2>&1
    if ($models -notmatch "error" -and $models -notmatch "Unable") {
        Write-Success "Bedrock access confirmed"
    } else {
        Write-Info "Bedrock access limited (may need permissions)"
    }
    
} catch {
    Write-Info "Some services may have limited access (this is normal for hackathon accounts)"
}

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "        Hackathon AWS Profile Test Complete!" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your hackathon AWS profile is configured and working." -ForegroundColor Green
Write-Host "You can now run the deployment script:" -ForegroundColor Yellow
Write-Host "  .\deploy-fixed.ps1" -ForegroundColor White
Write-Host ""