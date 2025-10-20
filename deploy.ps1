# SnapStudy - PowerShell Deployment Script for Windows
# This script deploys SnapStudy to AWS using PowerShell

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-ErrorCustom {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Print-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host ""
}

################################################################################
# STEP 1: Prerequisites Check
################################################################################

function Check-Prerequisites {
    Print-Header "STEP 1: Checking Prerequisites"

    $missingTools = 0

    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Success "Python installed: $pythonVersion"
    } catch {
        Write-ErrorCustom "Python 3.11+ is required but not found"
        $missingTools++
    }

    # Check Node.js
    try {
        $nodeVersion = node --version
        Write-Success "Node.js installed: $nodeVersion"
    } catch {
        Write-ErrorCustom "Node.js 16+ is required but not found"
        $missingTools++
    }

    # Check npm
    try {
        $npmVersion = npm --version
        Write-Success "npm installed: $npmVersion"
    } catch {
        Write-ErrorCustom "npm is required but not found"
        $missingTools++
    }

    # Check AWS CLI
    try {
        $awsVersion = aws --version
        Write-Success "AWS CLI installed: $awsVersion"
    } catch {
        Write-ErrorCustom "AWS CLI is required but not found"
        Write-Info "Install from: https://aws.amazon.com/cli/"
        $missingTools++
    }

    # Check CDK
    try {
        $cdkVersion = cdk --version
        Write-Success "AWS CDK installed: $cdkVersion"
    } catch {
        Write-Warning-Custom "AWS CDK not found. Installing..."
        npm install -g aws-cdk
        Write-Success "AWS CDK installed"
    }

    if ($missingTools -gt 0) {
        Write-ErrorCustom "Missing required tools. Please install them and try again."
        exit 1
    }

    Write-Success "All prerequisites met!"
}

################################################################################
# STEP 2: AWS Credentials Configuration
################################################################################

function Configure-AWSCredentials {
    Print-Header "STEP 2: AWS Credentials Configuration"

    # Check if AWS credentials are already configured
    try {
        $accountId = aws sts get-caller-identity --query Account --output text
        $userArn = aws sts get-caller-identity --query Arn --output text
        Write-Success "AWS credentials already configured"
        Write-Info "Account ID: $accountId"
        Write-Info "User: $userArn"

        $useExisting = Read-Host "Do you want to use these credentials? (y/n)"
        if ($useExisting -eq "n" -or $useExisting -eq "N") {
            Setup-NewCredentials
        }
    } catch {
        Write-Warning-Custom "AWS credentials not configured"
        Setup-NewCredentials
    }

    # Export for use in script
    $script:AWS_ACCOUNT_ID = aws sts get-caller-identity --query Account --output text
    $script:AWS_REGION = if ($env:AWS_REGION) { $env:AWS_REGION } else { "us-east-1" }

    Write-Success "AWS Account ID: $script:AWS_ACCOUNT_ID"
    Write-Success "AWS Region: $script:AWS_REGION"
}

function Setup-NewCredentials {
    Write-Info "Please enter your AWS credentials"

    $awsAccessKey = Read-Host "AWS Access Key ID"
    $awsSecretKey = Read-Host "AWS Secret Access Key" -AsSecureString
    $awsSecretKeyPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($awsSecretKey))
    $awsRegion = Read-Host "AWS Region [us-east-1]"
    if ([string]::IsNullOrWhiteSpace($awsRegion)) { $awsRegion = "us-east-1" }

    # Configure AWS CLI
    aws configure set aws_access_key_id $awsAccessKey
    aws configure set aws_secret_access_key $awsSecretKeyPlain
    aws configure set region $awsRegion
    aws configure set output json

    $env:AWS_REGION = $awsRegion

    # Verify credentials
    try {
        aws sts get-caller-identity | Out-Null
        Write-Success "AWS credentials configured successfully"
    } catch {
        Write-ErrorCustom "Failed to configure AWS credentials"
        exit 1
    }
}

################################################################################
# STEP 3: Check Bedrock Access
################################################################################

