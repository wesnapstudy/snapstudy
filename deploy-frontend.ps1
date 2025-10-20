#!/usr/bin/env pwsh
<#
.SYNOPSIS
    SnapStudy Frontend Deployment Script
.DESCRIPTION
    Builds and deploys the SnapStudy React frontend to AWS S3 + CloudFront
.PARAMETER Environment
    Target environment (dev, staging, prod)
.PARAMETER ApiUrl
    Backend API URL (if not provided, will try to get from backend outputs)
.PARAMETER SkipBuild
    Skip the build process and deploy existing build
.PARAMETER Force
    Force deployment without confirmation
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("dev", "staging", "prod")]
    [string]$Environment = "dev",
    
    [Parameter(Mandatory=$false)]
    [string]$ApiUrl,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipBuild,
    
    [Parameter(Mandatory=$false)]
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

function Test-Command($command) {
    $null = Get-Command $command -ErrorAction SilentlyContinue
    return $?
}

function Invoke-SafeCommand($command, $description) {
    Write-Info $description
    try {
        Invoke-Expression $command
        if ($LASTEXITCODE -ne 0) {
            throw "Command failed with exit code $LASTEXITCODE"
        }
        return $true
    }
    catch {
        Write-Error "Failed: $description - $($_.Exception.Message)"
        return $false
    }
}

function Get-BackendApiUrl($environment) {
    $outputsFile = Join-Path $PSScriptRoot "backend-outputs-$environment.json"
    if (Test-Path $outputsFile) {
        try {
            $outputs = Get-Content $outputsFile | ConvertFrom-Json
            $apiOutput = $outputs | Where-Object { $_.OutputKey -eq "RestApiUrl" }
            if ($apiOutput) {
                return $apiOutput.OutputValue
            }
        }
        catch {
            Write-Warning "Could not read backend outputs file: $outputsFile"
        }
    }
    
    # Try to get from CloudFormation directly
    try {
        $outputs = aws cloudformation describe-stacks --stack-name SnapStudyStack --query "Stacks[0].Outputs" --output json | ConvertFrom-Json
        $apiOutput = $outputs | Where-Object { $_.OutputKey -eq "RestApiUrl" }
        if ($apiOutput) {
            return $apiOutput.OutputValue
        }
    }
    catch {
        Write-Warning "Could not retrieve API URL from CloudFormation"
    }
    
    return $null
}

function Create-EnvFile($apiUrl, $environment) {
    $envContent = @"
# SnapStudy Frontend Environment Variables
REACT_APP_API_URL=$apiUrl
REACT_APP_ENVIRONMENT=$environment
REACT_APP_VERSION=1.0.0
GENERATE_SOURCEMAP=false
"@
    
    $envFile = Join-Path $frontendPath ".env.production"
    $envContent | Out-File -FilePath $envFile -Encoding UTF8
    Write-Success "Created environment file: $envFile"
}

function Get-S3BucketName($environment) {
    try {
        $outputs = aws cloudformation describe-stacks --stack-name SnapStudyStack --query "Stacks[0].Outputs" --output json | ConvertFrom-Json
        $bucketOutput = $outputs | Where-Object { $_.OutputKey -eq "FrontendBucketName" }
        if ($bucketOutput) {
            return $bucketOutput.OutputValue
        }
    }
    catch {
        Write-Warning "Could not retrieve S3 bucket name from CloudFormation"
    }
    
    # Fallback to constructed name
    $awsIdentity = aws sts get-caller-identity --output json | ConvertFrom-Json
    return "snapstudy-frontend-$($awsIdentity.Account)-us-east-1"
}

