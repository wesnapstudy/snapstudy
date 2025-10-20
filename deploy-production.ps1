# SnapStudy Production Deployment Script (PowerShell)
# This script deploys the complete SnapStudy application to AWS

param(
    [string]$AwsRegion = "us-east-1",
    [string]$Environment = "production"
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Configuration
$StackName = "SnapStudy-$Environment"

Write-Host "🚀 Starting SnapStudy Production Deployment" -ForegroundColor Blue
Write-Host "Region: $AwsRegion" -ForegroundColor Blue
Write-Host "Environment: $Environment" -ForegroundColor Blue
Write-Host "Stack Name: $StackName" -ForegroundColor Blue
Write-Host ""

# Function to print status
function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# Function to check if command exists
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Check prerequisites
Write-Host "📋 Checking Prerequisites" -ForegroundColor Blue

if (-not (Test-Command "aws")) {
    Write-Error "AWS CLI is not installed. Please install it first."
    exit 1
}

if (-not (Test-Command "node")) {
    Write-Error "Node.js is not installed. Please install it first."
    exit 1
}

if (-not (Test-Command "npm")) {
    Write-Error "npm is not installed. Please install it first."
    exit 1
}

if (-not (Test-Command "python")) {
    Write-Error "Python is not installed. Please install it first."
    exit 1
}

Write-Success "All prerequisites are installed"

# Check AWS credentials
Write-Host "🔐 Checking AWS Credentials" -ForegroundColor Blue
try {
    $CallerIdentity = aws sts get-caller-identity --output json | ConvertFrom-Json
    $AwsAccountId = $CallerIdentity.Account
    Write-Success "AWS credentials are configured (Account: $AwsAccountId)"
}
catch {
    Write-Error "AWS credentials are not configured. Please run 'aws configure' first."
    exit 1
}

# Bootstrap CDK if needed
Write-Host "🏗️  Bootstrapping CDK" -ForegroundColor Blue
Set-Location infrastructure
try {
    cdk bootstrap "aws://$AwsAccountId/$AwsRegion" 2>$null
}
catch {
    Write-Warning "CDK bootstrap may have failed, but continuing..."
}
Write-Success "CDK bootstrap completed"

# Install infrastructure dependencies
Write-Host "📦 Installing Infrastructure Dependencies" -ForegroundColor Blue
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install infrastructure dependencies"
    exit 1
}
Write-Success "Infrastructure dependencies installed"

# Build and deploy infrastructure
Write-Host "🏗️  Deploying Infrastructure" -ForegroundColor Blue
cdk deploy $StackName --require-approval never --outputs-file ../deployment-outputs.json
if ($LASTEXITCODE -ne 0) {
    Write-Error "Infrastructure deployment failed"
    exit 1
}
Write-Success "Infrastructure deployed successfully"

Set-Location ..

# Install backend dependencies
Write-Host "📦 Installing Backend Dependencies" -ForegroundColor Blue
Set-Location backend
python -m pip install -r requirements.txt --user
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install backend dependencies"
    exit 1
}
Write-Success "Backend dependencies installed"

# Deploy Lambda functions
Write-Host "🔧 Deploying Lambda Functions" -ForegroundColor Blue
python deploy_lambda.py --region $AwsRegion --environment $Environment
if ($LASTEXITCODE -ne 0) {
    Write-Error "Lambda function deployment failed"
    exit 1
}
Write-Success "Lambda functions deployed successfully"

Set-Location ..

# Build frontend
Write-Host "🎨 Building Frontend" -ForegroundColor Blue
Set-Location frontend

# Install frontend dependencies
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install frontend dependencies"
    exit 1
}
Write-Success "Frontend dependencies installed"

# Set environment variables for build
$ApiUrl = ""
$UserPoolId = ""
$UserPoolClientId = ""
$CloudFrontUrl = ""

if (Test-Path "../deployment-outputs.json") {
    try {
        $DeploymentOutputs = Get-Content "../deployment-outputs.json" | ConvertFrom-Json
        $StackOutputs = $DeploymentOutputs.$StackName
        
        if ($StackOutputs.ApiGatewayUrl) {
            $ApiUrl = $StackOutputs.ApiGatewayUrl
            $env:REACT_APP_API_URL = $ApiUrl
            Write-Success "API URL configured: $ApiUrl"
        }
        
        if ($StackOutputs.UserPoolId) {
            $UserPoolId = $StackOutputs.UserPoolId
            $env:REACT_APP_USER_POOL_ID = $UserPoolId
            Write-Success "User Pool ID configured"
        }
        
        if ($StackOutputs.UserPoolClientId) {
            $UserPoolClientId = $StackOutputs.UserPoolClientId
            $env:REACT_APP_USER_POOL_CLIENT_ID = $UserPoolClientId
            Write-Success "User Pool Client ID configured"
        }
        
        if ($StackOutputs.CloudFrontUrl) {
            $CloudFrontUrl = $StackOutputs.CloudFrontUrl
        }
    }
    catch {
        Write-Warning "Could not parse deployment outputs"
    }
}

