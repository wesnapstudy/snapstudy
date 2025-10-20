# Amazon Q Setup Helper Script for SnapStudy
# This script helps configure Amazon Q Business and Bedrock Guardrails

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "        SnapStudy Amazon Q Setup Helper" -ForegroundColor Cyan
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

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

# Step 1: Check Prerequisites
Write-Step "Step 1: Checking Prerequisites"

try {
    $awsVersion = aws --version
    Write-Success "AWS CLI: $awsVersion"
} catch {
    Write-Error-Custom "AWS CLI not found. Please install AWS CLI first."
    exit 1
}

try {
    $identity = aws sts get-caller-identity | ConvertFrom-Json
    Write-Success "AWS Account: $($identity.Account)"
    Write-Success "AWS User: $($identity.Arn)"
} catch {
    Write-Error-Custom "AWS credentials not configured. Run 'aws configure' first."
    exit 1
}

# Step 2: Check Current Q Business Setup
Write-Step "Step 2: Checking Amazon Q Business Status"

try {
    $qApps = aws qbusiness list-applications --output json 2>&1
    
    if ($qApps -match "error" -or $qApps -match "Unable") {
        Write-Warning-Custom "Amazon Q Business not available or not configured"
        Write-Info "This could be because:"
        Write-Info "  1. Q Business is not available in your region"
        Write-Info "  2. You don't have permissions to access Q Business"
        Write-Info "  3. Q Business is not enabled for your account"
        Write-Info ""
        
        $setupQ = Read-Host "Would you like guidance on setting up Q Business? (y/n)"
        if ($setupQ -eq 'y' -or $setupQ -eq 'Y') {
            Write-Info "Please follow these steps to set up Amazon Q Business:"
            Write-Info ""
            Write-Info "1. Go to AWS Console: https://console.aws.amazon.com/q/business"
            Write-Info "2. Click 'Create application'"
            Write-Info "3. Choose 'Create with quick start'"
            Write-Info "4. Application name: SnapStudy-Educational-Assistant"
            Write-Info "5. Follow the setup wizard"
            Write-Info "6. Note the Application ID for configuration"
            Write-Info ""
            Write-Info "After setup, run this script again to continue."
            
            $openConsole = Read-Host "Open Q Business console in browser? (y/n)"
            if ($openConsole -eq 'y' -or $openConsole -eq 'Y') {
                Start-Process "https://console.aws.amazon.com/q/business"
            }
        }
    } else {
        $qAppsData = $qApps | ConvertFrom-Json
        if ($qAppsData.applications -and $qAppsData.applications.Count -gt 0) {
            Write-Success "Found $($qAppsData.applications.Count) Q Business application(s)"
            
            Write-Info "Available Q Business Applications:"
            foreach ($app in $qAppsData.applications) {
                Write-Info "  - Name: $($app.displayName)"
                Write-Info "    ID: $($app.applicationId)"
                Write-Info "    Status: $($app.status)"
                Write-Info ""
            }
            
            # Ask user to select application
            if ($qAppsData.applications.Count -eq 1) {
                $selectedApp = $qAppsData.applications[0]
                Write-Info "Using application: $($selectedApp.displayName)"
            } else {
                Write-Info "Multiple applications found. Please select one:"
                for ($i = 0; $i -lt $qAppsData.applications.Count; $i++) {
                    Write-Host "  $($i + 1). $($qAppsData.applications[$i].displayName)"
                }
                
                do {
                    $selection = Read-Host "Enter selection (1-$($qAppsData.applications.Count))"
                    $selectionIndex = [int]$selection - 1
                } while ($selectionIndex -lt 0 -or $selectionIndex -ge $qAppsData.applications.Count)
                
                $selectedApp = $qAppsData.applications[$selectionIndex]
            }
            
            $script:Q_BUSINESS_APP_ID = $selectedApp.applicationId
            Write-Success "Selected Q Business Application ID: $script:Q_BUSINESS_APP_ID"
        } else {
            Write-Warning-Custom "No Q Business applications found"
            Write-Info "Please create a Q Business application first"
        }
    }
} catch {
    Write-Warning-Custom "Could not check Q Business status: $_"
}

# Step 3: Check Bedrock Guardrails
Write-Step "Step 3: Checking Bedrock Guardrails Status"

