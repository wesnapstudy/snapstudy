# SnapStudy Deployment Script - Fixed Credential Detection
# This version has improved credential detection

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

# Step 2: AWS Credentials - IMPROVED DETECTION
Write-Step "Step 2: Configuring AWS Credentials"

Write-Info "Testing AWS credentials..."

# Try to get caller identity
$callerIdentity = $null
try {
    $callerIdentity = aws sts get-caller-identity 2>&1

    # Check if it's an error or valid JSON
    if ($callerIdentity -match "Unable to locate credentials" -or $callerIdentity -match "could not be found") {
        throw "Credentials not found"
    }

    # Parse the JSON
    $identity = $callerIdentity | ConvertFrom-Json

    if ($identity.Account) {
        $script:AWS_ACCOUNT_ID = $identity.Account
        $script:AWS_REGION = if ($env:AWS_REGION) { $env:AWS_REGION } else { "us-east-1" }

        Write-Success "AWS credentials detected"
        Write-Info "Account ID: $script:AWS_ACCOUNT_ID"
        Write-Info "Region: $script:AWS_REGION"
        Write-Info "User: $($identity.Arn)"

        $continue = Read-Host "`nUse these credentials? (y/n)"
        if ($continue -ne 'y' -and $continue -ne 'Y') {
            Write-Info "Please configure different credentials:"
            Write-Info "  aws configure"
            exit 0
        }
    } else {
        throw "Invalid response from AWS"
    }
} catch {
    Write-Error-Custom "AWS credentials not working"
    Write-Info "Error: $_"
    Write-Info ""
    Write-Info "Please configure AWS credentials:"
    Write-Info "  1. Run: aws configure"
    Write-Info "  2. Enter your Access Key ID"
    Write-Info "  3. Enter your Secret Access Key"
    Write-Info "  4. Enter region: us-east-1"
    Write-Info "  5. Enter output: json"
    Write-Info ""
    Write-Info "Then run this script again"
    exit 1
}

Write-Success "Using Account: $script:AWS_ACCOUNT_ID"
Write-Success "Using Region: $script:AWS_REGION"

# Step 3: Check Bedrock Access
Write-Step "Step 3: Checking Amazon Bedrock Access"

Write-Info "Checking Claude 3.5 Sonnet access..."

try {
    $bedrockOutput = aws bedrock list-foundation-models --region us-east-1 --output json 2>&1

    if ($bedrockOutput -match "error" -or $bedrockOutput -match "Unable") {
        Write-Info "Cannot access Bedrock API. Continuing anyway..."
    } else {
        $models = $bedrockOutput | ConvertFrom-Json
        $claudeModel = $models.modelSummaries | Where-Object { $_.modelId -eq "anthropic.claude-3-5-sonnet-20240620-v1:0" }

        if ($claudeModel) {
            Write-Success "Claude 3.5 Sonnet access confirmed"
        } else {
            Write-Info "Claude 3.5 Sonnet not found in available models"
            Write-Info ""
            Write-Info "You need to enable it in AWS Console:"
            Write-Info "  1. Go to: https://console.aws.amazon.com/bedrock"
            Write-Info "  2. Select region: us-east-1 (top right corner)"
            Write-Info "  3. Click 'Model access' (left sidebar)"
            Write-Info "  4. Click 'Request model access' (orange button)"
            Write-Info "  5. Find and enable 'Anthropic Claude 3.5 Sonnet'"
            Write-Info "  6. Wait for approval (usually instant)"
            Write-Host ""
            $continue = Read-Host "Press Enter after enabling Bedrock access (or Ctrl+C to cancel)"
        }
    }
} catch {
    Write-Info "Bedrock check skipped. Will verify during deployment."
}

# Step 4: Backend Setup
Write-Step "Step 4: Setting Up Backend"

if (-not (Test-Path "backend")) {
    Write-Error-Custom "Backend directory not found. Are you in the right directory?"
    Write-Info "Current directory: $(Get-Location)"
    Write-Info "Expected: D:\repo\hackathon\study"
    exit 1
}

