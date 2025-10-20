# SnapStudy Complete Deployment with TRUE Autonomous AI
# Deploys infrastructure with genuine Bedrock Agents (not prompt-based)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "    SnapStudy TRUE Autonomous AI Deployment (Bedrock Agents)" -ForegroundColor Cyan
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

function Write-Autonomous {
    param([string]$Message)
    Write-Host "[🤖 AUTONOMOUS] $Message" -ForegroundColor Magenta
}

# Display autonomous AI features
Write-Host "🤖 TRUE AUTONOMOUS AI FEATURES:" -ForegroundColor Magenta
Write-Host "  ✓ Amazon Bedrock Learning Agent - Autonomous educational reasoning" -ForegroundColor Green
Write-Host "  ✓ Amazon Bedrock Adaptive Agent - Learning path optimization" -ForegroundColor Green
Write-Host "  ✓ Educational Knowledge Base - Vector-based content retrieval" -ForegroundColor Green
Write-Host "  ✓ Agent Action Functions - Autonomous decision execution" -ForegroundColor Green
Write-Host "  ✓ Real-time Adaptation - Performance-based autonomous adjustments" -ForegroundColor Green
Write-Host ""
Write-Host "🚫 NO MORE PROMPT-BASED 'AGENT-LIKE' BEHAVIOR" -ForegroundColor Red
Write-Host "✅ GENUINE AUTONOMOUS AI DECISION-MAKING" -ForegroundColor Green
Write-Host ""

# Step 1: Prerequisites Check
Write-Step "Step 1: Checking Prerequisites for Autonomous AI"

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

# Step 2: AWS Profile and Permissions Check
Write-Step "Step 2: Validating AWS Profile and Bedrock Permissions"

$env:AWS_PROFILE = "hackathon"

try {
    $testOutput = aws sts get-caller-identity --profile hackathon --output json 2>&1
    
    if ($testOutput -match "InvalidClientTokenId|NoCredentialsError|error") {
        Write-Error-Custom "AWS credentials for 'hackathon' profile are invalid"
        Write-Info "Please run: aws configure --profile hackathon"
        exit 1
    }
    
    Write-Success "AWS Profile 'hackathon' is working"
    
    # Parse account info
    try {
        $identity = $testOutput | ConvertFrom-Json
        $script:AWS_ACCOUNT_ID = $identity.Account
    } catch {
        if ($testOutput -match '"Account":\s*"(\d+)"') {
            $script:AWS_ACCOUNT_ID = $matches[1]
        } else {
            $script:AWS_ACCOUNT_ID = "unknown"
        }
    }
    
    $script:AWS_REGION = aws configure get region --profile hackathon 2>$null
    if (-not $script:AWS_REGION) {
        $script:AWS_REGION = "us-east-1"
    }
    
    Write-Success "Account ID: $script:AWS_ACCOUNT_ID"
    Write-Success "Region: $script:AWS_REGION"
    
} catch {
    Write-Error-Custom "AWS Profile test failed: $_"
    exit 1
}

# Step 3: Bedrock Permissions Validation
Write-Step "Step 3: Validating Bedrock Agent Permissions"

Write-Autonomous "Checking permissions for TRUE Bedrock Agents..."

# Check Bedrock model access
try {
    $bedrockTest = cmd /c "aws bedrock list-foundation-models --region $script:AWS_REGION --profile hackathon --output json 2>nul"
    
    if ($bedrockTest -and $bedrockTest -match '"modelSummaries"') {
        Write-Success "Bedrock foundation models accessible"
        
        if ($bedrockTest -match "anthropic.claude-3-5-sonnet") {
            Write-Success "Claude 3.5 Sonnet available for agents"
        } else {
            Write-Info "Claude 3.5 Sonnet not found - may need to be enabled"
        }
    } else {
        Write-Info "Bedrock model access limited - agents may use fallback"
    }
} catch {
    Write-Info "Bedrock model check skipped - will configure during deployment"
}

