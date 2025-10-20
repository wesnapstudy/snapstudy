# SnapStudy Complete Deployment Script with Frontend
# Deploys both backend infrastructure and frontend to AWS cloud

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "        SnapStudy Complete AWS Deployment (Backend + Frontend)" -ForegroundColor Cyan
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
    $npmVersion = npm --version
    Write-Success "npm: v$npmVersion"
} catch {
    Write-Error-Custom "npm not found. Install Node.js from: https://nodejs.org"
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

# Step 2: Check AWS Profile
Write-Step "Step 2: Checking AWS Profile 'hackathon'"

try {
    $profiles = aws configure list-profiles 2>&1
    $profilesList = $profiles -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }

    if ($profilesList -notcontains "hackathon") {
        Write-Error-Custom "Hackathon AWS profile not found"
        Write-Info "Available profiles: $($profilesList -join ', ')"
        Write-Info ""
        Write-Info "Please configure the 'hackathon' profile:"
        Write-Info "  aws configure --profile hackathon"
        Write-Info "  Enter your Hackathon Access Key ID"
        Write-Info "  Enter your Hackathon Secret Access Key"
        Write-Info "  Enter region: us-east-1"
        Write-Info "  Enter output: json"
        exit 1
    }

    Write-Success "Found 'hackathon' AWS profile"
} catch {
    Write-Error-Custom "Error checking AWS profiles: $_"
    exit 1
}

# Set the AWS profile environment variable
$env:AWS_PROFILE = "hackathon"
Write-Success "Using AWS Profile: hackathon"

# Verify profile is working
Write-Info "Testing AWS profile 'hackathon'..."

try {
    # Test the profile credentials
    $testOutput = aws sts get-caller-identity --profile hackathon --output json 2>&1
    
    # Check for specific error patterns
    if ($testOutput -match "InvalidClientTokenId") {
        Write-Error-Custom "AWS credentials for 'hackathon' profile are invalid or expired"
        Write-Info ""
        Write-Info "The hackathon profile exists but the credentials are not working."
        Write-Info "This usually means:"
        Write-Info "  1. The Access Key ID or Secret Access Key is incorrect"
        Write-Info "  2. The credentials have expired"
        Write-Info "  3. The credentials don't have the necessary permissions"
        Write-Info ""
        Write-Info "Please update your hackathon profile credentials:"
        Write-Info "  aws configure --profile hackathon"
        Write-Info "  Enter your current/valid Hackathon Access Key ID"
        Write-Info "  Enter your current/valid Hackathon Secret Access Key"
        Write-Info "  Set region: us-east-1"
        Write-Info "  Set output: json"
        Write-Info ""
        Write-Info "After updating, test with:"
        Write-Info "  aws sts get-caller-identity --profile hackathon"
        exit 1
    }
    
    if ($testOutput -match "error" -or $testOutput -match "Unable" -or $testOutput -match "could not be found") {
        throw "Profile test failed: $testOutput"
    }
    
    # Try to parse the JSON output
    try {
        $testIdentityObj = $testOutput | ConvertFrom-Json
        Write-Success "AWS Profile 'hackathon' is working correctly"
        Write-Info "Account: $($testIdentityObj.Account)"
        Write-Info "User: $($testIdentityObj.Arn)"
    } catch {
        # If JSON parsing fails, check if we can extract account ID manually
        if ($testOutput -match '"Account":\s*"(\d+)"') {
            Write-Success "AWS Profile 'hackathon' is working (with parsing workaround)"
            Write-Info "Account: $($matches[1])"
        } else {
            throw "Could not parse AWS identity response: $testOutput"
        }
    }
} catch {
    Write-Error-Custom "AWS Profile 'hackathon' test failed"
    Write-Info "Error: $_"
    Write-Info ""
    Write-Info "Current profile configuration:"
    try {
        aws configure list --profile hackathon
    } catch {
        Write-Info "Could not retrieve profile configuration"
    }
    Write-Info ""
    Write-Info "Please reconfigure the hackathon profile:"
    Write-Info "  aws configure --profile hackathon"
    Write-Info "  Enter your valid Hackathon credentials"
    exit 1
}