function Check-BedrockAccess {
    Print-Header "STEP 3: Checking Amazon Bedrock Access"

    Write-Info "Checking if Claude 3.5 Sonnet is available..."

    try {
        $models = aws bedrock list-foundation-models --region us-east-1 --query "modelSummaries[?modelId=='anthropic.claude-3-5-sonnet-20240620-v1:0']" --output text
        if ($models) {
            Write-Success "Claude 3.5 Sonnet model access confirmed"
        } else {
            throw "Model not found"
        }
    } catch {
        Write-ErrorCustom "Claude 3.5 Sonnet model access not found"
        Write-Warning-Custom "You need to request model access in AWS Console:"
        Write-Info "1. Go to AWS Console → Amazon Bedrock"
        Write-Info "2. Select region: us-east-1"
        Write-Info "3. Click 'Model access' in left sidebar"
        Write-Info "4. Click 'Request model access'"
        Write-Info "5. Enable 'Anthropic Claude 3.5 Sonnet'"
        Write-Info "6. Wait for approval (usually instant)"
        Write-Host ""
        Read-Host "Press Enter after you've enabled model access"

        # Re-check
        $models = aws bedrock list-foundation-models --region us-east-1 --query "modelSummaries[?modelId=='anthropic.claude-3-5-sonnet-20240620-v1:0']" --output text
        if ($models) {
            Write-Success "Model access confirmed!"
        } else {
            Write-ErrorCustom "Still cannot access model. Please check AWS Console."
            exit 1
        }
    }
}

################################################################################
# STEP 4: Backend Setup
################################################################################

function Setup-Backend {
    Print-Header "STEP 4: Backend Setup"

    Write-Info "Navigating to backend directory..."
    Set-Location backend

    # Create virtual environment
    Write-Info "Creating Python virtual environment..."
    python -m venv venv
    Write-Success "Virtual environment created"

    # Activate virtual environment
    Write-Info "Activating virtual environment..."
    .\venv\Scripts\Activate.ps1
    Write-Success "Virtual environment activated"

    # Upgrade pip
    Write-Info "Upgrading pip..."
    python -m pip install --upgrade pip --quiet

    # Install dependencies
    Write-Info "Installing Python dependencies (this may take a few minutes)..."
    pip install -r requirements.txt --quiet
    Write-Success "Python dependencies installed"

    # Create .env file
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
}

################################################################################
# STEP 5: CDK Bootstrap
################################################################################

function Bootstrap-CDK {
    Print-Header "STEP 5: CDK Bootstrap"

    Write-Info "Checking if CDK is already bootstrapped..."

    try {
        aws cloudformation describe-stacks --stack-name CDKToolkit --region $script:AWS_REGION | Out-Null
        Write-Success "CDK already bootstrapped in this account/region"
    } catch {
        Write-Info "Bootstrapping CDK (first-time setup)..."
        Write-Warning-Custom "This creates an S3 bucket and IAM roles for CDK deployments"

        Set-Location backend\infrastructure
        cdk bootstrap "aws://$script:AWS_ACCOUNT_ID/$script:AWS_REGION"

        if ($LASTEXITCODE -eq 0) {
            Write-Success "CDK bootstrap completed"
        } else {
            Write-ErrorCustom "CDK bootstrap failed"
            exit 1
        }

        Set-Location ..\..
    }
}

################################################################################
# STEP 6: Install CDK Dependencies
################################################################################

function Install-CDKDependencies {
    Print-Header "STEP 6: Installing CDK Dependencies"

    Set-Location backend\infrastructure

    Write-Info "Installing Node.js dependencies..."
    npm install
    Write-Success "CDK dependencies installed"

    Set-Location ..\..
}

################################################################################
# STEP 7: Synthesize CloudFormation Template
################################################################################

function Synthesize-Template {
    Print-Header "STEP 7: Synthesizing CloudFormation Template"

    Set-Location backend\infrastructure

    Write-Info "Generating CloudFormation template..."
    cdk synth | Out-Null

    if ($LASTEXITCODE -eq 0) {
        Write-Success "CloudFormation template generated successfully"
        Write-Info "Template location: backend\infrastructure\cdk.out\"
    } else {
        Write-ErrorCustom "Failed to synthesize template"
        exit 1
    }

    Set-Location ..\..
}

################################################################################
# STEP 8: Deploy Infrastructure
################################################################################

function Deploy-Infrastructure {
    Print-Header "STEP 8: Deploying Infrastructure to AWS"

    Write-Warning-Custom "This will create AWS resources in your account"
    Write-Info "Estimated deployment time: 5-10 minutes"
    Write-Info "Resources to be created:"
    Write-Info "  - Lambda Function (API)"
    Write-Info "  - API Gateway (REST API)"
    Write-Info "  - DynamoDB Tables (6 tables)"
    Write-Info "  - S3 Bucket (content storage)"
    Write-Info "  - Cognito User Pool"
    Write-Info "  - CloudWatch Dashboard"
    Write-Info "  - AWS WAF Web ACL"
    Write-Host ""

    $confirmDeploy = Read-Host "Continue with deployment? (y/n)"
    if ($confirmDeploy -ne "y" -and $confirmDeploy -ne "Y") {
        Write-Warning-Custom "Deployment cancelled"
        exit 0
    }

    Set-Location backend\infrastructure

    Write-Info "Starting deployment..."
    cdk deploy --require-approval never

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Infrastructure deployed successfully!"
    } else {
        Write-ErrorCustom "Deployment failed"
        exit 1
    }

    Set-Location ..\..
}