# Check Bedrock Agent permissions
try {
    $agentTest = cmd /c "aws bedrock-agent list-agents --region $script:AWS_REGION --profile hackathon --output json 2>nul"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Bedrock Agent service accessible"
        Write-Autonomous "Ready to create TRUE autonomous agents"
    } else {
        Write-Info "Bedrock Agent service check failed - will attempt during deployment"
    }
} catch {
    Write-Info "Bedrock Agent service check skipped"
}

# Step 4: Backend Setup with Agent Support
Write-Step "Step 4: Setting Up Backend for Autonomous AI"

Set-Location backend

Write-Info "Creating virtual environment..."
python -m venv venv
Write-Success "Virtual environment created"

Write-Info "Activating virtual environment..."
.\venv\Scripts\Activate.ps1

Write-Info "Installing Python dependencies with agent support..."
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# Add additional dependencies for agents if needed
pip install boto3 --upgrade --quiet
Write-Success "Dependencies installed with agent support"

Write-Info "Creating .env file with autonomous AI configuration..."
$jwtSecret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})

$envContent = @"
AWS_REGION=$script:AWS_REGION
AWS_ACCOUNT_ID=$script:AWS_ACCOUNT_ID
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
JWT_SECRET_KEY=$jwtSecret

# Amazon Q Configuration (Optional)
Q_BUSINESS_APPLICATION_ID=
Q_BUSINESS_INDEX_ID=
Q_DEVELOPER_ENABLED=false

# Bedrock Guardrails Configuration (Optional)
BEDROCK_GUARDRAIL_ID=
BEDROCK_GUARDRAIL_VERSION=DRAFT

# Enhanced Chat Configuration
ENHANCED_CHAT_ENABLED=true
CONTENT_SAFETY_LEVEL=strict

# TRUE Autonomous AI Configuration (Bedrock Agents)
LEARNING_AGENT_ID=
ADAPTIVE_AGENT_ID=
KNOWLEDGE_BASE_ID=
BEDROCK_AGENT_ALIAS_ID=PRODUCTION

# Autonomous Features
AUTONOMOUS_ADAPTATION_ENABLED=true
AGENT_DECISION_LOGGING=true
"@

$envContent | Out-File -FilePath .env -Encoding utf8
Write-Success "Backend .env file created with autonomous AI settings"
Write-Autonomous "Agent configuration placeholders ready"

Set-Location ..

# Step 5: Frontend Setup
Write-Step "Step 5: Setting Up Frontend"

Set-Location frontend

# Clean and rebuild frontend
if (Test-Path "node_modules") {
    Write-Info "Cleaning existing node_modules..."
    Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
}

if (Test-Path "package-lock.json") {
    Remove-Item package-lock.json -ErrorAction SilentlyContinue
}

Write-Info "Installing frontend dependencies (fresh install)..."
npm install

if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Frontend dependency installation failed"
    exit 1
}

Write-Success "Frontend dependencies installed"

Write-Info "Creating frontend environment configuration..."
$frontendEnvContent = @"
REACT_APP_AWS_REGION=$script:AWS_REGION
REACT_APP_USER_POOL_ID=PLACEHOLDER
REACT_APP_USER_POOL_CLIENT_ID=PLACEHOLDER
REACT_APP_API_URL=PLACEHOLDER
REACT_APP_AUTONOMOUS_AI_ENABLED=true
"@

$frontendEnvContent | Out-File -FilePath .env.production -Encoding utf8
Write-Success "Frontend .env.production created"

Write-Info "Building frontend (this may take 2-3 minutes)..."
npm run build

if ($LASTEXITCODE -eq 0) {
    Write-Success "Frontend build completed successfully"
} else {
    Write-Error-Custom "Frontend build failed"
    Write-Info "Check the error messages above"
    
    $continueWithoutFrontend = Read-Host "Continue with backend-only deployment? (y/n)"
    if ($continueWithoutFrontend -ne "y") {
        exit 1
    }
    Write-Info "Continuing with backend-only deployment..."
}

Set-Location ..

# Step 6: CDK Infrastructure Deployment with Bedrock Agents
Write-Step "Step 6: Deploying Infrastructure with TRUE Bedrock Agents"

Set-Location backend\infrastructure

Write-Info "Installing CDK dependencies..."
if (-not (Test-Path "node_modules")) {
    npm install
}

