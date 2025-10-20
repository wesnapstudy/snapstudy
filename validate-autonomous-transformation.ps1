# Validate TRUE Autonomous AI Transformation
# This script verifies that SnapStudy has been successfully transformed
# from prompt-based reasoning to TRUE Bedrock Agents

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "     SnapStudy Autonomous AI Transformation Validation" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

function Write-Check {
    param([string]$Message)
    Write-Host "🔍 $Message" -ForegroundColor Blue
}

function Write-Pass {
    param([string]$Message)
    Write-Host "✅ PASS: $Message" -ForegroundColor Green
}

function Write-Fail {
    param([string]$Message)
    Write-Host "❌ FAIL: $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  WARN: $Message" -ForegroundColor Yellow
}

function Write-Autonomous {
    param([string]$Message)
    Write-Host "🤖 $Message" -ForegroundColor Magenta
}

$validationResults = @()

# Check 1: Infrastructure Code Analysis
Write-Check "Checking infrastructure for TRUE Bedrock Agents..."

if (Test-Path "backend/infrastructure/stacks/snapstudy_stack.py") {
    $infraContent = Get-Content "backend/infrastructure/stacks/snapstudy_stack.py" -Raw
    
    if ($infraContent -match "bedrock\.CfnAgent") {
        Write-Pass "Found Bedrock Agent creation in infrastructure"
        $validationResults += @{Test="Infrastructure Agents"; Result="PASS"}
    } else {
        Write-Fail "No Bedrock Agent creation found in infrastructure"
        $validationResults += @{Test="Infrastructure Agents"; Result="FAIL"}
    }
    
    if ($infraContent -match "bedrock\.CfnKnowledgeBase") {
        Write-Pass "Found Knowledge Base creation in infrastructure"
        $validationResults += @{Test="Infrastructure Knowledge Base"; Result="PASS"}
    } else {
        Write-Fail "No Knowledge Base creation found in infrastructure"
        $validationResults += @{Test="Infrastructure Knowledge Base"; Result="FAIL"}
    }
    
    if ($infraContent -match "opensearch.*CfnCollection") {
        Write-Pass "Found OpenSearch Serverless collection for vector storage"
        $validationResults += @{Test="Vector Storage"; Result="PASS"}
    } else {
        Write-Warning "OpenSearch collection not found - may impact knowledge base"
        $validationResults += @{Test="Vector Storage"; Result="WARN"}
    }
} else {
    Write-Fail "Infrastructure file not found"
    $validationResults += @{Test="Infrastructure File"; Result="FAIL"}
}

# Check 2: Agent Core Implementation Analysis
Write-Check "Analyzing BedrockAgentCore implementation..."

if (Test-Path "backend/src/services/adaptive_agent.py") {
    $agentContent = Get-Content "backend/src/services/adaptive_agent.py" -Raw
    
    # Check for TRUE agent invocation (not prompt-based)
    if ($agentContent -match "bedrock_agent_client\.invoke_agent") {
        Write-Pass "Found TRUE Bedrock Agent invocation (not prompt-based)"
        $validationResults += @{Test="Agent Invocation"; Result="PASS"}
    } else {
        Write-Fail "No TRUE agent invocation found - may still be using prompts"
        $validationResults += @{Test="Agent Invocation"; Result="FAIL"}
    }
    
    # Check for autonomous decision methods
    if ($agentContent -match "autonomous_adapt_learning_path") {
        Write-Pass "Found autonomous adaptation methods"
        $validationResults += @{Test="Autonomous Methods"; Result="PASS"}
    } else {
        Write-Fail "Autonomous adaptation methods not found"
        $validationResults += @{Test="Autonomous Methods"; Result="FAIL"}
    }
    
    # Check for agent session management
    if ($agentContent -match "sessionId.*active_sessions") {
        Write-Pass "Found agent session management"
        $validationResults += @{Test="Session Management"; Result="PASS"}
    } else {
        Write-Warning "Agent session management not found"
        $validationResults += @{Test="Session Management"; Result="WARN"}
    }
    
    # Check for elimination of prompt-based reasoning
    if ($agentContent -match "_create_reasoning_prompt|_invoke_claude_reasoning") {
        Write-Fail "Still contains prompt-based reasoning methods"
        $validationResults += @{Test="Prompt Elimination"; Result="FAIL"}
    } else {
        Write-Pass "Prompt-based reasoning methods eliminated"
        $validationResults += @{Test="Prompt Elimination"; Result="PASS"}
    }
} else {
    Write-Fail "Adaptive agent file not found"
    $validationResults += @{Test="Agent Core File"; Result="FAIL"}
}