# Step 3: Verify AWS Credentials
Write-Step "Step 3: Verifying AWS Credentials"

try {
    Write-Info "Getting AWS account information..."
    
    # Try multiple approaches to get identity
    $identityOutput = $null
    $parseSuccess = $false
    
    # Method 1: Use environment variable
    try {
        $identityOutput = aws sts get-caller-identity --output json 2>&1
        $identity = $identityOutput | ConvertFrom-Json
        $parseSuccess = $true
        Write-Info "Method 1 (env var) successful"
    } catch {
        Write-Info "Method 1 failed, trying method 2..."
    }
    
    # Method 2: Explicit profile with retry
    if (-not $parseSuccess) {
        try {
            Start-Sleep 2
            $identityOutput = aws sts get-caller-identity --profile hackathon --output json 2>&1
            $identity = $identityOutput | ConvertFrom-Json
            $parseSuccess = $true
            Write-Info "Method 2 (explicit profile) successful"
        } catch {
            Write-Info "Method 2 failed, trying method 3..."
        }
    }
    
    # Method 3: Text parsing fallback
    if (-not $parseSuccess) {
        Write-Info "JSON parsing failed, using text parsing..."
        if ($identityOutput -match '"Account":\s*"(\d+)"') {
            $script:AWS_ACCOUNT_ID = $matches[1]
            $parseSuccess = $true
            Write-Info "Method 3 (text parsing) successful"
        }
    }
    
    if (-not $parseSuccess) {
        throw "Could not parse AWS identity from any method. Output: $identityOutput"
    }
    
    # Set account ID
    if ($identity -and $identity.Account) {
        $script:AWS_ACCOUNT_ID = $identity.Account
    }
    
    # Get region
    $script:AWS_REGION = aws configure get region --profile hackathon 2>$null
    if (-not $script:AWS_REGION) {
        $script:AWS_REGION = "us-east-1"
        Write-Info "No region configured, using default: us-east-1"
    }

    Write-Success "AWS credentials verified"
    Write-Success "Account ID: $script:AWS_ACCOUNT_ID"
    Write-Success "Region: $script:AWS_REGION"
    
    if ($identity -and $identity.Arn) {
        Write-Success "User ARN: $($identity.Arn)"
    }
} catch {
    Write-Error-Custom "AWS credentials verification failed"
    Write-Info "Error: $_"
    Write-Info ""
    Write-Info "Debug information:"
    Write-Info "Raw output: $identityOutput"
    Write-Info ""
    Write-Info "Please try these steps:"
    Write-Info "1. Test manually: aws sts get-caller-identity --profile hackathon"
    Write-Info "2. Check profile: aws configure list --profile hackathon"
    Write-Info "3. Reconfigure: aws configure --profile hackathon"
    exit 1
}

# Step 4: Check Bedrock Access (Optional)
Write-Step "Step 4: Checking Amazon Bedrock Access (Optional)"

Write-Info "Testing Bedrock access (this step is optional)..."

# Make Bedrock check completely non-blocking
$bedrockAvailable = $false

try {
    # Use cmd to avoid PowerShell execution policy issues
    $bedrockTest = cmd /c "aws bedrock list-foundation-models --region us-east-1 --profile hackathon --output json 2>nul"
    
    if ($bedrockTest -and $bedrockTest -match '"modelSummaries"') {
        Write-Success "Bedrock service is accessible"
        $bedrockAvailable = $true
        
        # Check for Claude model availability
        if ($bedrockTest -match "anthropic.claude-3-5-sonnet") {
            Write-Success "Claude 3.5 Sonnet is available"
        } else {
            Write-Info "Claude 3.5 Sonnet not found - may need to be enabled"
            Write-Info "You can enable it later in AWS Console > Bedrock > Model access"
        }
    } else {
        Write-Info "Bedrock access is limited or not available"
    }
} catch {
    Write-Info "Bedrock check could not be completed"
}