################################################################################
# STEP 9: Save Deployment Outputs
################################################################################

function Save-Outputs {
    Print-Header "STEP 9: Saving Deployment Outputs"

    Write-Info "Retrieving CloudFormation outputs..."

    aws cloudformation describe-stacks --stack-name SnapStudyStack --region $script:AWS_REGION --query "Stacks[0].Outputs" --output json | Out-File -FilePath deployment-outputs.json

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Outputs saved to deployment-outputs.json"

        # Extract key outputs
        $outputs = Get-Content deployment-outputs.json | ConvertFrom-Json
        $script:API_URL = ($outputs | Where-Object { $_.OutputKey -eq "RestApiUrl" }).OutputValue
        $script:USER_POOL_ID = ($outputs | Where-Object { $_.OutputKey -eq "UserPoolId" }).OutputValue
        $script:USER_POOL_CLIENT_ID = ($outputs | Where-Object { $_.OutputKey -eq "UserPoolClientId" }).OutputValue
        $script:CONTENT_BUCKET = ($outputs | Where-Object { $_.OutputKey -eq "ContentBucketName" }).OutputValue

        Write-Host ""
        Write-Success "Deployment Outputs:"
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
        Write-Host "API URL: $script:API_URL"
        Write-Host "User Pool ID: $script:USER_POOL_ID"
        Write-Host "User Pool Client ID: $script:USER_POOL_CLIENT_ID"
        Write-Host "Content Bucket: $script:CONTENT_BUCKET"
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
        Write-Host ""
    } else {
        Write-ErrorCustom "Failed to retrieve outputs"
    }
}

################################################################################
# STEP 10: Test Deployment
################################################################################

function Test-Deployment {
    Print-Header "STEP 10: Testing Deployment"

    Write-Info "Testing API health endpoint..."

    try {
        $healthResponse = Invoke-RestMethod -Uri "$script:API_URL/health" -Method Get
        Write-Success "API is healthy!"
        Write-Info "Response: $($healthResponse | ConvertTo-Json)"
    } catch {
        Write-Warning-Custom "API health check failed"
        Write-Info "Error: $_"
    }
}

################################################################################
# STEP 11: Create Test User
################################################################################

function Create-TestUser {
    Print-Header "STEP 11: Creating Test User"

    $createUser = Read-Host "Do you want to create a test user? (y/n)"
    if ($createUser -ne "y" -and $createUser -ne "Y") {
        Write-Info "Skipping test user creation"
        return
    }

    $testEmail = Read-Host "Test user email [test@example.com]"
    if ([string]::IsNullOrWhiteSpace($testEmail)) { $testEmail = "test@example.com" }

    $testPassword = Read-Host "Test user password [TestPassword123!]" -AsSecureString
    $testPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($testPassword))
    if ([string]::IsNullOrWhiteSpace($testPasswordPlain)) { $testPasswordPlain = "TestPassword123!" }

    Write-Info "Creating test user..."

    # Create user
    aws cognito-idp admin-create-user --user-pool-id $script:USER_POOL_ID --username $testEmail --user-attributes Name=email,Value=$testEmail Name=email_verified,Value=true Name=name,Value="Test User" --message-action SUPPRESS --region $script:AWS_REGION 2>&1 | Out-Null

    # Set permanent password
    aws cognito-idp admin-set-user-password --user-pool-id $script:USER_POOL_ID --username $testEmail --password $testPasswordPlain --permanent --region $script:AWS_REGION 2>&1 | Out-Null

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Test user created successfully!"
        Write-Host ""
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
        Write-Host "Test User Credentials:"
        Write-Host "Email: $testEmail"
        Write-Host "Password: $testPasswordPlain"
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
        Write-Host ""
    } else {
        Write-Warning-Custom "Failed to create test user (may already exist)"
    }
}

################################################################################
# STEP 12: Frontend Setup
################################################################################