try {
    $guardrails = aws bedrock list-guardrails --output json 2>&1
    
    if ($guardrails -match "error" -or $guardrails -match "Unable") {
        Write-Warning-Custom "Bedrock Guardrails not available or not configured"
        Write-Info "This could be because:"
        Write-Info "  1. Bedrock is not available in your region"
        Write-Info "  2. You don't have permissions to access Bedrock"
        Write-Info "  3. Guardrails feature is not enabled"
        Write-Info ""
        
        $setupGuardrails = Read-Host "Would you like guidance on setting up Bedrock Guardrails? (y/n)"
        if ($setupGuardrails -eq 'y' -or $setupGuardrails -eq 'Y') {
            Write-Info "Please follow these steps to set up Bedrock Guardrails:"
            Write-Info ""
            Write-Info "1. Go to AWS Console: https://console.aws.amazon.com/bedrock"
            Write-Info "2. Click 'Guardrails' in the left sidebar"
            Write-Info "3. Click 'Create guardrail'"
            Write-Info "4. Name: SnapStudy-Educational-Content-Filter"
            Write-Info "5. Configure content filters for educational safety"
            Write-Info "6. Add denied topics for non-educational content"
            Write-Info "7. Create and note the Guardrail ID"
            Write-Info ""
            
            $openBedrock = Read-Host "Open Bedrock console in browser? (y/n)"
            if ($openBedrock -eq 'y' -or $openBedrock -eq 'Y') {
                Start-Process "https://console.aws.amazon.com/bedrock"
            }
        }
    } else {
        $guardrailsData = $guardrails | ConvertFrom-Json
        if ($guardrailsData.guardrails -and $guardrailsData.guardrails.Count -gt 0) {
            Write-Success "Found $($guardrailsData.guardrails.Count) Bedrock Guardrail(s)"
            
            Write-Info "Available Bedrock Guardrails:"
            foreach ($guardrail in $guardrailsData.guardrails) {
                Write-Info "  - Name: $($guardrail.name)"
                Write-Info "    ID: $($guardrail.id)"
                Write-Info "    Status: $($guardrail.status)"
                Write-Info ""
            }
            
            # Ask user to select guardrail
            if ($guardrailsData.guardrails.Count -eq 1) {
                $selectedGuardrail = $guardrailsData.guardrails[0]
                Write-Info "Using guardrail: $($selectedGuardrail.name)"
            } else {
                Write-Info "Multiple guardrails found. Please select one:"
                for ($i = 0; $i -lt $guardrailsData.guardrails.Count; $i++) {
                    Write-Host "  $($i + 1). $($guardrailsData.guardrails[$i].name)"
                }
                
                do {
                    $selection = Read-Host "Enter selection (1-$($guardrailsData.guardrails.Count))"
                    $selectionIndex = [int]$selection - 1
                } while ($selectionIndex -lt 0 -or $selectionIndex -ge $guardrailsData.guardrails.Count)
                
                $selectedGuardrail = $guardrailsData.guardrails[$selectionIndex]
            }
            
            $script:BEDROCK_GUARDRAIL_ID = $selectedGuardrail.id
            Write-Success "Selected Bedrock Guardrail ID: $script:BEDROCK_GUARDRAIL_ID"
        } else {
            Write-Warning-Custom "No Bedrock Guardrails found"
            Write-Info "Please create a Bedrock Guardrail for content safety"
        }
    }
} catch {
    Write-Warning-Custom "Could not check Bedrock Guardrails status: $_"
}

# Step 4: Update Configuration
Write-Step "Step 4: Updating SnapStudy Configuration"

$envFilePath = "backend\.env"

if (Test-Path $envFilePath) {
    Write-Info "Found existing .env file"
    
    # Read current .env file
    $envContent = Get-Content $envFilePath -Raw
    
    # Update Q Business configuration
    if ($script:Q_BUSINESS_APP_ID) {
        if ($envContent -match "Q_BUSINESS_APPLICATION_ID=") {
            $envContent = $envContent -replace "# Q_BUSINESS_APPLICATION_ID=.*", "Q_BUSINESS_APPLICATION_ID=$script:Q_BUSINESS_APP_ID"
            $envContent = $envContent -replace "Q_BUSINESS_APPLICATION_ID=.*", "Q_BUSINESS_APPLICATION_ID=$script:Q_BUSINESS_APP_ID"
        } else {
            $envContent += "`nQ_BUSINESS_APPLICATION_ID=$script:Q_BUSINESS_APP_ID"
        }
        Write-Success "Updated Q Business Application ID in .env file"
    }
    
    # Update Guardrail configuration
    if ($script:BEDROCK_GUARDRAIL_ID) {
        if ($envContent -match "BEDROCK_GUARDRAIL_ID=") {
            $envContent = $envContent -replace "# BEDROCK_GUARDRAIL_ID=.*", "BEDROCK_GUARDRAIL_ID=$script:BEDROCK_GUARDRAIL_ID"
            $envContent = $envContent -replace "BEDROCK_GUARDRAIL_ID=.*", "BEDROCK_GUARDRAIL_ID=$script:BEDROCK_GUARDRAIL_ID"
        } else {
            $envContent += "`nBEDROCK_GUARDRAIL_ID=$script:BEDROCK_GUARDRAIL_ID"
        }
        
        if ($envContent -match "BEDROCK_GUARDRAIL_VERSION=") {
            $envContent = $envContent -replace "# BEDROCK_GUARDRAIL_VERSION=.*", "BEDROCK_GUARDRAIL_VERSION=DRAFT"
            $envContent = $envContent -replace "BEDROCK_GUARDRAIL_VERSION=.*", "BEDROCK_GUARDRAIL_VERSION=DRAFT"
        } else {
            $envContent += "`nBEDROCK_GUARDRAIL_VERSION=DRAFT"
        }
        Write-Success "Updated Bedrock Guardrail ID in .env file"
    }
    
    # Enable enhanced chat
    if ($envContent -match "ENHANCED_CHAT_ENABLED=") {
        $envContent = $envContent -replace "ENHANCED_CHAT_ENABLED=.*", "ENHANCED_CHAT_ENABLED=true"
    } else {
        $envContent += "`nENHANCED_CHAT_ENABLED=true"
    }
    
    # Write updated content
    $envContent | Out-File -FilePath $envFilePath -Encoding utf8
    Write-Success "Configuration updated successfully"
    
} else {
    Write-Warning-Custom ".env file not found"
    Write-Info "Please run the main deployment script first to create the .env file"
}