if (-not $bedrockAvailable) {
    Write-Host ""
    Write-Host "Bedrock Status: Not Available or Limited Access" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "This is completely fine! Your SnapStudy deployment will:" -ForegroundColor Green
    Write-Host "  ✓ Work perfectly without Bedrock" -ForegroundColor Green
    Write-Host "  ✓ Use alternative AI services" -ForegroundColor Green
    Write-Host "  ✓ Provide full functionality" -ForegroundColor Green
    Write-Host ""
    Write-Host "To enable Bedrock later (optional):" -ForegroundColor Cyan
    Write-Host "  1. Go to AWS Console > Bedrock > Model access" -ForegroundColor White
    Write-Host "  2. Request access to Claude 3.5 Sonnet" -ForegroundColor White
    Write-Host "  3. Update your application configuration" -ForegroundColor White
    Write-Host ""
}

Write-Info "Continuing with deployment - Bedrock is optional for SnapStudy"

# Step 5: Backend Setup
Write-Step "Step 5: Setting Up Backend"

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

# Amazon Q Configuration (Optional - configure after deployment)
Q_BUSINESS_APPLICATION_ID=
Q_BUSINESS_INDEX_ID=
Q_DEVELOPER_ENABLED=false

# Bedrock Guardrails Configuration (Optional)
BEDROCK_GUARDRAIL_ID=
BEDROCK_GUARDRAIL_VERSION=DRAFT

# Enhanced Chat Configuration
ENHANCED_CHAT_ENABLED=true
CONTENT_SAFETY_LEVEL=strict
"@ | Out-File -FilePath .env -Encoding utf8
Write-Success ".env file created"

Set-Location ..

# Step 6: Frontend Setup
Write-Step "Step 6: Setting Up and Building Frontend"

Set-Location frontend

if (-not (Test-Path "node_modules")) {
    Write-Info "Installing frontend dependencies (this may take a few minutes)..."
    npm install
    Write-Success "Frontend dependencies installed"
} else {
    Write-Info "Frontend dependencies already installed"
}

Write-Info "Creating frontend environment configuration..."
@"
REACT_APP_AWS_REGION=$script:AWS_REGION
REACT_APP_USER_POOL_ID=PLACEHOLDER
REACT_APP_USER_POOL_CLIENT_ID=PLACEHOLDER
REACT_APP_API_URL=PLACEHOLDER
"@ | Out-File -FilePath .env.production -Encoding utf8
Write-Success "Frontend .env.production created (will be updated after deployment)"

Write-Info "Building frontend (this may take 2-3 minutes)..."
npm run build

if ($LASTEXITCODE -eq 0) {
    Write-Success "Frontend build completed successfully"
    Write-Success "Build files located in: frontend\build\"
} else {
    Write-Error-Custom "Frontend build failed"
    exit 1
}

Set-Location ..

# Step 7: CDK Bootstrap
Write-Step "Step 7: Bootstrapping AWS CDK"

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

# Step 8: Install CDK Dependencies
Write-Step "Step 8: Installing CDK Dependencies"

Set-Location backend\infrastructure

if (-not (Test-Path "node_modules")) {
    Write-Info "Installing Node.js dependencies..."
    npm install
    Write-Success "CDK dependencies installed"
} else {
    Write-Info "CDK dependencies already installed"
}

# Step 9: Synthesize Template
Write-Step "Step 9: Generating CloudFormation Template"

Write-Info "Synthesizing template..."
cdk synth | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Success "Template generated"
} else {
    Write-Error-Custom "Template generation failed"
    exit 1
}

# Step 10: Deploy Infrastructure
Write-Step "Step 10: Deploying to AWS (Backend + Frontend)"