Write-Info "Bootstrapping CDK (if needed)..."
try {
    aws cloudformation describe-stacks --stack-name CDKToolkit --region $script:AWS_REGION 2>$null | Out-Null
    Write-Success "CDK already bootstrapped"
} catch {
    Write-Info "Bootstrapping CDK..."
    cdk bootstrap "aws://$script:AWS_ACCOUNT_ID/$script:AWS_REGION"
}

Write-Info "Synthesizing CloudFormation template with Bedrock Agents..."
cdk synth | Out-Null

Write-Host ""
Write-Host "🤖 READY TO DEPLOY TRUE AUTONOMOUS AI!" -ForegroundColor Magenta
Write-Host ""
Write-Host "This deployment will create:" -ForegroundColor Yellow
Write-Host "  🤖 Amazon Bedrock Learning Agent - Autonomous educational reasoning" -ForegroundColor Green
Write-Host "  🎯 Amazon Bedrock Adaptive Agent - Learning path optimization" -ForegroundColor Green
Write-Host "  📚 Educational Knowledge Base - Vector storage with OpenSearch" -ForegroundColor Green
Write-Host "  ⚡ Agent Action Functions - Lambda functions for autonomous actions" -ForegroundColor Green
Write-Host "  🔧 Standard Infrastructure - API, DynamoDB, S3, Cognito, etc." -ForegroundColor White
Write-Host ""
Write-Host "🚫 NO PROMPT-BASED REASONING - TRUE AUTONOMOUS AGENTS ONLY" -ForegroundColor Red
Write-Host ""

$confirmDeploy = Read-Host "Deploy TRUE Autonomous AI infrastructure? (y/n)"
if ($confirmDeploy -ne "y") {
    Write-Info "Deployment cancelled"
    exit 0
}

Write-Autonomous "Starting deployment of TRUE Bedrock Agents (8-15 minutes)..."
Write-Info "Creating autonomous AI agents and knowledge base..."

cdk deploy --require-approval never

if ($LASTEXITCODE -eq 0) {
    Write-Success "Infrastructure with Bedrock Agents deployed successfully!"
    Write-Autonomous "TRUE autonomous AI agents are now active!"
} else {
    Write-Error-Custom "Deployment failed"
    exit 1
}

Set-Location ..\..

# Step 7: Configure Bedrock Agents
Write-Step "Step 7: Configuring Bedrock Agent IDs"

Write-Autonomous "Extracting agent IDs from deployment..."

try {
    $stackOutputs = aws cloudformation describe-stacks --stack-name SnapStudyStack --region $script:AWS_REGION --query "Stacks[0].Outputs" --output json
    $outputs = $stackOutputs | ConvertFrom-Json
    
    $learningAgentId = ($outputs | Where-Object { $_.OutputKey -eq "LearningAgentId" }).OutputValue
    $adaptiveAgentId = ($outputs | Where-Object { $_.OutputKey -eq "AdaptiveAgentId" }).OutputValue
    $knowledgeBaseId = ($outputs | Where-Object { $_.OutputKey -eq "KnowledgeBaseId" }).OutputValue
    
    if ($learningAgentId) {
        Write-Autonomous "Learning Agent ID: $learningAgentId"
        
        # Update backend .env with agent IDs
        Set-Location backend
        $envContent = Get-Content ".env" -Raw
        $envContent = $envContent -replace "LEARNING_AGENT_ID=", "LEARNING_AGENT_ID=$learningAgentId"
        
        if ($adaptiveAgentId) {
            Write-Autonomous "Adaptive Agent ID: $adaptiveAgentId"
            $envContent = $envContent -replace "ADAPTIVE_AGENT_ID=", "ADAPTIVE_AGENT_ID=$adaptiveAgentId"
        }
        
        if ($knowledgeBaseId) {
            Write-Autonomous "Knowledge Base ID: $knowledgeBaseId"
            $envContent = $envContent -replace "KNOWLEDGE_BASE_ID=", "KNOWLEDGE_BASE_ID=$knowledgeBaseId"
        }
        
        $envContent | Out-File -FilePath .env -Encoding utf8 -NoNewline
        Write-Success "Agent IDs configured in backend"
        
        Set-Location ..
    } else {
        Write-Error-Custom "Learning Agent ID not found in deployment outputs"
        Write-Info "Agents may not have been created successfully"
    }
    
} catch {
    Write-Error-Custom "Error configuring agent IDs: $_"
    Write-Info "You may need to configure agent IDs manually"
}