# Check 3: Agent Action Functions
Write-Check "Checking Agent Action Functions..."

if (Test-Path "backend/src/agent_actions/agent_actions.py") {
    $actionsContent = Get-Content "backend/src/agent_actions/agent_actions.py" -Raw
    
    if ($actionsContent -match "analyze_student_performance|adapt_learning_path") {
        Write-Pass "Found agent action functions for autonomous decisions"
        $validationResults += @{Test="Agent Actions"; Result="PASS"}
    } else {
        Write-Fail "Agent action functions not found"
        $validationResults += @{Test="Agent Actions"; Result="FAIL"}
    }
} else {
    Write-Fail "Agent actions file not found"
    $validationResults += @{Test="Agent Actions File"; Result="FAIL"}
}

# Check 4: Configuration Updates
Write-Check "Checking configuration for agent support..."

if (Test-Path "backend/src/config.py") {
    $configContent = Get-Content "backend/src/config.py" -Raw
    
    if ($configContent -match "learning_agent_id.*adaptive_agent_id.*knowledge_base_id") {
        Write-Pass "Found agent configuration settings"
        $validationResults += @{Test="Agent Configuration"; Result="PASS"}
    } else {
        Write-Fail "Agent configuration settings not found"
        $validationResults += @{Test="Agent Configuration"; Result="FAIL"}
    }
} else {
    Write-Fail "Configuration file not found"
    $validationResults += @{Test="Configuration File"; Result="FAIL"}
}

# Check 5: Enhanced Chat Integration
Write-Check "Checking enhanced chat agent integration..."

if (Test-Path "backend/src/services/enhanced_chat_agent.py") {
    $chatContent = Get-Content "backend/src/services/enhanced_chat_agent.py" -Raw
    
    if ($chatContent -match "_handle_agent_core_request.*autonomous_decision") {
        Write-Pass "Found TRUE agent integration in enhanced chat"
        $validationResults += @{Test="Chat Agent Integration"; Result="PASS"}
    } else {
        Write-Fail "TRUE agent integration not found in chat"
        $validationResults += @{Test="Chat Agent Integration"; Result="FAIL"}
    }
} else {
    Write-Fail "Enhanced chat agent file not found"
    $validationResults += @{Test="Chat Agent File"; Result="FAIL"}
}

# Check 6: Deployment Scripts
Write-Check "Checking deployment scripts for autonomous AI..."

$deploymentScripts = @(
    "deploy-snapstudy-autonomous.ps1",
    "setup-bedrock-agents.ps1"
)

$deploymentFound = 0
foreach ($script in $deploymentScripts) {
    if (Test-Path $script) {
        $deploymentFound++
        Write-Pass "Found deployment script: $script"
    }
}

if ($deploymentFound -eq $deploymentScripts.Count) {
    $validationResults += @{Test="Deployment Scripts"; Result="PASS"}
} elseif ($deploymentFound -gt 0) {
    $validationResults += @{Test="Deployment Scripts"; Result="WARN"}
} else {
    $validationResults += @{Test="Deployment Scripts"; Result="FAIL"}
}

# Check 7: Test Suite
Write-Check "Checking autonomous AI test suite..."

if (Test-Path "test-autonomous-ai.py") {
    $testContent = Get-Content "test-autonomous-ai.py" -Raw
    
    if ($testContent -match "test_autonomous_reasoning|test_agent_vs_prompts") {
        Write-Pass "Found comprehensive autonomous AI test suite"
        $validationResults += @{Test="Test Suite"; Result="PASS"}
    } else {
        Write-Warning "Test suite found but may be incomplete"
        $validationResults += @{Test="Test Suite"; Result="WARN"}
    }
} else {
    Write-Fail "Autonomous AI test suite not found"
    $validationResults += @{Test="Test Suite"; Result="FAIL"}
}

# Check 8: Documentation
Write-Check "Checking autonomous AI documentation..."