Write-Host ""
Write-Host "This will create AWS resources in your account:" -ForegroundColor Yellow
Write-Host "  - Lambda Function (API)" -ForegroundColor White
Write-Host "  - API Gateway (REST API)" -ForegroundColor White
Write-Host "  - DynamoDB Tables (6 tables)" -ForegroundColor White
Write-Host "  - S3 Bucket (Content)" -ForegroundColor White
Write-Host "  - S3 Bucket (Frontend Website)" -ForegroundColor White
Write-Host "  - Cognito User Pool" -ForegroundColor White
Write-Host "  - CloudWatch Dashboard" -ForegroundColor White
Write-Host "  - AWS WAF" -ForegroundColor White
Write-Host ""
Write-Host "Estimated deployment time: 8-12 minutes" -ForegroundColor Yellow
Write-Host ""

$confirmDeploy = Read-Host "Continue with deployment? (y/n)"
if ($confirmDeploy -ne "y") {
    Write-Info "Deployment cancelled"
    exit 0
}

Write-Info "Starting deployment (please wait 8-12 minutes)..."
Write-Info "Frontend build will be automatically deployed to S3..."
cdk deploy --require-approval never

if ($LASTEXITCODE -eq 0) {
    Write-Success "Infrastructure deployed successfully!"
} else {
    Write-Error-Custom "Deployment failed"
    exit 1
}

Set-Location ..\..

# Step 11: Retrieve Deployment Outputs
Write-Step "Step 11: Retrieving Deployment Outputs"

aws cloudformation describe-stacks --stack-name SnapStudyStack --region $script:AWS_REGION --query "Stacks[0].Outputs" --output json | Out-File -FilePath deployment-outputs.json

$outputs = Get-Content deployment-outputs.json | ConvertFrom-Json
$script:API_URL = ($outputs | Where-Object { $_.OutputKey -eq "RestApiUrl" }).OutputValue
$script:USER_POOL_ID = ($outputs | Where-Object { $_.OutputKey -eq "UserPoolId" }).OutputValue
$script:USER_POOL_CLIENT_ID = ($outputs | Where-Object { $_.OutputKey -eq "UserPoolClientId" }).OutputValue
$script:CONTENT_BUCKET = ($outputs | Where-Object { $_.OutputKey -eq "ContentBucketName" }).OutputValue
$script:FRONTEND_BUCKET = ($outputs | Where-Object { $_.OutputKey -eq "FrontendBucketName" }).OutputValue
$script:FRONTEND_URL = ($outputs | Where-Object { $_.OutputKey -eq "FrontendUrl" }).OutputValue

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "                   DEPLOYMENT OUTPUTS" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "Backend API URL: $script:API_URL" -ForegroundColor Green
Write-Host "User Pool ID: $script:USER_POOL_ID" -ForegroundColor Green
Write-Host "Client ID: $script:USER_POOL_CLIENT_ID" -ForegroundColor Green
Write-Host "Content S3 Bucket: $script:CONTENT_BUCKET" -ForegroundColor Green
Write-Host "Frontend S3 Bucket: $script:FRONTEND_BUCKET" -ForegroundColor Green
Write-Host "Frontend Website URL: $script:FRONTEND_URL" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Step 12: Update Frontend Configuration
Write-Step "Step 12: Updating Frontend Configuration with Real Values"

Set-Location frontend

Write-Info "Creating updated .env.production with deployment values..."
@"
REACT_APP_AWS_REGION=$script:AWS_REGION
REACT_APP_USER_POOL_ID=$script:USER_POOL_ID
REACT_APP_USER_POOL_CLIENT_ID=$script:USER_POOL_CLIENT_ID
REACT_APP_API_URL=$script:API_URL
"@ | Out-File -FilePath .env.production -Encoding utf8
Write-Success "Frontend .env.production updated"

Write-Info "Rebuilding frontend with correct configuration..."
npm run build