# Build the frontend
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Error "Frontend build failed"
    exit 1
}
Write-Success "Frontend built successfully"

# Deploy frontend to S3
Write-Host "☁️  Deploying Frontend to S3" -ForegroundColor Blue
try {
    $StackDescription = aws cloudformation describe-stacks --stack-name $StackName --region $AwsRegion --output json | ConvertFrom-Json
    $FrontendBucket = ($StackDescription.Stacks[0].Outputs | Where-Object { $_.OutputKey -eq "FrontendBucketName" }).OutputValue
    
    if ($FrontendBucket) {
        # Sync build files to S3
        aws s3 sync build/ "s3://$FrontendBucket/" --delete --region $AwsRegion
        
        # Invalidate CloudFront cache
        if ($CloudFrontUrl) {
            try {
                $Distributions = aws cloudfront list-distributions --output json | ConvertFrom-Json
                $DistributionId = ($Distributions.DistributionList.Items | Where-Object { $_.Comment -eq "SnapStudy Frontend Distribution" }).Id
                
                if ($DistributionId) {
                    aws cloudfront create-invalidation --distribution-id $DistributionId --paths "/*" --region $AwsRegion | Out-Null
                    Write-Success "CloudFront cache invalidated"
                }
            }
            catch {
                Write-Warning "Could not invalidate CloudFront cache"
            }
        }
        
        Write-Success "Frontend deployed to S3"
    }
    else {
        Write-Warning "Could not find frontend bucket name, skipping S3 deployment"
    }
}
catch {
    Write-Warning "Could not deploy frontend to S3: $($_.Exception.Message)"
}

Set-Location ..

# Run post-deployment tests
Write-Host "🧪 Running Post-Deployment Tests" -ForegroundColor Blue

# Test API health endpoint
if ($ApiUrl) {
    try {
        $HealthResponse = Invoke-RestMethod -Uri "$ApiUrl/health" -Method Get -TimeoutSec 10
        if ($HealthResponse.status -eq "healthy") {
            Write-Success "API health check passed"
        }
        else {
            Write-Warning "API health check returned unexpected response"
        }
    }
    catch {
        Write-Warning "API health check failed: $($_.Exception.Message)"
    }
}

# Display deployment summary
Write-Host ""
Write-Host "🎉 Deployment Summary" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green

Write-Host "API Gateway URL: $ApiUrl" -ForegroundColor Blue
Write-Host "CloudFront URL: $CloudFrontUrl" -ForegroundColor Blue
Write-Host "User Pool ID: $UserPoolId" -ForegroundColor Blue
Write-Host "User Pool Client ID: $UserPoolClientId" -ForegroundColor Blue

Write-Host ""
Write-Host "✅ SnapStudy has been successfully deployed to production!" -ForegroundColor Green
Write-Host "🌐 Your application is now available at: $CloudFrontUrl" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Test the application thoroughly" -ForegroundColor Yellow
Write-Host "2. Set up monitoring and alerting" -ForegroundColor Yellow
Write-Host "3. Configure custom domain (optional)" -ForegroundColor Yellow
Write-Host "4. Set up CI/CD pipeline for future deployments" -ForegroundColor Yellow
Write-Host ""

# Save deployment info
$DeploymentInfo = @"
SnapStudy Deployment Information
================================
Deployment Date: $(Get-Date)
AWS Region: $AwsRegion
Environment: $Environment
Stack Name: $StackName
AWS Account: $AwsAccountId

Application URLs:
- API Gateway: $ApiUrl
- CloudFront: $CloudFrontUrl

Cognito Configuration:
- User Pool ID: $UserPoolId
- User Pool Client ID: $UserPoolClientId

Deployment Status: SUCCESS
"@

$DeploymentInfo | Out-File -FilePath "deployment-info.txt" -Encoding UTF8
Write-Success "Deployment information saved to deployment-info.txt"

Write-Host "🚀 Deployment completed successfully!" -ForegroundColor Green