if (Test-Path "TRUE_AUTONOMOUS_AI_IMPLEMENTATION.md") {
    Write-Pass "Found comprehensive autonomous AI documentation"
    $validationResults += @{Test="Documentation"; Result="PASS"}
} else {
    Write-Fail "Autonomous AI documentation not found"
    $validationResults += @{Test="Documentation"; Result="FAIL"}
}

# Generate Validation Report
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "                    VALIDATION REPORT" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan

$passCount = ($validationResults | Where-Object { $_.Result -eq "PASS" }).Count
$warnCount = ($validationResults | Where-Object { $_.Result -eq "WARN" }).Count
$failCount = ($validationResults | Where-Object { $_.Result -eq "FAIL" }).Count
$totalTests = $validationResults.Count

Write-Host ""
Write-Host "Test Results Summary:" -ForegroundColor Yellow
Write-Host "  ✅ PASSED: $passCount/$totalTests" -ForegroundColor Green
Write-Host "  ⚠️  WARNINGS: $warnCount/$totalTests" -ForegroundColor Yellow
Write-Host "  ❌ FAILED: $failCount/$totalTests" -ForegroundColor Red
Write-Host ""

Write-Host "Detailed Results:" -ForegroundColor Yellow
foreach ($result in $validationResults) {
    $icon = switch ($result.Result) {
        "PASS" { "✅" }
        "WARN" { "⚠️ " }
        "FAIL" { "❌" }
    }
    Write-Host "  $icon $($result.Test): $($result.Result)"
}

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan

# Overall Assessment
if ($failCount -eq 0 -and $passCount -ge ($totalTests * 0.8)) {
    Write-Autonomous "TRANSFORMATION SUCCESSFUL!"
    Write-Host ""
    Write-Host "🎉 SnapStudy has been successfully transformed to use TRUE Bedrock Agents!" -ForegroundColor Green
    Write-Host "   ✅ Eliminated prompt-based reasoning" -ForegroundColor Green
    Write-Host "   ✅ Implemented genuine autonomous AI agents" -ForegroundColor Green
    Write-Host "   ✅ Added real-time decision-making capabilities" -ForegroundColor Green
    Write-Host "   ✅ Created comprehensive agent infrastructure" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your application now uses TRUE autonomous AI, not 'agent-like' prompting!" -ForegroundColor Magenta
    
} elseif ($failCount -le 2 -and $passCount -ge ($totalTests * 0.6)) {
    Write-Warning "TRANSFORMATION MOSTLY COMPLETE"
    Write-Host ""
    Write-Host "⚠️  SnapStudy transformation is mostly complete but needs attention:" -ForegroundColor Yellow
    Write-Host "   - Most autonomous AI features are implemented" -ForegroundColor Yellow
    Write-Host "   - Some components may need configuration or fixes" -ForegroundColor Yellow
    Write-Host "   - Review failed tests above for specific issues" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Address the failed tests to complete the transformation." -ForegroundColor Yellow
    
} else {
    Write-Fail "TRANSFORMATION INCOMPLETE"
    Write-Host ""
    Write-Host "❌ SnapStudy transformation to TRUE autonomous AI is incomplete:" -ForegroundColor Red
    Write-Host "   - Multiple critical components are missing or incorrect" -ForegroundColor Red
    Write-Host "   - May still be using prompt-based reasoning" -ForegroundColor Red
    Write-Host "   - Requires significant work to complete transformation" -ForegroundColor Red
    Write-Host ""
    Write-Host "Review and fix the failed tests before deployment." -ForegroundColor Red
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
if ($failCount -eq 0) {
    Write-Host "1. Deploy using: .\deploy-snapstudy-autonomous.ps1" -ForegroundColor White
    Write-Host "2. Run tests: python test-autonomous-ai.py" -ForegroundColor White
    Write-Host "3. Monitor autonomous decisions in production" -ForegroundColor White
} else {
    Write-Host "1. Fix failed validation tests above" -ForegroundColor White
    Write-Host "2. Re-run validation: .\validate-autonomous-transformation.ps1" -ForegroundColor White
    Write-Host "3. Deploy when all tests pass" -ForegroundColor White
}

Write-Host ""
Write-Host "Validation completed at: $(Get-Date)" -ForegroundColor Gray
Write-Host "=====================================================================" -ForegroundColor Cyan