# Step 5: Test Configuration
Write-Step "Step 5: Testing Configuration"

if ($script:Q_BUSINESS_APP_ID) {
    Write-Info "Testing Q Business access..."
    try {
        $testConversations = aws qbusiness list-conversations --application-id $script:Q_BUSINESS_APP_ID --user-id "test-user" --max-results 1 2>&1
        
        if ($testConversations -match "error") {
            Write-Warning-Custom "Q Business access test failed (this may be normal if no conversations exist)"
        } else {
            Write-Success "Q Business access test passed"
        }
    } catch {
        Write-Warning-Custom "Q Business access test failed: $_"
    }
}

if ($script:BEDROCK_GUARDRAIL_ID) {
    Write-Info "Testing Bedrock Guardrail access..."
    try {
        $testGuardrail = aws bedrock get-guardrail --guardrail-identifier $script:BEDROCK_GUARDRAIL_ID 2>&1
        
        if ($testGuardrail -match "error") {
            Write-Warning-Custom "Bedrock Guardrail access test failed"
        } else {
            Write-Success "Bedrock Guardrail access test passed"
        }
    } catch {
        Write-Warning-Custom "Bedrock Guardrail access test failed: $_"
    }
}

# Step 6: Run Enhanced Chat Tests
Write-Step "Step 6: Running Enhanced Chat Tests (Optional)"

$runTests = Read-Host "Run enhanced chat system tests? (y/n)"
if ($runTests -eq 'y' -or $runTests -eq 'Y') {
    Write-Info "Running enhanced chat tests..."
    
    try {
        Set-Location backend
        python test_enhanced_chat_system.py
        Set-Location ..
        Write-Success "Enhanced chat tests completed"
    } catch {
        Write-Warning-Custom "Enhanced chat tests failed: $_"
        Write-Info "This may be normal if dependencies are not installed"
    }
}

# Final Summary
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "                  AMAZON Q SETUP COMPLETE!" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Configuration Summary:" -ForegroundColor Yellow
if ($script:Q_BUSINESS_APP_ID) {
    Write-Host "✅ Amazon Q Business: Configured ($script:Q_BUSINESS_APP_ID)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Amazon Q Business: Not configured (optional)" -ForegroundColor Yellow
}

if ($script:BEDROCK_GUARDRAIL_ID) {
    Write-Host "✅ Bedrock Guardrails: Configured ($script:BEDROCK_GUARDRAIL_ID)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Bedrock Guardrails: Not configured (recommended)" -ForegroundColor Yellow
}

Write-Host "✅ Enhanced Chat: Enabled" -ForegroundColor Green

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Restart your SnapStudy backend to load new configuration" -ForegroundColor White
Write-Host "2. Test the enhanced chat features in the application" -ForegroundColor White
Write-Host "3. Monitor chat interactions and adjust configurations as needed" -ForegroundColor White
Write-Host "4. Review the AMAZON_Q_SETUP_GUIDE.md for detailed configuration options" -ForegroundColor White

if (-not $script:Q_BUSINESS_APP_ID) {
    Write-Host ""
    Write-Host "To enable full Amazon Q features:" -ForegroundColor Yellow
    Write-Host "1. Set up Amazon Q Business application in AWS Console" -ForegroundColor White
    Write-Host "2. Run this script again to configure the application ID" -ForegroundColor White
}

if (-not $script:BEDROCK_GUARDRAIL_ID) {
    Write-Host ""
    Write-Host "To enable content safety guardrails:" -ForegroundColor Yellow
    Write-Host "1. Set up Bedrock Guardrails in AWS Console" -ForegroundColor White
    Write-Host "2. Run this script again to configure the guardrail ID" -ForegroundColor White
}

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""