# Main deployment function
function Deploy-Frontend {
    Write-Info "🚀 Starting SnapStudy Frontend Deployment"
    Write-Info "Environment: $Environment"
    Write-Info "Skip Build: $SkipBuild"
    
    # Check prerequisites
    Write-Info "Checking prerequisites..."
    
    if (-not (Test-Command "node")) {
        Write-Error "Node.js is not installed or not in PATH"
        exit 1
    }
    
    if (-not (Test-Command "npm")) {
        Write-Error "npm is not installed or not in PATH"
        exit 1
    }
    
    if (-not (Test-Command "aws")) {
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
    $script:frontendPath = Join-Path $PSScriptRoot "frontend"
    if (-not (Test-Path $frontendPath)) {
        Write-Error "Frontend directory not found: $frontendPath"
        exit 1
    }
    
    Set-Location $frontendPath
    Write-Info "Working directory: $(Get-Location)"
    
    # Get API URL
    if (-not $ApiUrl) {
        Write-Info "Getting backend API URL..."
        $ApiUrl = Get-BackendApiUrl $Environment
        if (-not $ApiUrl) {
            Write-Error "Could not determine backend API URL. Please provide it with -ApiUrl parameter"
            exit 1
        }
    }
    
    Write-Success "Backend API URL: $ApiUrl"
    
    # Create environment file
    Create-EnvFile $ApiUrl $Environment
    
    # Install dependencies
    if (-not $SkipBuild) {
        Write-Info "Installing frontend dependencies..."
        if (-not (Invoke-SafeCommand "npm install" "Installing frontend dependencies")) {
            exit 1
        }
        
        # Run tests
        Write-Info "Running frontend tests..."
        if (Test-Path "src/__tests__") {
            if (-not (Invoke-SafeCommand "npm test -- --coverage --watchAll=false" "Running frontend tests")) {
                Write-Warning "Tests failed, but continuing deployment..."
            }
        } else {
            Write-Warning "No tests found, skipping tests"
        }
        
        # Build the application
        Write-Info "Building React application..."
        if (-not (Invoke-SafeCommand "npm run build" "Building React application")) {
            exit 1
        }
        
        Write-Success "Build completed successfully"
    } else {
        Write-Info "Skipping build process"
    }
    
    # Verify build directory exists
    $buildPath = Join-Path $frontendPath "build"
    if (-not (Test-Path $buildPath)) {
        Write-Error "Build directory not found: $buildPath. Run without -SkipBuild flag."
        exit 1
    }
    
    # Get S3 bucket name
    Write-Info "Getting S3 bucket name..."
    $bucketName = Get-S3BucketName $Environment
    Write-Success "S3 Bucket: $bucketName"
    
    # Verify S3 bucket exists
    try {
        aws s3 ls "s3://$bucketName" | Out-Null
        Write-Success "S3 bucket exists and is accessible"
    }
    catch {
        Write-Error "S3 bucket '$bucketName' does not exist or is not accessible"
        Write-Info "Make sure the backend is deployed first"
        exit 1
    }
    
    # Confirmation prompt
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
    $syncCommand = "aws s3 sync build/ s3://$bucketName --delete --cache-control 'max-age=31536000' --exclude '*.html' --exclude 'service-worker.js'"
    if (-not (Invoke-SafeCommand $syncCommand "Syncing static assets to S3")) {
        exit 1
    }
    
    # Deploy HTML files with no-cache
    Write-Info "Deploying HTML files with no-cache..."
    $htmlCommand = "aws s3 sync build/ s3://$bucketName --delete --cache-control 'no-cache' --include '*.html' --include 'service-worker.js'"
    if (-not (Invoke-SafeCommand $htmlCommand "Syncing HTML files to S3")) {
        exit 1
    }
    
    # Set website configuration
    Write-Info "Configuring S3 website..."
    $websiteConfig = @{
        IndexDocument = @{ Suffix = "index.html" }
        ErrorDocument = @{ Key = "index.html" }
    } | ConvertTo-Json -Depth 10
    
    $tempConfigFile = [System.IO.Path]::GetTempFileName()
    $websiteConfig | Out-File -FilePath $tempConfigFile -Encoding UTF8
    
    try {
        aws s3api put-bucket-website --bucket $bucketName --website-configuration "file://$tempConfigFile"
        Write-Success "S3 website configuration updated"
    }
    catch {
        Write-Warning "Could not update S3 website configuration: $($_.Exception.Message)"
    }
    finally {
        Remove-Item $tempConfigFile -Force -ErrorAction SilentlyContinue
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
    
    # Create deployment summary
    $deploymentSummary = @{
        Environment = $Environment
        ApiUrl = $ApiUrl
        S3Bucket = $bucketName
        WebsiteUrl = $websiteUrl
        DeploymentTime = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss UTC")
    }
    
    $summaryFile = Join-Path $PSScriptRoot "frontend-deployment-$Environment.json"
    $deploymentSummary | ConvertTo-Json -Depth 10 | Out-File -FilePath $summaryFile -Encoding UTF8
    
    Write-Success "🎉 Frontend deployment completed!"
    Write-Info ""
    Write-Info "📋 Deployment Summary:"
    Write-Info "  Environment: $Environment"
    Write-Info "  API URL: $ApiUrl"
    Write-Info "  S3 Bucket: $bucketName"
    Write-Info "  Website URL: $websiteUrl"
    Write-Info "  Summary saved to: $summaryFile"
    Write-Info ""
    Write-Info "🌐 Access your application at: $websiteUrl"
    Write-Info ""
    Write-Info "Next steps:"
    Write-Info "1. Test the complete application functionality"
    Write-Info "2. Set up CloudFront distribution for production (optional)"
    Write-Info "3. Configure custom domain (optional)"
    Write-Info "4. Set up monitoring and alerts"
}

# Error handling
trap {
    Write-Error "An unexpected error occurred: $($_.Exception.Message)"
    Write-Error "Stack trace: $($_.ScriptStackTrace)"
    exit 1
}

# Run deployment
try {
    Deploy-Frontend
}
catch {
    Write-Error "Deployment failed: $($_.Exception.Message)"
    exit 1
}
finally {
    # Return to original directory
    Set-Location $PSScriptRoot
}