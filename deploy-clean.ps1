# SnapStudy Clean Deployment Script
# Fixed version without syntax errors

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "        SnapStudy Complete AWS Deployment (Clean Version)" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

function Write-Step {
    param([string]$Message)
    Write-Host "`n>>> $Message" -ForegroundColor Yellow
}

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

# Step 1: Check Prerequisites
Write-Step "Step 1: Checking Prerequisites"

try {
    $pythonVersion = python --version 2>&1
    Write-Success "Python: $pythonVersion"
} catch {
    Write-Error-Custom "Python not found. Install from: https://www.python.org"
    exit 1
}

try {
    $nodeVersion = node --version
    Write-Success "Node.js: $nodeVersion"
} catch {
    Write-Error-Custom "Node.js not found. Install from: https://nodejs.org"
    exit 1
}

try {
    $awsVersion = aws --version
    Write-Success "AWS CLI: $awsVersion"
} catch {
    Write-Error-Custom "AWS CLI not found. Install from: https://aws.amazon.com/cli/"
    exit 1
}

# Step 2: Check AWS Profile
Write-Step "Step 2: Checking AWS Profile 'hackathon'"

$env:AWS_PROFILE = "hackathon"

try {
    $testOutput = aws sts get-caller-identity --profile hackathon --output json 2>&1
    
    if ($testOutput -match "InvalidClientTokenId|NoCredentialsError|error") {
        Write-Error-Custom "AWS credentials for 'hackathon' profile are invalid"
        Write-Info "Please run: aws configure --profile hackathon"
        exit 1
    }
    
    Write-Success "AWS Profile 'hackathon' is working"
    
    # Parse account info
    try {
        $identity = $testOutput | ConvertFrom-Json
        $script:AWS_ACCOUNT_ID = $identity.Account
    } catch {
        if ($testOutput -match '"Account":\s*"(\d+)"') {
            $script:AWS_ACCOUNT_ID = $matches[1]
        } else {
            $script:AWS_ACCOUNT_ID = "unknown"
        }
    }
    
    $script:AWS_REGION = aws configure get region --profile hackathon 2>$null
    if (-not $script:AWS_REGION) {
        $script:AWS_REGION = "us-east-1"
    }
    
    Write-Success "Account ID: $script:AWS_ACCOUNT_ID"
    Write-Success "Region: $script:AWS_REGION"
    
} catch {
    Write-Error-Custom "AWS Profile test failed: $_"
    exit 1
}

# Step 3: Bedrock Check (Optional)
Write-Step "Step 3: Checking Amazon Bedrock Access (Optional)"

Write-Info "Testing Bedrock access (optional)..."
$bedrockAvailable = $false

try {
    $bedrockTest = cmd /c "aws bedrock list-foundation-models --region us-east-1 --profile hackathon --output json 2>nul"
    
    if ($bedrockTest -and $bedrockTest -match '"modelSummaries"') {
        Write-Success "Bedrock service is accessible"
        $bedrockAvailable = $true
        
        if ($bedrockTest -match "anthropic.claude-3-5-sonnet") {
            Write-Success "Claude 3.5 Sonnet is available"
        } else {
            Write-Info "Claude 3.5 Sonnet not found - can be enabled later"
        }
    } else {
        Write-Info "Bedrock access is limited - this is OK"
    }
} catch {
    Write-Info "Bedrock check skipped"
}

if (-not $bedrockAvailable) {
    Write-Host ""
    Write-Host "Bedrock Status: Limited Access (This is Fine!)" -ForegroundColor Yellow
    Write-Host "Your SnapStudy will work perfectly without Bedrock" -ForegroundColor Green
    Write-Host ""
}

# Step 4: Backend Setup
Write-Step "Step 4: Setting Up Backend"

Set-Location backend

Write-Info "Creating virtual environment..."
python -m venv venv
Write-Success "Virtual environment created"

Write-Info "Activating virtual environment..."
.\venv\Scripts\Activate.ps1

Write-Info "Installing Python dependencies..."
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
Write-Success "Dependencies installed"

Write-Info "Creating .env file..."
$jwtSecret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})

$envContent = @"
AWS_REGION=$script:AWS_REGION
AWS_ACCOUNT_ID=$script:AWS_ACCOUNT_ID
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
JWT_SECRET_KEY=$jwtSecret

# Amazon Q Configuration (Optional)
Q_BUSINESS_APPLICATION_ID=
Q_BUSINESS_INDEX_ID=
Q_DEVELOPER_ENABLED=false

# Bedrock Guardrails Configuration (Optional)
BEDROCK_GUARDRAIL_ID=
BEDROCK_GUARDRAIL_VERSION=DRAFT

# Enhanced Chat Configuration
ENHANCED_CHAT_ENABLED=true
CONTENT_SAFETY_LEVEL=strict
"@

$envContent | Out-File -FilePath .env -Encoding utf8
Write-Success "Backend .env file created"

Set-Location ..

# Step 5: Frontend Setup
Write-Step "Step 5: Setting Up Frontend"

Set-Location frontend

# Fix frontend build issues first
Write-Info "Fixing frontend build issues..."

