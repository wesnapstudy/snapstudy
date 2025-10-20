# SnapStudy Simple Deployment Script
# Fixed version without special characters

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "        SnapStudy AWS Deployment Script" -ForegroundColor Cyan
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

try {
    $cdkVersion = cdk --version
    Write-Success "AWS CDK: $cdkVersion"
} catch {
    Write-Info "Installing AWS CDK..."
    npm install -g aws-cdk
    Write-Success "AWS CDK installed"
}

# Step 2: AWS Credentials
Write-Step "Step 2: Configuring AWS Credentials"

try {
    $accountId = aws sts get-caller-identity --query Account --output text 2>$null
    if ($accountId) {
        Write-Success "AWS credentials found"
        Write-Info "Account ID: $accountId"

        $continue = Read-Host "Use these credentials? (y/n)"
        if ($continue -ne 'y') {
            Write-Info "Please run: aws configure"
            exit 0
        }
    }
} catch {
    Write-Info "AWS credentials not configured"
    Write-Info "Please run: aws configure"
    Write-Info "Then run this script again"
    exit 1
}

$script:AWS_ACCOUNT_ID = aws sts get-caller-identity --query Account --output text
$script:AWS_REGION = if ($env:AWS_REGION) { $env:AWS_REGION } else { "us-east-1" }

Write-Success "Account: $script:AWS_ACCOUNT_ID"
Write-Success "Region: $script:AWS_REGION"

# Step 3: Check Bedrock Access
Write-Step "Step 3: Checking Amazon Bedrock Access"

Write-Info "Checking Claude 3.5 Sonnet access..."

try {
    $models = aws bedrock list-foundation-models --region us-east-1 --output json 2>$null | ConvertFrom-Json
    $claudeModel = $models.modelSummaries | Where-Object { $_.modelId -eq "anthropic.claude-3-5-sonnet-20240620-v1:0" }

    if ($claudeModel) {
        Write-Success "Claude 3.5 Sonnet access confirmed"
    } else {
        Write-Error-Custom "Claude 3.5 Sonnet not accessible"
        Write-Info "Enable it in AWS Console:"
        Write-Info "1. Go to: https://console.aws.amazon.com/bedrock"
        Write-Info "2. Select region: us-east-1 (top right)"
        Write-Info "3. Click 'Model access' (left sidebar)"
        Write-Info "4. Click 'Request model access'"
        Write-Info "5. Enable 'Anthropic Claude 3.5 Sonnet'"
        Write-Host ""
        Read-Host "Press Enter after enabling access"
    }
} catch {
    Write-Error-Custom "Cannot access Bedrock. Ensure you have permissions."
}

# Step 4: Backend Setup
Write-Step "Step 4: Setting Up Backend"

Set-Location backend

Write-Info "Creating virtual environment..."
python -m venv venv
Write-Success "Virtual environment created"

Write-Info "Activating virtual environment..."
.\venv\Scripts\Activate.ps1

Write-Info "Installing Python dependencies (this may take a few minutes)..."
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
Write-Success "Dependencies installed"

Write-Info "Creating .env file..."
$jwtSecret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
@"
AWS_REGION=$script:AWS_REGION
AWS_ACCOUNT_ID=$script:AWS_ACCOUNT_ID
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
JWT_SECRET_KEY=$jwtSecret
"@ | Out-File -FilePath .env -Encoding utf8
Write-Success ".env file created"

Set-Location ..

# Step 5: CDK Bootstrap
Write-Step "Step 5: Bootstrapping AWS CDK"

try {
    aws cloudformation describe-stacks --stack-name CDKToolkit --region $script:AWS_REGION 2>$null | Out-Null
    Write-Success "CDK already bootstrapped"
} catch {
    Write-Info "Bootstrapping CDK (first-time setup)..."
    Set-Location backend\infrastructure
    cdk bootstrap "aws://$script:AWS_ACCOUNT_ID/$script:AWS_REGION"
    if ($LASTEXITCODE -eq 0) {
        Write-Success "CDK bootstrapped"
    } else {
        Write-Error-Custom "CDK bootstrap failed"
        exit 1
    }
    Set-Location ..\..
}

# Step 6: Install CDK Dependencies
Write-Step "Step 6: Installing CDK Dependencies"

Set-Location backend\infrastructure

Write-Info "Installing Node.js dependencies..."
npm install
Write-Success "CDK dependencies installed"

# Step 7: Synthesize Template
Write-Step "Step 7: Generating CloudFormation Template"

Write-Info "Synthesizing template..."
cdk synth | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Success "Template generated"
} else {
    Write-Error-Custom "Template generation failed"
    exit 1
}

# Step 8: Deploy Infrastructure
Write-Step "Step 8: Deploying to AWS"