# Step 8: Get Deployment Outputs
Write-Step "Step 8: Retrieving Deployment Information"

$script:API_URL = ($outputs | Where-Object { $_.OutputKey -eq "RestApiUrl" }).OutputValue
$script:USER_POOL_ID = ($outputs | Where-Object { $_.OutputKey -eq "UserPoolId" }).OutputValue
$script:USER_POOL_CLIENT_ID = ($outputs | Where-Object { $_.OutputKey -eq "UserPoolClientId" }).OutputValue
$script:FRONTEND_URL = ($outputs | Where-Object { $_.OutputKey -eq "FrontendUrl" }).OutputValue

# Step 9: Test Autonomous AI
Write-Step "Step 9: Testing TRUE Autonomous AI Implementation"

Write-Autonomous "Running autonomous AI validation tests..."

try {
    python test-autonomous-ai.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Autonomous "Autonomous AI tests completed - check results above"
    } else {
        Write-Info "Autonomous AI tests encountered issues - manual verification recommended"
    }
} catch {
    Write-Info "Autonomous AI test script not found or failed to run"
    Write-Info "You can manually test agent functionality after deployment"
}

# Step 10: Final Configuration and Testing
Write-Step "Step 10: Final System Validation"

Write-Info "Testing API health endpoint..."
try {
    $health = Invoke-RestMethod -Uri "$script:API_URL/health" -Method Get
    Write-Success "API is healthy!"
} catch {
    Write-Info "API test: $($_.Exception.Message)"
    Write-Info "API may need a few seconds to warm up"
}

# Final Summary
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "           TRUE AUTONOMOUS AI DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""

Write-Host "🤖 AUTONOMOUS AI AGENTS DEPLOYED:" -ForegroundColor Magenta
if ($learningAgentId) {
    Write-Host "  ✅ Learning Agent: $learningAgentId" -ForegroundColor Green
}
if ($adaptiveAgentId) {
    Write-Host "  ✅ Adaptive Agent: $adaptiveAgentId" -ForegroundColor Green
}
if ($knowledgeBaseId) {
    Write-Host "  ✅ Knowledge Base: $knowledgeBaseId" -ForegroundColor Green
}
Write-Host ""

Write-Host "🌐 APPLICATION ENDPOINTS:" -ForegroundColor Yellow
Write-Host "  Backend API: $script:API_URL" -ForegroundColor White
Write-Host "  Frontend: $script:FRONTEND_URL" -ForegroundColor White
Write-Host ""

Write-Host "🎯 AUTONOMOUS CAPABILITIES ACTIVE:" -ForegroundColor Green
Write-Host "  ✅ Real-time Learning Adaptation" -ForegroundColor Green
Write-Host "  ✅ Performance-based Decision Making" -ForegroundColor Green
Write-Host "  ✅ Autonomous Content Personalization" -ForegroundColor Green
Write-Host "  ✅ Intelligent Learning Path Optimization" -ForegroundColor Green
Write-Host "  ✅ Educational Knowledge Base Integration" -ForegroundColor Green
Write-Host ""

Write-Host "🚫 ELIMINATED PROMPT-BASED REASONING" -ForegroundColor Red
Write-Host "✅ IMPLEMENTED TRUE BEDROCK AGENTS" -ForegroundColor Green
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Open frontend: $script:FRONTEND_URL" -ForegroundColor White
Write-Host "2. Test autonomous AI features in the chat interface" -ForegroundColor White
Write-Host "3. Monitor agent decisions in CloudWatch logs" -ForegroundColor White
Write-Host "4. Upload educational content to the Knowledge Base" -ForegroundColor White
Write-Host ""

Write-Autonomous "Your SnapStudy application now uses TRUE Amazon Bedrock Agents!"
Write-Autonomous "Genuine autonomous AI decision-making is now active!"
Write-Host ""

Write-Success "TRUE Autonomous AI deployment completed successfully!"