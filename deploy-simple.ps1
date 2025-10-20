#!/usr/bin/env pwsh
param(
    [string]$Environment = "dev",
    [switch]$Force
)

function Write-Info($message) {
    Write-Host "INFO: $message" -ForegroundColor Blue
}

function Write-Success($message) {
    Write-Host "SUCCESS: $message" -ForegroundColor Green
}

function Write-Warning($message) {
    Write-Host "WARNING: $message" -ForegroundColor Yellow
}

function Write-Error($message) {
    Write-Host "ERROR: $message" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "SnapStudy Platform Deployment" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Info "Environment: $Environment"
Write-Info "Force: $Force"

# Check prerequisites
Write-Info "Checking prerequisites..."

if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not installed or not in PATH"
    exit 1
}

if (-not (Get-Command "aws" -ErrorAction SilentlyContinue)) {
    Write-Error "AWS CLI is not installed or not in PATH"
    exit 1
}

if (-not (Get-Command "cdk" -ErrorAction SilentlyContinue)) {
    Write-Error "AWS CDK is not installed. Run: npm install -g aws-cdk"
    exit 1
}

Write-Success "Prerequisites check passed"

# Check AWS credentials
Write-Info "Verifying AWS credentials..."
try {
    $awsIdentity = aws sts get-caller-identity --output json | ConvertFrom-Json
    Write-Success "AWS Account: $($awsIdentity.Account)"
    Write-Success "AWS User: $($awsIdentity.Arn)"
}
catch {
    Write-Error "AWS credentials not configured. Run: aws configure"
    exit 1
}

# Confirmation
if (-not $Force) {
    Write-Warning "This will deploy SnapStudy to AWS account $($awsIdentity.Account)"
    $confirmation = Read-Host "Do you want to continue (y/N)"
    if ($confirmation -ne "y" -and $confirmation -ne "Y") {
        Write-Info "Deployment cancelled by user"
        exit 0
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Deploying Backend" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to backend directory
$backendPath = Join-Path $PSScriptRoot "backend"
if (-not (Test-Path $backendPath)) {
    Write-Error "Backend directory not found: $backendPath"
    exit 1
}

Set-Location $backendPath
Write-Info "Working directory: $(Get-Location)"

# Install Python dependencies
Write-Info "Installing Python dependencies..."
try {
    python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw "pip install failed" }
    Write-Success "Backend dependencies installed"
}
catch {
    Write-Error "Failed to install backend dependencies: $($_.Exception.Message)"
    exit 1
}

# Navigate to infrastructure directory
$infraPath = Join-Path $backendPath "infrastructure"
if (-not (Test-Path $infraPath)) {
    Write-Error "Infrastructure directory not found: $infraPath"
    exit 1
}

Set-Location $infraPath

# Install CDK dependencies
Write-Info "Installing CDK dependencies..."
try {
    python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw "CDK pip install failed" }
    Write-Success "CDK dependencies installed"
}
catch {
    Write-Error "Failed to install CDK dependencies: $($_.Exception.Message)"
    exit 1
}

# Set environment variables
$env:ENVIRONMENT = $Environment
$env:AWS_REGION = "us-east-1"

# Load .env file if exists
$envFile = Join-Path (Join-Path $PSScriptRoot "infrastructure") ".env"
if (Test-Path $envFile) {
    Write-Info "Loading environment variables from .env file..."
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2])
        }
    }
}

# CDK Bootstrap check
Write-Info "Checking CDK bootstrap status..."
try {
    cdk bootstrap
    if ($LASTEXITCODE -ne 0) { throw "CDK bootstrap failed" }
    Write-Success "CDK bootstrap completed"
}
catch {
    Write-Warning "CDK bootstrap had issues, but continuing..."
}

# CDK Synth
Write-Info "Synthesizing CloudFormation template..."
try {
    cdk synth
    if ($LASTEXITCODE -ne 0) { throw "CDK synth failed" }
    Write-Success "CDK synthesis completed"
}
catch {
    Write-Error "Failed to synthesize CDK template: $($_.Exception.Message)"
    exit 1
}

# Deploy the stack
Write-Info "Deploying SnapStudy backend infrastructure..."
try {
    cdk deploy --require-approval never
    if ($LASTEXITCODE -ne 0) { throw "CDK deploy failed" }
    Write-Success "Backend deployment completed"
}
catch {
    Write-Error "Backend deployment failed: $($_.Exception.Message)"
    exit 1
}

# Get stack outputs
Write-Info "Retrieving stack outputs..."
try {
    $stackName = "SnapStudyStack"
    $outputs = aws cloudformation describe-stacks --stack-name $stackName --query "Stacks[0].Outputs" --output json | ConvertFrom-Json
    
    Write-Success "Backend deployment completed successfully!"
    Write-Info ""
    Write-Info "Stack Outputs:"
    foreach ($output in $outputs) {
        Write-Info "  $($output.OutputKey): $($output.OutputValue)"
    }
    
    # Save outputs to file
    $outputsFile = Join-Path $PSScriptRoot "backend-outputs-$Environment.json"
    $outputs | ConvertTo-Json -Depth 10 | Out-File -FilePath $outputsFile -Encoding UTF8
    Write-Success "Outputs saved to: $outputsFile"
}
catch {
    Write-Warning "Could not retrieve stack outputs: $($_.Exception.Message)"
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Deployment Complete" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Success "SnapStudy backend deployed successfully!"
Write-Info "Next steps:"
Write-Info "1. Note down the API Gateway URL from outputs above"
Write-Info "2. Deploy frontend using: ./deploy-frontend.ps1"
Write-Info "3. Test the complete application"

# Return to original directory
Set-Location $PSScriptRoot