Set-Location backend

Write-Info "Creating virtual environment..."
if (Test-Path "venv") {
    Write-Info "Virtual environment already exists, using it"
} else {
    python -m venv venv
    Write-Success "Virtual environment created"
}

Write-Info "Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

Write-Info "Upgrading pip..."
python -m pip install --upgrade pip --quiet

Write-Info "Installing Python dependencies (this may take a few minutes)..."
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Success "Dependencies installed"
} else {
    Write-Error-Custom "Failed to install dependencies"
    exit 1
}

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
    $stackInfo = aws cloudformation describe-stacks --stack-name CDKToolkit --region $script:AWS_REGION 2>&1
    if ($stackInfo -match "does not exist") {
        throw "Not bootstrapped"
    }
    Write-Success "CDK already bootstrapped"
} catch {
    Write-Info "Bootstrapping CDK (first-time setup)..."
    Write-Info "This creates an S3 bucket and IAM roles for CDK"

    Set-Location backend\infrastructure

    Write-Info "Running: cdk bootstrap aws://$script:AWS_ACCOUNT_ID/$script:AWS_REGION"
    cdk bootstrap "aws://$script:AWS_ACCOUNT_ID/$script:AWS_REGION"

    if ($LASTEXITCODE -eq 0) {
        Write-Success "CDK bootstrapped successfully"
    } else {
        Write-Error-Custom "CDK bootstrap failed"
        Write-Info "Check if you have IAM permissions"
        exit 1
    }

    Set-Location ..\..
}

# Step 6: Install CDK Dependencies
Write-Step "Step 6: Installing CDK Dependencies"

Set-Location backend\infrastructure

if (-not (Test-Path "package.json")) {
    Write-Error-Custom "package.json not found in infrastructure directory"
    exit 1
}

Write-Info "Installing Node.js dependencies..."
npm install
if ($LASTEXITCODE -eq 0) {
    Write-Success "CDK dependencies installed"
} else {
    Write-Error-Custom "Failed to install CDK dependencies"
    exit 1
}

# Step 7: Synthesize Template
Write-Step "Step 7: Generating CloudFormation Template"

Write-Info "Synthesizing CDK template..."
cdk synth | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Success "CloudFormation template generated"
    Write-Info "Template location: cdk.out/"
} else {
    Write-Error-Custom "Template generation failed"
    Write-Info "Check the error messages above"
    exit 1
}

# Step 8: Deploy Infrastructure
Write-Step "Step 8: Deploying to AWS"

Write-Host ""
Write-Host "Resources to be created:" -ForegroundColor Yellow
Write-Host "  - Lambda Function (FastAPI backend)" -ForegroundColor White
Write-Host "  - API Gateway (REST API)" -ForegroundColor White
Write-Host "  - DynamoDB Tables (6 tables)" -ForegroundColor White
Write-Host "  - S3 Bucket (content storage)" -ForegroundColor White
Write-Host "  - Cognito User Pool (authentication)" -ForegroundColor White
Write-Host "  - CloudWatch Dashboard (monitoring)" -ForegroundColor White
Write-Host "  - AWS WAF (security)" -ForegroundColor White
Write-Host ""
Write-Host "Estimated deployment time: 5-10 minutes" -ForegroundColor Yellow
Write-Host "Estimated cost: `$0-5/month (mostly free tier)" -ForegroundColor Yellow
Write-Host ""

$confirmDeploy = Read-Host "Continue with deployment? (y/n)"
if ($confirmDeploy -ne "y" -and $confirmDeploy -ne "Y") {
    Write-Info "Deployment cancelled by user"
    exit 0
}

Write-Host ""
Write-Info "Starting deployment... (please wait 5-10 minutes)"
Write-Info "You can watch progress in AWS Console: CloudFormation > Stacks"
Write-Host ""

cdk deploy --require-approval never

