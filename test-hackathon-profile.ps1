# Test Hackathon AWS Profile
# This script tests if the hackathon AWS profile is properly configured

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "        Testing Hackathon AWS Profile" -ForegroundColor Cyan
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

# Test 1: Check if hackathon profile exists
Write-Info "Checking if 'hackathon' profile exists..."

try {
    $profiles = aws configure list-profiles 2>&1
    $profilesList = $profiles -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
    
    Write-Info "Available profiles: $($profilesList -join ', ')"
    
    if ($profilesList -contains "hackathon") {
        Write-Success "Hackathon profile found"
    } else {
        Write-Error-Custom "Hackathon profile not found"
        Write-Info ""
        Write-Info "To create the hackathon profile, run:"
        Write-Info "  aws configure --profile hackathon"
        exit 1
    }
} catch {
    Write-Error-Custom "Error checking profiles: $_"
    exit 1
}

# Test 2: Test hackathon profile with explicit --profile parameter
Write-Info "Testing hackathon profile with --profile parameter..."

try {
    $identity1 = aws sts get-caller-identity --profile hackathon 2>&1
    
    if ($identity1 -match "error" -or $identity1 -match "Unable") {
        Write-Error-Custom "Profile test with --profile failed: $identity1"
    } else {
        $identityObj1 = $identity1 | ConvertFrom-Json
        Write-Success "Profile test with --profile parameter successful"
        Write-Info "Account: $($identityObj1.Account)"
        Write-Info "User: $($identityObj1.Arn)"
    }
} catch {
    Write-Error-Custom "Profile test with --profile failed: $_"
}

# Test 3: Test hackathon profile with environment variable
Write-Info "Testing hackathon profile with environment variable..."

try {
    # Set environment variable
    $env:AWS_PROFILE = "hackathon"
    
    $identity2 = aws sts get-caller-identity 2>&1
    
    if ($identity2 -match "error" -or $identity2 -match "Unable") {
        Write-Error-Custom "Profile test with env var failed: $identity2"
    } else {
        $identityObj2 = $identity2 | ConvertFrom-Json
        Write-Success "Profile test with environment variable successful"
        Write-Info "Account: $($identityObj2.Account)"
        Write-Info "User: $($identityObj2.Arn)"
    }
} catch {
    Write-Error-Custom "Profile test with environment variable failed: $_"
}

# Test 4: Check profile configuration
Write-Info "Checking hackathon profile configuration..."

try {
    $region = aws configure get region --profile hackathon
    $output = aws configure get output --profile hackathon
    
    Write-Info "Region: $($region -or 'not set')"
    Write-Info "Output: $($output -or 'not set')"
    
    if (-not $region) {
        Write-Info "Consider setting a default region:"
        Write-Info "  aws configure set region us-east-1 --profile hackathon"
    }
} catch {
    Write-Info "Could not retrieve profile configuration: $_"
}

# Test 5: Test AWS service access
Write-Info "Testing AWS service access..."

try {
    $env:AWS_PROFILE = "hackathon"
    
    # Test S3 access
    $buckets = aws s3 ls 2>&1
    if ($buckets -notmatch "error" -and $buckets -notmatch "Unable") {
        Write-Success "S3 access working"
    } else {
        Write-Info "S3 access limited: $($buckets -split "`n" | Select-Object -First 1)"
    }
    
    # Test CloudFormation access
    $stacks = aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE --max-items 1 2>&1
    if ($stacks -notmatch "error" -and $stacks -notmatch "Unable") {
        Write-Success "CloudFormation access working"
    } else {
        Write-Info "CloudFormation access limited: $($stacks -split "`n" | Select-Object -First 1)"
    }
    
} catch {
    Write-Info "Service access test failed: $_"
}

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "        Hackathon Profile Test Complete" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""

Write-Info "If all tests passed, you can run the deployment script:"
Write-Info "  .\deploy-complete.ps1"
Write-Host ""