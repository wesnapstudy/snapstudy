#!/usr/bin/env pwsh
<#
.SYNOPSIS
    SnapStudy Backend Deployment Script
.DESCRIPTION
    Deploys the SnapStudy backend infrastructure and Lambda functions to AWS
.PARAMETER Environment
    Target environment (dev, staging, prod)
.PARAMETER SkipTests
    Skip running tests before deployment
.PARAMETER Force
    Force deployment without confirmation
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("dev", "staging", "prod")]
    [string]$Environment = "dev",
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipTests,
    
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

# Main deployment function
function Deploy-Backend {
    Write-Info "🚀 Starting SnapStudy Backend Deployment"
    Write-Info "Environment: $Environment"
    Write-Info "Skip Tests: $SkipTests"
    
    # Check prerequisites
    Write-Info "Checking prerequisites..."
    
    if (-not (Test-Command "python")) {
        Write-Error "Python is not installed or not in PATH"
        exit 1
    }
    
    if (-not (Test-Command "aws")) {
        Write-Error "AWS CLI is not installed or not in PATH"
        exit 1
    }
    
    if (-not (Test-Command "cdk")) {
        Write-Error "AWS CDK is not installed. Run: npm install -g aws-cdk"
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
    if (-not (Invoke-SafeCommand "pip install -r requirements.txt" "Installing backend dependencies")) {
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
    if (-not (Invoke-SafeCommand "pip install -r requirements.txt" "Installing CDK dependencies")) {
        exit 1
    }
    
    # Run tests if not skipped
    if (-not $SkipTests) {
        Write-Info "Running backend tests..."
        Set-Location $backendPath
        if (Test-Path "tests") {
            if (-not (Invoke-SafeCommand "python -m pytest tests/ -v" "Running backend tests")) {
                Write-Warning "Tests failed, but continuing deployment..."
            }
        } else {
            Write-Warning "No tests directory found, skipping tests"
        }
        Set-Location $infraPath
    }
    
    # Set environment variables
    Write-Info "Setting environment variables..."
    $env:ENVIRONMENT = $Environment
    $env:AWS_REGION = "us-east-1"
    
    # Load .env file if exists
    $envFile = Join-Path $PSScriptRoot "infrastructure" ".env"
    if (Test-Path $envFile) {
        Write-Info "Loading environment variables from .env file..."
        Get-Content $envFile | ForEach-Object {
            if ($_ -match "^([^#][^=]+)=(.*)$") {
                [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2])
            }
        }
    }
    
    # CDK Bootstrap (if needed)
    Write-Info "Checking CDK bootstrap status..."
    try {
        $bootstrapCheck = cdk list 2>&1
        if ($bootstrapCheck -match "not bootstrapped") {
            Write-Info "Bootstrapping CDK..."
            if (-not (Invoke-SafeCommand "cdk bootstrap" "CDK Bootstrap")) {
                exit 1
            }
        } else {
            Write-Success "CDK already bootstrapped"
        }
    }
    catch {
        Write-Info "Bootstrapping CDK..."
        if (-not (Invoke-SafeCommand "cdk bootstrap" "CDK Bootstrap")) {
            exit 1
        }
    }
    
    # CDK Synth
    Write-Info "Synthesizing CloudFormation template..."
    if (-not (Invoke-SafeCommand "cdk synth" "CDK Synthesis")) {
        exit 1
    }
    
    # Show deployment plan
    Write-Info "Showing deployment differences..."
    cdk diff
    
    # Confirmation prompt
    if (-not $Force) {
        Write-Warning "This will deploy the SnapStudy backend to AWS account $($awsIdentity.Account)"
        $confirmation = Read-Host "Do you want to continue (y/N)"
        if ($confirmation -ne "y" -and $confirmation -ne "Y") {
            Write-Info "Deployment cancelled by user"
            exit 0
        }
    }
    
    # Deploy the stack
    Write-Info "Deploying SnapStudy backend infrastructure..."
    $deployCommand = "cdk deploy --require-approval never"
    if ($Environment -eq "prod") {
        $deployCommand += " --no-rollback"
    }
    
    if (-not (Invoke-SafeCommand $deployCommand "CDK Deployment")) {
        Write-Error "Deployment failed"
        exit 1
    }
    
    # Get stack outputs
    Write-Info "Retrieving stack outputs..."
    try {
        $stackName = "SnapStudyStack"
        $outputs = aws cloudformation describe-stacks --stack-name $stackName --query "Stacks[0].Outputs" --output json | ConvertFrom-Json
        
        Write-Success "Deployment completed successfully!"
        Write-Info ""
        Write-Info "📋 Stack Outputs:"
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
    
    # Validate deployment
    Write-Info "Validating deployment..."
    try {
        $apiUrl = ($outputs | Where-Object { $_.OutputKey -eq "RestApiUrl" }).OutputValue
        if ($apiUrl) {
            Write-Info "Testing API endpoint: $apiUrl"
            $response = Invoke-RestMethod -Uri "$apiUrl/health" -Method GET -TimeoutSec 30
            Write-Success "API health check passed"
        }
    }
    catch {
        Write-Warning "API health check failed: $($_.Exception.Message)"
    }
    
    Write-Success "🎉 Backend deployment completed!"
    Write-Info ""
    Write-Info "Next steps:"
    Write-Info "1. Note down the API Gateway URL from outputs above"
    Write-Info "2. Update frontend configuration with the new API URL"
    Write-Info "3. Deploy frontend using: ./deploy-frontend.ps1"
    Write-Info "4. Test the complete application"
}

# Error handling
trap {
    Write-Error "An unexpected error occurred: $($_.Exception.Message)"
    Write-Error "Stack trace: $($_.ScriptStackTrace)"
    exit 1
}

# Run deployment
try {
    Deploy-Backend
}
catch {
    Write-Error "Deployment failed: $($_.Exception.Message)"
    exit 1
}
finally {
    # Return to original directory
    Set-Location $PSScriptRoot
}