if ($LASTEXITCODE -eq 0) {
    Write-Success "Infrastructure deployed successfully!"
} else {
    Write-Error-Custom "Deployment failed"
    Write-Info "Check CloudFormation console for details"
    Write-Info "https://console.aws.amazon.com/cloudformation"
    exit 1
}

Set-Location ..\..

# Step 9: Save Outputs
Write-Step "Step 9: Retrieving Deployment Outputs"

Write-Info "Fetching CloudFormation outputs..."
aws cloudformation describe-stacks --stack-name SnapStudyStack --region $script:AWS_REGION --query "Stacks[0].Outputs" --output json | Out-File -FilePath deployment-outputs.json

if (Test-Path "deployment-outputs.json") {
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
} else {
    Write-Info "Could not retrieve outputs. Check AWS Console."
}

# Step 10: Test Deployment
Write-Step "Step 10: Testing Deployment"

if ($script:API_URL) {
    Write-Info "Testing API health endpoint..."
    try {
        $health = Invoke-RestMethod -Uri "$script:API_URL/health" -Method Get -TimeoutSec 10
        Write-Success "API is healthy!"
        Write-Info "Response: $($health | ConvertTo-Json -Compress)"
    } catch {
        Write-Info "API test: $($_.Exception.Message)"
        Write-Info "The API might need a minute to warm up. Try again in 30 seconds."
    }
}

# Step 11: Create Test User
Write-Step "Step 11: Creating Test User (Optional)"

$createUser = Read-Host "Create test user? (y/n)"
if ($createUser -eq "y" -or $createUser -eq "Y") {
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
        Write-Host "=====================================================================" -ForegroundColor Cyan
        Write-Host "Test User Credentials:" -ForegroundColor Yellow
        Write-Host "  Email: $testEmail" -ForegroundColor White
        Write-Host "  Password: $testPassword" -ForegroundColor White
        Write-Host "=====================================================================" -ForegroundColor Cyan
        Write-Host ""
    } else {
        Write-Info "User may already exist or there was an error"
    }
}

# Step 12: Frontend Setup
Write-Step "Step 12: Frontend Setup (Optional)"

$setupFrontend = Read-Host "Set up frontend? (y/n)"
if ($setupFrontend -eq "y" -or $setupFrontend -eq "Y") {
    if (Test-Path "frontend") {
        Set-Location frontend

        Write-Info "Installing frontend dependencies..."
        npm install

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Frontend dependencies installed"
        }

        Write-Info "Creating frontend configuration..."
        @"
REACT_APP_API_URL=$script:API_URL
REACT_APP_USER_POOL_ID=$script:USER_POOL_ID
REACT_APP_USER_POOL_CLIENT_ID=$script:USER_POOL_CLIENT_ID
REACT_APP_AWS_REGION=$script:AWS_REGION
"@ | Out-File -FilePath .env.local -Encoding utf8
        Write-Success "Frontend config created (.env.local)"

        Write-Info "Building frontend (this takes 2-3 minutes)..."
        npm run build

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Frontend built successfully"
            Write-Info "Build files: frontend\build\"
        } else {
            Write-Info "Frontend build had errors (can fix later)"
        }

        Set-Location ..
    } else {
        Write-Info "Frontend directory not found, skipping"
    }
}

# Final Summary
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "                  DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Test API:" -ForegroundColor White
Write-Host "   Invoke-RestMethod -Uri '$script:API_URL/health'" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. View CloudWatch Dashboard:" -ForegroundColor White
Write-Host "   https://console.aws.amazon.com/cloudwatch/home?region=$script:AWS_REGION#dashboards:" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Run Frontend:" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Cyan
Write-Host "   npm start" -ForegroundColor Cyan
Write-Host ""
Write-Host "Outputs saved to:" -ForegroundColor Yellow
Write-Host "  - deployment-outputs.json" -ForegroundColor White
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""

Write-Success "Deployment script completed!"