function Setup-Frontend {
    Print-Header "STEP 12: Frontend Setup (Optional)"

    $setupFe = Read-Host "Do you want to set up the frontend? (y/n)"
    if ($setupFe -ne "y" -and $setupFe -ne "Y") {
        Write-Info "Skipping frontend setup"
        return
    }

    Set-Location frontend

    Write-Info "Installing frontend dependencies..."
    npm install
    Write-Success "Frontend dependencies installed"

    # Create .env.local
    Write-Info "Creating frontend configuration..."
    @"
REACT_APP_API_URL=$script:API_URL
REACT_APP_USER_POOL_ID=$script:USER_POOL_ID
REACT_APP_USER_POOL_CLIENT_ID=$script:USER_POOL_CLIENT_ID
REACT_APP_AWS_REGION=$script:AWS_REGION
"@ | Out-File -FilePath .env.local -Encoding utf8
    Write-Success "Frontend configuration created"

    Write-Info "Building frontend..."
    npm run build

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Frontend build completed"
        Write-Info "Build files located in: frontend\build\"
    } else {
        Write-ErrorCustom "Frontend build failed"
    }

    Set-Location ..
}

################################################################################
# STEP 13: Display Final Summary
################################################################################

function Display-Summary {
    Print-Header "🎉 DEPLOYMENT COMPLETE!"

    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "                    SnapStudy Deployment Summary" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✅ Backend Infrastructure:"
    Write-Host "   API URL: $script:API_URL"
    Write-Host "   Region: $script:AWS_REGION"
    Write-Host "   Account: $script:AWS_ACCOUNT_ID"
    Write-Host ""
    Write-Host "✅ Cognito Authentication:"
    Write-Host "   User Pool ID: $script:USER_POOL_ID"
    Write-Host "   Client ID: $script:USER_POOL_CLIENT_ID"
    Write-Host ""
    Write-Host "✅ Storage:"
    Write-Host "   S3 Bucket: $script:CONTENT_BUCKET"
    Write-Host ""
    Write-Host "📝 Next Steps:"
    Write-Host "   1. Test the API: Invoke-RestMethod -Uri $script:API_URL/health"
    Write-Host "   2. View CloudWatch Dashboard: AWS Console → CloudWatch → Dashboards"
    Write-Host "   3. Check WAF Rules: AWS Console → WAF & Shield"
    Write-Host "   4. Deploy frontend: cd frontend && npm start"
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""

    # Save summary to file
    @"
SnapStudy Deployment Summary
Generated: $(Get-Date)

API URL: $script:API_URL
User Pool ID: $script:USER_POOL_ID
User Pool Client ID: $script:USER_POOL_CLIENT_ID
Content Bucket: $script:CONTENT_BUCKET
Region: $script:AWS_REGION
Account ID: $script:AWS_ACCOUNT_ID

CloudFormation Stack: SnapStudyStack
Status: Deployed

Resources Created:
- Lambda Function: SnapStudyStack-ApiLambda
- API Gateway: SnapStudy-RestApi
- DynamoDB Tables: 6 (Users, Lessons, MicroLessons, Quizzes, UserEngagement, ChatHistory)
- S3 Bucket: $script:CONTENT_BUCKET
- Cognito User Pool: $script:USER_POOL_ID
- CloudWatch Dashboard: SnapStudy-Metrics
- AWS WAF: SnapStudyApiWaf

Next Steps:
1. Test API: Invoke-RestMethod -Uri $script:API_URL/health
2. Access CloudWatch Dashboard
3. Deploy frontend
4. Create demo video
5. Submit to hackathon

Deployment Time: $(Get-Date)
"@ | Out-File -FilePath DEPLOYMENT_SUMMARY.txt -Encoding utf8

    Write-Success "Deployment summary saved to DEPLOYMENT_SUMMARY.txt"
}

################################################################################
# MAIN EXECUTION
################################################################################

function Main {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                                                               ║" -ForegroundColor Cyan
    Write-Host "║              SnapStudy AWS Deployment Script                  ║" -ForegroundColor Cyan
    Write-Host "║                                                               ║" -ForegroundColor Cyan
    Write-Host "║  This script will deploy SnapStudy to your AWS account       ║" -ForegroundColor Cyan
    Write-Host "║                                                               ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""

    # Execute deployment steps
    Check-Prerequisites
    Configure-AWSCredentials
    Check-BedrockAccess
    Setup-Backend
    Bootstrap-CDK
    Install-CDKDependencies
    Synthesize-Template
    Deploy-Infrastructure
    Save-Outputs
    Test-Deployment
    Create-TestUser
    Setup-Frontend
    Display-Summary

    Write-Success "Deployment script completed successfully! 🎉"
}

# Run main function
Main
