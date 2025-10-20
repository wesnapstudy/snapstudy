# Test Frontend and Backend Builds
# This script tests both frontend and backend builds to identify issues

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "        Testing Frontend and Backend Builds" -ForegroundColor Cyan
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

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

# Test 1: Check Prerequisites
Write-Info "Step 1: Checking Prerequisites"

try {
    $nodeVersion = node --version
    Write-Success "Node.js: $nodeVersion"
} catch {
    Write-Error-Custom "Node.js not found. Please install from: https://nodejs.org"
    exit 1
}

try {
    $npmVersion = npm --version
    Write-Success "npm: v$npmVersion"
} catch {
    Write-Error-Custom "npm not found"
    exit 1
}

try {
    $pythonVersion = python --version
    Write-Success "Python: $pythonVersion"
} catch {
    Write-Error-Custom "Python not found"
    exit 1
}

# Test 2: Frontend Build Test
Write-Info "Step 2: Testing Frontend Build"

if (Test-Path "frontend") {
    Set-Location frontend
    
    Write-Info "Checking if node_modules exists..."
    if (-not (Test-Path "node_modules")) {
        Write-Info "Installing frontend dependencies..."
        try {
            npm install
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Frontend dependencies installed"
            } else {
                Write-Error-Custom "Frontend dependency installation failed"
                Set-Location ..
                exit 1
            }
        } catch {
            Write-Error-Custom "npm install failed: $_"
            Set-Location ..
            exit 1
        }
    } else {
        Write-Success "Frontend dependencies already installed"
    }
    
    Write-Info "Testing frontend build..."
    try {
        # Create a minimal .env file for testing
        @"
REACT_APP_AWS_REGION=us-east-1
REACT_APP_USER_POOL_ID=test-pool-id
REACT_APP_USER_POOL_CLIENT_ID=test-client-id
REACT_APP_API_URL=https://test-api-url.com
"@ | Out-File -FilePath .env.local -Encoding utf8
        
        Write-Info "Created test .env.local file"
        
        # Run build
        npm run build
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Frontend build successful!"
            
            # Check if build directory was created
            if (Test-Path "build") {
                $buildFiles = Get-ChildItem "build" -Recurse | Measure-Object
                Write-Success "Build directory created with $($buildFiles.Count) files"
            } else {
                Write-Warning-Custom "Build completed but no build directory found"
            }
        } else {
            Write-Error-Custom "Frontend build failed with exit code: $LASTEXITCODE"
            Write-Info "Check the error messages above for details"
        }
    } catch {
        Write-Error-Custom "Frontend build test failed: $_"
    }
    
    Set-Location ..
} else {
    Write-Error-Custom "Frontend directory not found"
}

# Test 3: Backend Dependencies Test
Write-Info "Step 3: Testing Backend Dependencies"

if (Test-Path "backend") {
    Set-Location backend
    
    Write-Info "Checking backend requirements..."
    if (Test-Path "requirements.txt") {
        Write-Success "requirements.txt found"
        
        # Show requirements
        Write-Info "Backend dependencies:"
        Get-Content "requirements.txt" | Where-Object { $_ -notmatch "^#" -and $_ -ne "" } | ForEach-Object {
            Write-Info "  - $_"
        }
    } else {
        Write-Error-Custom "requirements.txt not found"
        Set-Location ..
        exit 1
    }
    
    Write-Info "Testing Python dependency installation (dry run)..."
    try {
        # Test if we can resolve all dependencies
        $pipCheck = python -m pip check 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Current Python environment has no dependency conflicts"
        } else {
            Write-Warning-Custom "Python dependency issues detected: $pipCheck"
        }
    } catch {
        Write-Info "Could not check Python dependencies: $_"
    }
    
    # Test if we can import key modules
    Write-Info "Testing key Python imports..."
    try {
        $importTest = python -c "
import sys
try:
    import fastapi
    print('✅ FastAPI available')
except ImportError:
    print('❌ FastAPI not available')

try:
    import boto3
    print('✅ boto3 available')
except ImportError:
    print('❌ boto3 not available')

try:
    import pydantic
    print('✅ Pydantic available')
except ImportError:
    print('❌ Pydantic not available')
" 2>&1
        
        Write-Info "Import test results:"
        $importTest -split "`n" | ForEach-Object {
            if ($_.Trim()) {
                Write-Info "  $($_.Trim())"
            }
        }
    } catch {
        Write-Warning-Custom "Python import test failed: $_"
    }
    
    Set-Location ..
} else {
    Write-Error-Custom "Backend directory not found"
}

# Test 4: CDK Infrastructure Test
Write-Info "Step 4: Testing CDK Infrastructure"

if (Test-Path "backend/infrastructure") {
    Set-Location "backend/infrastructure"
    
    Write-Info "Checking CDK setup..."
    if (Test-Path "package.json") {
        Write-Success "CDK package.json found"
        
        Write-Info "Checking CDK dependencies..."
        if (-not (Test-Path "node_modules")) {
            Write-Info "Installing CDK dependencies..."
            try {
                npm install
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "CDK dependencies installed"
                } else {
                    Write-Error-Custom "CDK dependency installation failed"
                    Set-Location "../.."
                    exit 1
                }
            } catch {
                Write-Error-Custom "CDK npm install failed: $_"
                Set-Location "../.."
                exit 1
            }
        } else {
            Write-Success "CDK dependencies already installed"
        }
        
        Write-Info "Testing CDK synthesis..."
        try {
            # Set environment variables for CDK
            $env:AWS_REGION = "us-east-1"
            $env:AWS_ACCOUNT_ID = "054037102331"
            
            cdk synth --quiet
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "CDK synthesis successful!"
                
                # Check if cdk.out directory was created
                if (Test-Path "cdk.out") {
                    $cdkFiles = Get-ChildItem "cdk.out" | Measure-Object
                    Write-Success "CDK output directory created with $($cdkFiles.Count) files"
                } else {
                    Write-Warning-Custom "CDK synthesis completed but no output directory found"
                }
            } else {
                Write-Error-Custom "CDK synthesis failed with exit code: $LASTEXITCODE"
            }
        } catch {
            Write-Error-Custom "CDK synthesis test failed: $_"
        }
    } else {
        Write-Error-Custom "CDK package.json not found"
    }
    
    Set-Location "../.."
} else {
    Write-Error-Custom "Backend infrastructure directory not found"
}

# Summary
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Yellow
Write-Host "                        BUILD TEST SUMMARY" -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Yellow
Write-Host ""

Write-Info "Build test completed. Review the results above."
Write-Info ""
Write-Info "If all tests passed, you can run:"
Write-Info "  powershell -ExecutionPolicy Bypass -File deploy-complete.ps1"
Write-Info ""
Write-Info "If there were failures, address them before deployment:"
Write-Info "  - Frontend issues: Check Node.js version and npm dependencies"
Write-Info "  - Backend issues: Check Python version and pip dependencies"
Write-Info "  - CDK issues: Check AWS CDK installation and permissions"
Write-Host ""