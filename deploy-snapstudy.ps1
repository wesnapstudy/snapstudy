#!/usr/bin/env pwsh
<#
.SYNOPSIS
    SnapStudy Complete Deployment Script
.DESCRIPTION
    Deploys both backend and frontend components of SnapStudy platform
.PARAMETER Environment
    Target environment (dev, staging, prod)
.PARAMETER BackendOnly
    Deploy only the backend
.PARAMETER FrontendOnly
    Deploy only the frontend
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
    [switch]$BackendOnly,
    
    [Parameter(Mandatory=$false)]
    [switch]$FrontendOnly,
    
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

function Write-Header($message) {
    Write-Host ""
    Write-Host "${Cyan}$('=' * 60)${Reset}"
    Write-Host "${Cyan}$message${Reset}"
    Write-Host "${Cyan}$('=' * 60)${Reset}"
    Write-Host ""
}

function Show-DeploymentPlan {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "SnapStudy Deployment Plan" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Info "Environment: $Environment"
    Write-Info "Backend: $(if ($FrontendOnly) { 'Skip' } else { 'Deploy' })"
    Write-Info "Frontend: $(if ($BackendOnly) { 'Skip' } else { 'Deploy' })"
    Write-Info "Skip Tests: $SkipTests"
    Write-Info "Force: $Force"
    Write-Info ""
    
    if (-not $Force) {
        $confirmation = Read-Host "Do you want to proceed with this deployment plan (y/N)"
        if ($confirmation -ne "y" -and $confirmation -ne "Y") {
            Write-Info "Deployment cancelled by user"
            exit 0
        }
    }
}

function Test-Prerequisites {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "Checking Prerequisites" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    
    $missing = @()
    
    if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
        $missing += "Python"
    }
    
    if (-not (Get-Command "node" -ErrorAction SilentlyContinue)) {
        $missing += "Node.js"
    }
    
    if (-not (Get-Command "npm" -ErrorAction SilentlyContinue)) {
        $missing += "npm"
    }
    
    if (-not (Get-Command "aws" -ErrorAction SilentlyContinue)) {
        $missing += "AWS CLI"
    }
    
    if (-not (Get-Command "cdk" -ErrorAction SilentlyContinue)) {
        $missing += "AWS CDK"
    }
    
    if ($missing.Count -gt 0) {
        Write-Error "Missing prerequisites: $($missing -join ', ')"
        Write-Info "Please install the missing tools and try again"
        exit 1
    }
    
    Write-Success "All prerequisites are installed"
    
    # Check AWS credentials
    try {
        $awsIdentity = aws sts get-caller-identity --output json | ConvertFrom-Json
        Write-Success "AWS Account: $($awsIdentity.Account)"
        Write-Success "AWS User: $($awsIdentity.Arn)"
    }
    catch {
        Write-Error "AWS credentials not configured. Run: aws configure"
        exit 1
    }
}

function Deploy-Backend {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "Deploying SnapStudy Backend" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    
    $backendArgs = @(
        "-Environment", $Environment
    )
    
    if ($SkipTests) {
        $backendArgs += "-SkipTests"
    }
    
    if ($Force) {
        $backendArgs += "-Force"
    }
    
    $backendScript = Join-Path $PSScriptRoot "deploy-backend.ps1"
    if (-not (Test-Path $backendScript)) {
        Write-Error "Backend deployment script not found: $backendScript"
        exit 1
    }
    
    try {
        & $backendScript @backendArgs
        if ($LASTEXITCODE -ne 0) {
            throw "Backend deployment failed with exit code $LASTEXITCODE"
        }
        Write-Success "Backend deployment completed successfully"
        return $true
    }
    catch {
        Write-Error "Backend deployment failed: $($_.Exception.Message)"
        return $false
    }
}

function Deploy-Frontend {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "Deploying SnapStudy Frontend" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    
    $frontendArgs = @(
        "-Environment", $Environment
    )
    
    if ($Force) {
        $frontendArgs += "-Force"
    }
    
    $frontendScript = Join-Path $PSScriptRoot "deploy-frontend.ps1"
    if (-not (Test-Path $frontendScript)) {
        Write-Error "Frontend deployment script not found: $frontendScript"
        exit 1
    }
    
    try {
        & $frontendScript @frontendArgs
        if ($LASTEXITCODE -ne 0) {
            throw "Frontend deployment failed with exit code $LASTEXITCODE"
        }
        Write-Success "Frontend deployment completed successfully"
        return $true
    }
    catch {
        Write-Error "Frontend deployment failed: $($_.Exception.Message)"
        return $false
    }
}