Write-Host ""
Write-Host "This will create AWS resources in your account:" -ForegroundColor Yellow
Write-Host "  - Lambda Function (API)" -ForegroundColor White
Write-Host "  - API Gateway (REST API)" -ForegroundColor White
Write-Host "  - DynamoDB Tables (6 tables)" -ForegroundColor White
Write-Host "  - S3 Bucket" -ForegroundColor White
Write-Host "  - Cognito User Pool" -ForegroundColor White
Write-Host "  - CloudWatch Dashboard" -ForegroundColor White
Write-Host "  - AWS WAF" -ForegroundColor White
Write-Host ""
Write-Host "Estimated deployment time: 5-10 minutes" -ForegroundColor Yellow
Write-Host ""

$confirmDeploy = Read-Host "Continue with deployment? (y/n)"
if ($confirmDeploy -ne "y") {
    Write-Info "Deployment cancelled"
    exit 0
}

Write-Info "Starting deployment (please wait 5-10 minutes)..."
cdk deploy --require-approval never

if ($LASTEXITCODE -eq 0) {
    Write-Success "Infrastructure deployed successfully!"
} else {
    Write-Error-Custom "Deployment failed"
    exit 1
}

Set-Location ..\..

# Step 9: Save Outputs
Write-Step "Step 9: Retrieving Deployment Outputs"

aws cloudformation describe-stacks --stack-name SnapStudyStack --region $script:AWS_REGION --query "Stacks[0].Outputs" --output json | Out-File -FilePath deployment-outputs.json

$outputs = Get-Content deployment-outputs.json | ConvertFrom-Json
$script:API_URL = ($outputs | Where-Object { $_.OutputKey -eq "RestApiUrl" }).OutputValue
$script:USER_POOL_ID = ($outputs | Where-Object { $_.OutputKey -eq "UserPoolId" }).OutputValue
$script:USER_POOL_CLIENT_ID = ($outputs | Where-Object { $_.OutputKey -eq "UserPoolClientId" }).OutputValue
$script:CONTENT_BUCKET = ($outputs | Where-Object { $_.OutputKey -eq "ContentBucketName" }).OutputValue

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "                   DEPLOYMENT OUTPUTS" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "API URL: $script:API_URL" -ForegroundColor Green
Write-Host "User Pool ID: $script:USER_POOL_ID" -ForegroundColor Green
Write-Host "Client ID: $script:USER_POOL_CLIENT_ID" -ForegroundColor Green
Write-Host "S3 Bucket: $script:CONTENT_BUCKET" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Step 10: Test Deployment
Write-Step "Step 10: Testing Deployment"

Write-Info "Testing API health endpoint..."
try {
    $health = Invoke-RestMethod -Uri "$script:API_URL/health" -Method Get
    Write-Success "API is healthy!"
    Write-Info "Response: $($health | ConvertTo-Json -Compress)"
} catch {
    Write-Info "API test: $($_.Exception.Message)"
}

# Step 11: Create Test User
Write-Step "Step 11: Creating Test User"

$createUser = Read-Host "Create test user? (y/n)"
if ($createUser -eq "y") {
    $testEmail = "test@example.com"
    $testPassword = "TestPassword123!"

    Write-Info "Creating user: $testEmail"

    aws cognito-idp admin-create-user `
        --user-pool-id $script:USER_POOL_ID `
        --username $testEmail `
        --user-attributes Name=email,Value=$testEmail Name=email_verified,Value=true Name=name,Value="Test User" `
        --message-action SUPPRESS `
        --region $script:AWS_REGION 2>$null

    aws cognito-idp admin-set-user-password `
        --user-pool-id $script:USER_POOL_ID `
        --username $testEmail `
        --password $testPassword `
        --permanent `
        --region $script:AWS_REGION 2>$null

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Test user created"
        Write-Host ""
        Write-Host "Test User Credentials:" -ForegroundColor Yellow
        Write-Host "  Email: $testEmail" -ForegroundColor White
        Write-Host "  Password: $testPassword" -ForegroundColor White
        Write-Host ""
    }
}

# Step 12: Frontend Setup
Write-Step "Step 12: Frontend Setup"

$setupFrontend = Read-Host "Set up frontend? (y/n)"
if ($setupFrontend -eq "y") {
    Set-Location frontend

    Write-Info "Installing frontend dependencies..."
    npm install

    Write-Info "Creating frontend config..."
    @"
REACT_APP_API_URL=$script:API_URL
REACT_APP_USER_POOL_ID=$script:USER_POOL_ID
REACT_APP_USER_POOL_CLIENT_ID=$script:USER_POOL_CLIENT_ID
REACT_APP_AWS_REGION=$script:AWS_REGION
"@ | Out-File -FilePath .env.local -Encoding utf8

    Write-Info "Building frontend..."
    npm run build

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Frontend built successfully"
    }

    Set-Location ..
}

# Final Summary
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "                  DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Test API: Invoke-RestMethod -Uri '$script:API_URL/health'" -ForegroundColor White
Write-Host "  2. View CloudWatch: AWS Console -> CloudWatch -> Dashboards" -ForegroundColor White
Write-Host "  3. Run frontend: cd frontend && npm start" -ForegroundColor White
Write-Host ""
Write-Host "Outputs saved to:" -ForegroundColor Yellow
Write-Host "  - deployment-outputs.json" -ForegroundColor White
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""

Write-Success "Deployment completed successfully!"