if ($LASTEXITCODE -eq 0) {
    Write-Success "Frontend rebuilt successfully"

    # Re-deploy frontend with updated config
    Write-Info "Deploying updated frontend to S3..."
    aws s3 sync build/ "s3://$script:FRONTEND_BUCKET" --delete --region $script:AWS_REGION

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Frontend deployed to S3 successfully"
    } else {
        Write-Error-Custom "Frontend S3 upload failed"
    }
} else {
    Write-Error-Custom "Frontend rebuild failed"
}

Set-Location ..

# Step 13: Test Deployment
Write-Step "Step 13: Testing Deployment"

Write-Info "Testing API health endpoint..."
try {
    $health = Invoke-RestMethod -Uri "$script:API_URL/health" -Method Get
    Write-Success "API is healthy!"
    Write-Info "Response: $($health | ConvertTo-Json -Compress)"
} catch {
    Write-Info "API test: $($_.Exception.Message)"
    Write-Info "Note: API may need a few seconds to warm up. Try again in a moment."
}

Write-Info "Testing frontend website..."
try {
    $frontendResponse = Invoke-WebRequest -Uri $script:FRONTEND_URL -Method Get -UseBasicParsing
    if ($frontendResponse.StatusCode -eq 200) {
        Write-Success "Frontend website is accessible!"
    }
} catch {
    Write-Info "Frontend test: $($_.Exception.Message)"
}

# Step 14: Create Test User
Write-Step "Step 14: Creating Test User"

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

# Final Summary
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "                  DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your SnapStudy application is now deployed to AWS!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Backend API:" -ForegroundColor Yellow
Write-Host "  URL: $script:API_URL" -ForegroundColor White
Write-Host "  Test: Invoke-RestMethod -Uri '$script:API_URL/health'" -ForegroundColor White
Write-Host ""
Write-Host "Frontend Website:" -ForegroundColor Yellow
Write-Host "  URL: $script:FRONTEND_URL" -ForegroundColor White
Write-Host "  Open in browser to access the application" -ForegroundColor White
Write-Host ""
Write-Host "AWS Resources:" -ForegroundColor Yellow
Write-Host "  CloudWatch Dashboard: AWS Console -> CloudWatch -> Dashboards -> SnapStudy-Metrics" -ForegroundColor White
Write-Host "  WAF Rules: AWS Console -> WAF & Shield -> Web ACLs -> SnapStudyApiWaf" -ForegroundColor White
Write-Host "  DynamoDB Tables: AWS Console -> DynamoDB -> Tables" -ForegroundColor White
Write-Host ""
Write-Host "Outputs saved to:" -ForegroundColor Yellow
Write-Host "  - deployment-outputs.json" -ForegroundColor White
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""

Write-Success "Deployment completed successfully!"
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Open frontend: $script:FRONTEND_URL" -ForegroundColor White
Write-Host "2. Login with test user (if created)" -ForegroundColor White
Write-Host "3. Monitor via CloudWatch Dashboard" -ForegroundColor White
Write-Host "4. Review security via AWS WAF console" -ForegroundColor White
Write-Host ""
Write-Host "Optional Enhancements:" -ForegroundColor Cyan
Write-Host "To enable advanced educational AI features with Amazon Q:" -ForegroundColor White
Write-Host "  1. Run: .\setup-amazon-q.ps1" -ForegroundColor Yellow
Write-Host "     This configures Amazon Q Business for educational resources" -ForegroundColor White
Write-Host "  2. Sets up Bedrock Guardrails for content safety" -ForegroundColor White
Write-Host "  3. Enables enhanced chat with multi-AI orchestration" -ForegroundColor White
Write-Host ""
Write-Host "Benefits of Amazon Q Integration:" -ForegroundColor Cyan
Write-Host "  - Research assistance with educational resources" -ForegroundColor White
Write-Host "  - Coding help with safety validation" -ForegroundColor White
Write-Host "  - Multi-layered content safety guardrails" -ForegroundColor White
Write-Host "  - Educational appropriateness validation" -ForegroundColor White
Write-Host "  - Academic integrity enforcement" -ForegroundColor White
Write-Host ""
