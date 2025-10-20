# Test Bedrock Access
$ErrorActionPreference = "Continue"

Write-Host "Testing Bedrock access..." -ForegroundColor Yellow

# Set AWS profile
$env:AWS_PROFILE = "hackathon"

# Test Bedrock access
try {
    Write-Host "Running: aws bedrock list-foundation-models --region us-east-1 --profile hackathon --output json" -ForegroundColor Blue
    
    $bedrockOutput = aws bedrock list-foundation-models --region us-east-1 --profile hackathon --output json 2>&1
    
    Write-Host "Raw output:" -ForegroundColor Cyan
    Write-Host $bedrockOutput
    
    # Check for errors
    if ($bedrockOutput -match "AccessDenied|UnauthorizedOperation|InvalidUserID|Forbidden|NoCredentialsError") {
        Write-Host "ERROR: Access denied to Bedrock service" -ForegroundColor Red
    } elseif ($bedrockOutput -match "error|Error|ERROR") {
        Write-Host "ERROR: Bedrock API error detected" -ForegroundColor Red
    } else {
        Write-Host "SUCCESS: Bedrock accessible" -ForegroundColor Green
        
        # Try to parse JSON
        try {
            $models = $bedrockOutput | ConvertFrom-Json
            Write-Host "Found $($models.modelSummaries.Count) models" -ForegroundColor Green
            
            $claudeModel = $models.modelSummaries | Where-Object { $_.modelId -eq "anthropic.claude-3-5-sonnet-20240620-v1:0" }
            if ($claudeModel) {
                Write-Host "Claude 3.5 Sonnet is available!" -ForegroundColor Green
            } else {
                Write-Host "Claude 3.5 Sonnet not found in available models" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "Could not parse JSON response" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "Exception occurred: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Test completed." -ForegroundColor Yellow