function Show-DeploymentSummary($backendSuccess, $frontendSuccess) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "Deployment Summary" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Info "Environment: $Environment"
    Write-Info "Backend: $(if ($FrontendOnly) { 'Skipped' } elseif ($backendSuccess) { 'Success ✅' } else { 'Failed ❌' })"
    Write-Info "Frontend: $(if ($BackendOnly) { 'Skipped' } elseif ($frontendSuccess) { 'Success ✅' } else { 'Failed ❌' })"
    
    # Load deployment details
    $backendOutputs = $null
    $frontendSummary = $null
    
    if (-not $FrontendOnly) {
        $backendOutputsFile = Join-Path $PSScriptRoot "backend-outputs-$Environment.json"
        if (Test-Path $backendOutputsFile) {
            try {
                $backendOutputs = Get-Content $backendOutputsFile | ConvertFrom-Json
            }
            catch {
                Write-Warning "Could not read backend outputs"
            }
        }
    }
    
    if (-not $BackendOnly) {
        $frontendSummaryFile = Join-Path $PSScriptRoot "frontend-deployment-$Environment.json"
        if (Test-Path $frontendSummaryFile) {
            try {
                $frontendSummary = Get-Content $frontendSummaryFile | ConvertFrom-Json
            }
            catch {
                Write-Warning "Could not read frontend summary"
            }
        }
    }
    
    Write-Info ""
    Write-Info "📋 Deployment Details:"
    
    if ($backendOutputs) {
        $apiUrl = ($backendOutputs | Where-Object { $_.OutputKey -eq "RestApiUrl" }).OutputValue
        if ($apiUrl) {
            Write-Info "  Backend API: $apiUrl"
        }
    }
    
    if ($frontendSummary) {
        Write-Info "  Frontend URL: $($frontendSummary.WebsiteUrl)"
    }
    
    Write-Info ""
    
    if ($backendSuccess -and $frontendSuccess) {
        Write-Success "🎉 Complete deployment successful!"
        Write-Info ""
        Write-Info "Next steps:"
        Write-Info "1. Test the complete application functionality"
        Write-Info "2. Run integration tests"
        Write-Info "3. Set up monitoring and alerts"
        Write-Info "4. Configure custom domain (optional)"
    }
    elseif ($backendSuccess -or $frontendSuccess) {
        Write-Warning "⚠️  Partial deployment completed"
        Write-Info "Please check the errors above and retry the failed component"
    }
    else {
        Write-Error "❌ Deployment failed"
        Write-Info "Please check the errors above and retry"
        exit 1
    }
}

# Main deployment orchestration
function Start-Deployment {
    $startTime = Get-Date
    
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "SnapStudy Platform Deployment" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Info "Started at: $($startTime.ToString('yyyy-MM-dd HH:mm:ss'))"
    
    # Show deployment plan
    Show-DeploymentPlan
    
    # Check prerequisites
    Test-Prerequisites
    
    # Deploy components
    $backendSuccess = $true
    $frontendSuccess = $true
    
    if (-not $FrontendOnly) {
        $backendSuccess = Deploy-Backend
        if (-not $backendSuccess -and -not $Force) {
            Write-Error "Backend deployment failed. Stopping deployment."
            exit 1
        }
    }
    
    if (-not $BackendOnly) {
        $frontendSuccess = Deploy-Frontend
    }
    
    # Show summary
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    Show-DeploymentSummary $backendSuccess $frontendSuccess
    
    Write-Info ""
    Write-Info "Total deployment time: $($duration.ToString('mm\:ss'))"
    Write-Info "Completed at: $($endTime.ToString('yyyy-MM-dd HH:mm:ss'))"
}

# Error handling
trap {
    Write-Error "An unexpected error occurred: $($_.Exception.Message)"
    Write-Error "Stack trace: $($_.ScriptStackTrace)"
    exit 1
}

# Validate parameters
if ($BackendOnly -and $FrontendOnly) {
    Write-Error "Cannot specify both -BackendOnly and -FrontendOnly"
    exit 1
}

# Run deployment
try {
    Start-Deployment
}
catch {
    Write-Error "Deployment orchestration failed: $($_.Exception.Message)"
    exit 1
}