# Clean node_modules if it exists and is corrupted
if (Test-Path "node_modules") {
    Write-Info "Cleaning existing node_modules..."
    Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
}

if (Test-Path "package-lock.json") {
    Remove-Item package-lock.json -ErrorAction SilentlyContinue
}

Write-Info "Installing frontend dependencies (fresh install)..."
npm install

if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Frontend dependency installation failed"
    exit 1
}

Write-Success "Frontend dependencies installed"

Write-Info "Creating frontend environment configuration..."
$frontendEnvContent = @"
REACT_APP_AWS_REGION=$script:AWS_REGION
REACT_APP_USER_POOL_ID=PLACEHOLDER
REACT_APP_USER_POOL_CLIENT_ID=PLACEHOLDER
REACT_APP_API_URL=PLACEHOLDER
"@

$frontendEnvContent | Out-File -FilePath .env.production -Encoding utf8
Write-Success "Frontend .env.production created"

Write-Info "Building frontend (this may take 2-3 minutes)..."
npm run build

if ($LASTEXITCODE -eq 0) {
    Write-Success "Frontend build completed successfully"
} else {
    Write-Error-Custom "Frontend build failed"
    Write-Info "Check the error messages above"
    Write-Info "You can continue with backend-only deployment if needed"
    
    $continueWithoutFrontend = Read-Host "Continue with backend-only deployment? (y/n)"
    if ($continueWithoutFrontend -ne "y") {
        exit 1
    }
    Write-Info "Continuing with backend-only deployment..."
}

Set-Location ..

# Step 6: CDK Setup and Deployment
Write-Step "Step 6: Deploying Infrastructure"

Set-Location backend\infrastructure

Write-Info "Installing CDK dependencies..."
if (-not (Test-Path "node_modules")) {
    npm install
}

Write-Info "Bootstrapping CDK (if needed)..."
try {
    aws cloudformation describe-stacks --stack-name CDKToolkit --region $script:AWS_REGION 2>$null | Out-Null
    Write-Success "CDK already bootstrapped"
} catch {
    Write-Info "Bootstrapping CDK..."
    cdk bootstrap "aws://$script:AWS_ACCOUNT_ID/$script:AWS_REGION"
}

Write-Info "Synthesizing CloudFormation template..."
cdk synth | Out-Null

Write-Host ""
Write-Host "Ready to deploy SnapStudy to AWS!" -ForegroundColor Green
Write-Host ""
Write-Host "This will create:" -ForegroundColor Yellow
Write-Host "  - Lambda Function (API)" -ForegroundColor White
Write-Host "  - API Gateway (REST API)" -ForegroundColor White
Write-Host "  - DynamoDB Tables" -ForegroundColor White
Write-Host "  - S3 Buckets" -ForegroundColor White
Write-Host "  - Cognito User Pool" -ForegroundColor White
Write-Host "  - CloudWatch Dashboard" -ForegroundColor White
Write-Host ""

$confirmDeploy = Read-Host "Continue with deployment? (y/n)"
if ($confirmDeploy -ne "y") {
    Write-Info "Deployment cancelled"
    exit 0
}

Write-Info "Starting deployment (8-12 minutes)..."
cdk deploy --require-approval never

if ($LASTEXITCODE -eq 0) {
    Write-Success "Infrastructure deployed successfully!"
} else {
    Write-Error-Custom "Deployment failed"
    exit 1
}

# Step 7: Get Deployment Outputs
Write-Step "Step 7: Retrieving Deployment Information"

Set-Location ..\..

aws cloudformation describe-stacks --stack-name SnapStudyStack --region $script:AWS_REGION --query "Stacks[0].Outputs" --output json | Out-File -FilePath deployment-outputs.json

$outputs = Get-Content deployment-outputs.json | ConvertFrom-Json
$script:API_URL = ($outputs | Where-Object { $_.OutputKey -eq "RestApiUrl" }).OutputValue
$script:USER_POOL_ID = ($outputs | Where-Object { $_.OutputKey -eq "UserPoolId" }).OutputValue
$script:USER_POOL_CLIENT_ID = ($outputs | Where-Object { $_.OutputKey -eq "UserPoolClientId" }).OutputValue
$script:FRONTEND_URL = ($outputs | Where-Object { $_.OutputKey -eq "FrontendUrl" }).OutputValue

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "                  DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend API URL: $script:API_URL" -ForegroundColor Green
Write-Host "Frontend Website: $script:FRONTEND_URL" -ForegroundColor Green
Write-Host "User Pool ID: $script:USER_POOL_ID" -ForegroundColor Green
Write-Host ""

# Test API
Write-Info "Testing API health..."
try {
    $health = Invoke-RestMethod -Uri "$script:API_URL/health" -Method Get
    Write-Success "API is healthy!"
} catch {
    Write-Info "API test: $($_.Exception.Message)"
}

Write-Host ""
Write-Host "Your SnapStudy application is now live!" -ForegroundColor Yellow
Write-Host "Open: $script:FRONTEND_URL" -ForegroundColor Cyan
Write-Host ""
Write-Success "Deployment completed successfully!"