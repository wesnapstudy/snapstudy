@echo off
echo Testing Bedrock access...

set AWS_PROFILE=hackathon

echo Running Bedrock test...
aws bedrock list-foundation-models --region us-east-1 --profile hackathon --output json

echo.
echo Test completed.
pause