#!/usr/bin/env pwsh
param(
    [string]$Environment = "dev",
    [string]$ApiUrl = "https://hc3av6xdja.execute-api.us-east-1.amazonaws.com/prod/",
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
Write-Host "SnapStudy Frontend Deployment" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Info "Environment: $Environment"
Write-Info "API URL: $ApiUrl"
Write-Info "Force: $Force"

# Check prerequisites
Write-Info "Checking prerequisites..."

if (-not (Get-Command "node" -ErrorAction SilentlyContinue)) {
    Write-Error "Node.js is not installed or not in PATH"
    exit 1
}

if (-not (Get-Command "npm" -ErrorAction SilentlyContinue)) {
    Write-Error "npm is not installed or not in PATH"
    exit 1
}

if (-not (Get-Command "aws" -ErrorAction SilentlyContinue)) {
    Write-Error "AWS CLI is not installed or not in PATH"
    exit 1
}

Write-Success "Prerequisites check passed"

# Verify AWS credentials
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

# Navigate to frontend directory
$frontendPath = Join-Path $PSScriptRoot "frontend"
if (-not (Test-Path $frontendPath)) {
    Write-Error "Frontend directory not found: $frontendPath"
    exit 1
}

Set-Location $frontendPath
Write-Info "Working directory: $(Get-Location)"

# Create environment file
Write-Info "Creating environment configuration..."
$envContent = @"
REACT_APP_API_URL=$ApiUrl
REACT_APP_ENVIRONMENT=$Environment
REACT_APP_VERSION=1.0.0
GENERATE_SOURCEMAP=false
"@

$envFile = Join-Path $frontendPath ".env.production"
$envContent | Out-File -FilePath $envFile -Encoding UTF8
Write-Success "Created environment file: $envFile"

# Install dependencies
Write-Info "Installing frontend dependencies..."
try {
    npm install
    if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
    Write-Success "Frontend dependencies installed"
}
catch {
    Write-Error "Failed to install frontend dependencies: $($_.Exception.Message)"
    exit 1
}

# Build the application
Write-Info "Building React application..."
try {
    npm run build
    if ($LASTEXITCODE -ne 0) { throw "npm build failed" }
    Write-Success "Build completed successfully"
}
catch {
    Write-Error "Failed to build React application: $($_.Exception.Message)"
    exit 1
}

# Verify build directory exists
$buildPath = Join-Path $frontendPath "build"
if (-not (Test-Path $buildPath)) {
    Write-Error "Build directory not found: $buildPath"
    exit 1
}

# Get S3 bucket name
$bucketName = "snapstudy-frontend-054037102331-us-east-1"
Write-Success "S3 Bucket: $bucketName"

# Verify S3 bucket exists
Write-Info "Verifying S3 bucket exists..."
try {
    aws s3 ls "s3://$bucketName" | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "S3 bucket not accessible" }
    Write-Success "S3 bucket exists and is accessible"
}
catch {
    Write-Error "S3 bucket '$bucketName' does not exist or is not accessible"
    Write-Info "Make sure the backend is deployed first"
    exit 1
}

# Confirmation
if (-not $Force) {
    Write-Warning "This will deploy the frontend to S3 bucket: $bucketName"
    $confirmation = Read-Host "Do you want to continue (y/N)"
    if ($confirmation -ne "y" -and $confirmation -ne "Y") {
        Write-Info "Deployment cancelled by user"
        exit 0
    }
}

# Deploy to S3
Write-Info "Deploying to S3..."
try {
    # Sync static assets with long cache
    aws s3 sync build/ "s3://$bucketName" --delete --cache-control "max-age=31536000" --exclude "*.html" --exclude "service-worker.js"
    if ($LASTEXITCODE -ne 0) { throw "S3 sync static assets failed" }
    
    # Sync HTML files with no cache
    aws s3 sync build/ "s3://$bucketName" --delete --cache-control "no-cache" --include "*.html" --include "service-worker.js"
    if ($LASTEXITCODE -ne 0) { throw "S3 sync HTML files failed" }
    
    Write-Success "Files deployed to S3 successfully"
}
catch {
    Write-Error "Failed to deploy to S3: $($_.Exception.Message)"
    exit 1
}

# Set website configuration
Write-Info "Configuring S3 website..."
try {
    aws s3 website "s3://$bucketName" --index-document index.html --error-document index.html
    if ($LASTEXITCODE -ne 0) { throw "S3 website configuration failed" }
    Write-Success "S3 website configuration updated"
}
catch {
    Write-Warning "Could not update S3 website configuration: $($_.Exception.Message)"
}

# Get website URL
$websiteUrl = "http://$bucketName.s3-website-us-east-1.amazonaws.com"

# Test deployment
Write-Info "Testing deployment..."
try {
    $response = Invoke-WebRequest -Uri $websiteUrl -Method GET -TimeoutSec 30
    if ($response.StatusCode -eq 200) {
        Write-Success "Frontend deployment test passed"
    }
}
catch {
    Write-Warning "Frontend deployment test failed: $($_.Exception.Message)"
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Frontend Deployment Complete" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Success "Frontend deployment completed successfully!"
Write-Info ""
Write-Info "Deployment Summary:"
Write-Info "  Environment: $Environment"
Write-Info "  API URL: $ApiUrl"
Write-Info "  S3 Bucket: $bucketName"
Write-Info "  Website URL: $websiteUrl"
Write-Info ""
Write-Success "Access your application at: $websiteUrl"
Write-Info ""
Write-Info "Next steps:"
Write-Info "1. Test the complete application functionality"
Write-Info "2. Set up CloudFront distribution for production (optional)"
Write-Info "3. Configure custom domain (optional)"
Write-Info "4. Set up monitoring and alerts"

# Return to original directory
Set-Location $PSScriptRoot