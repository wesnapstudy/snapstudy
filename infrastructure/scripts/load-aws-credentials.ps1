# Load AWS Credentials Script
# This script loads AWS credentials from environment variables first,
# then falls back to .env file if not found

param(
    [switch]$Verbose
)

function Write-Info {
    param($message)
    if ($Verbose) {
        Write-Host "[INFO] $message" -ForegroundColor Blue
    }
}

function Write-Success {
    param($message)
    Write-Host "[SUCCESS] $message" -ForegroundColor Green
}

function Write-Warning {
    param($message)
    Write-Host "[WARNING] $message" -ForegroundColor Yellow
}

function Write-Error {
    param($message)
    Write-Host "[ERROR] $message" -ForegroundColor Red
}

function Load-EnvFile {
    param($filePath)
    
    if (Test-Path $filePath) {
        Write-Info "Loading environment variables from $filePath"
        
        Get-Content $filePath | ForEach-Object {
            if ($_ -match '^([^#][^=]+)=(.*)$') {
                $name = $matches[1].Trim()
                $value = $matches[2].Trim()
                
                # Remove quotes if present
                if ($value -match '^"(.*)"$' -or $value -match "^'(.*)'$") {
                    $value = $matches[1]
                }
                
                # Only set if not already in environment
                if (-not [System.Environment]::GetEnvironmentVariable($name)) {
                    [System.Environment]::SetEnvironmentVariable($name, $value, "Process")
                    Write-Info "Set $name from .env file"
                }
            }
        }
    } else {
        Write-Warning ".env file not found at $filePath"
    }
}

function Test-AwsCredentials {
    Write-Info "Testing AWS credentials..."
    
    try {
        # Clear any profile settings to use environment variables
        $env:AWS_PROFILE = $null
        $identity = aws sts get-caller-identity 2>$null | ConvertFrom-Json
        if ($identity) {
            Write-Success "AWS credentials are valid"
            Write-Info "Account ID: $($identity.Account)"
            Write-Info "User ARN: $($identity.Arn)"
            return $true
        }
    } catch {
        Write-Warning "AWS credentials test failed: $($_.ToString())"
        Write-Warning "AWS credentials test failed: $_"
        return $false
    }
    
    return $false
}

# Main execution
Write-Info "Loading AWS credentials..."

# Step 1: Check if credentials are already in environment variables
$hasEnvCredentials = $false
if ($env:AWS_ACCESS_KEY_ID -and $env:AWS_SECRET_ACCESS_KEY) {
    Write-Success "AWS credentials found in environment variables"
    $hasEnvCredentials = $true
} else {
    Write-Info "AWS credentials not found in environment variables"
}

# Step 2: Load from .env file if not in environment
if (-not $hasEnvCredentials) {
    Write-Info "Attempting to load credentials from .env file..."
    Load-EnvFile ".env"
    
    # Check if credentials are now available
    if ($env:AWS_ACCESS_KEY_ID -and $env:AWS_SECRET_ACCESS_KEY) {
        Write-Success "AWS credentials loaded from .env file"
        $hasEnvCredentials = $true
    } else {
        Write-Warning "AWS credentials not found in .env file"
    }
}

# Step 3: Check if credentials are now available after loading from .env
if (-not $hasEnvCredentials) {
    Write-Info "Checking if credentials are now available..."
    if ($env:AWS_ACCESS_KEY_ID -and $env:AWS_SECRET_ACCESS_KEY) {
        Write-Success "AWS credentials are now available"
        $hasEnvCredentials = $true
    } else {
        Write-Info "No AWS credentials found in environment or .env file"
    }
}

# Step 4: Test credentials
if ($hasEnvCredentials) {
    if (Test-AwsCredentials) {
        Write-Success "AWS credentials are configured and valid"
        
        # Display current configuration
        Write-Host ""
        Write-Host "Current AWS Configuration:" -ForegroundColor Cyan
        Write-Host "=========================" -ForegroundColor Cyan
        
        if ($env:AWS_REGION) {
            Write-Host "Region: $env:AWS_REGION" -ForegroundColor Gray
        }
        if ($env:AWS_ACCOUNT_ID) {
            Write-Host "Account ID: $env:AWS_ACCOUNT_ID" -ForegroundColor Gray
        }
        if ($env:ENVIRONMENT) {
            Write-Host "Environment: $env:ENVIRONMENT" -ForegroundColor Gray
        }
        
        exit 0
    } else {
        Write-Warning "AWS credentials are configured but may be invalid or expired"
        Write-Info "Credentials are loaded from .env file but AWS validation failed"
        Write-Info "This may be due to expired credentials or network issues"
        exit 0  # Don't fail completely, let deployment proceed
    }
} else {
    Write-Error "No valid AWS credentials found"
    Write-Host ""
    Write-Host "To configure AWS credentials, you can:" -ForegroundColor Yellow
    Write-Host "1. Set environment variables:" -ForegroundColor Yellow
    Write-Host "   - AWS_ACCESS_KEY_ID" -ForegroundColor Gray
    Write-Host "   - AWS_SECRET_ACCESS_KEY" -ForegroundColor Gray
    Write-Host "   - AWS_REGION (optional)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Update .env file with your credentials" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "3. Run 'aws configure' to set up AWS CLI" -ForegroundColor Yellow
    
    exit 1
}