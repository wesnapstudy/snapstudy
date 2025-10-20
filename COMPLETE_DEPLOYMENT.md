# Complete AWS Deployment Guide - Backend + Frontend

## Overview

This deployment script (`deploy-complete.ps1`) deploys your entire SnapStudy application to AWS cloud, including:

- **Backend Infrastructure**: Lambda, API Gateway, DynamoDB, Cognito
- **Frontend Website**: React app deployed to S3 with static website hosting
- **Security**: AWS WAF with managed rules
- **Monitoring**: CloudWatch Dashboard and Alarms

## Prerequisites

Before running the deployment, ensure you have:

1. **AWS Profile**: Named `hackathon` configured with valid credentials
   ```powershell
   aws configure --profile hackathon
   ```

2. **Software Installed**:
   - Python 3.11+
   - Node.js 18+
   - AWS CLI
   - AWS CDK (will be installed automatically if missing)

3. **Bedrock Access**: Claude 3.5 Sonnet model enabled in `us-east-1` region

## Quick Start

### Step 1: Open PowerShell as Administrator

Press `Win + X` → Select "Windows PowerShell (Admin)"

### Step 2: Navigate to Project Directory

```powershell
cd D:\repo\hackathon\study
```

### Step 3: Run Complete Deployment

```powershell
.\deploy-complete.ps1
```

## What the Script Does

### Phase 1: Prerequisites Check (1 minute)
- Verifies Python, Node.js, npm, AWS CLI, and CDK
- Checks AWS profile 'hackathon' exists
- Verifies AWS credentials and Bedrock access

### Phase 2: Backend Setup (3 minutes)
- Creates Python virtual environment
- Installs Python dependencies
- Creates `.env` file with AWS configuration

### Phase 3: Frontend Setup (4 minutes)
- Installs React dependencies
- Creates production environment config
- **Builds React app** (creates optimized production build)

### Phase 4: CDK Bootstrap (2 minutes, first-time only)
- Bootstraps AWS CDK in your account
- Creates necessary CDK resources

### Phase 5: Infrastructure Deployment (8-12 minutes)
- Deploys all AWS resources via CloudFormation
- Creates 6 DynamoDB tables
- Creates Lambda function with all necessary IAM permissions
- Creates API Gateway with CORS
- Creates Cognito User Pool
- Creates AWS WAF with security rules
- Creates CloudWatch Dashboard and Alarms
- **Creates S3 bucket for frontend hosting**
- **Deploys frontend build to S3**

### Phase 6: Post-Deployment (2 minutes)
- Updates frontend config with real API URLs
- Rebuilds and redeploys frontend
- Tests API health endpoint
- Tests frontend website accessibility
- Creates test user (optional)

## Deployment Outputs

After successful deployment, you'll receive:

```
Backend API URL: https://abc123.execute-api.us-east-1.amazonaws.com/prod/
User Pool ID: us-east-1_ABC123
Client ID: 1a2b3c4d5e6f7g8h9i0j1k
Content S3 Bucket: snapstudy-content-123456789012-us-east-1
Frontend S3 Bucket: snapstudy-frontend-123456789012-us-east-1
Frontend Website URL: http://snapstudy-frontend-123456789012-us-east-1.s3-website-us-east-1.amazonaws.com
```

These are also saved to `deployment-outputs.json`

## Testing Your Deployment

### 1. Test Backend API

```powershell
Invoke-RestMethod -Uri "https://YOUR-API-URL/health"
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-20T14:30:00Z"
}
```

### 2. Test Frontend Website

Open your browser and navigate to the Frontend URL:
```
http://snapstudy-frontend-ACCOUNT-REGION.s3-website-us-east-1.amazonaws.com
```

You should see the SnapStudy login page.

### 3. Login with Test User

If you created a test user during deployment:
- **Email**: `test@example.com`
- **Password**: `TestPassword123!`

### 4. View CloudWatch Dashboard

1. Go to AWS Console: https://console.aws.amazon.com/cloudwatch
2. Select region: **US East (N. Virginia)**
3. Click **Dashboards** → **SnapStudy-Metrics**

You'll see real-time metrics for:
- Lambda invocations, errors, duration
- API Gateway requests, latency, errors
- DynamoDB read/write capacity

### 5. Check AWS WAF

1. Go to AWS Console: https://console.aws.amazon.com/wafv2
2. Select region: **US East (N. Virginia)**
3. Click **Web ACLs** → **SnapStudyApiWaf**

You'll see active security rules:
- AWS Managed Rules - Common Rule Set
- AWS Managed Rules - Known Bad Inputs
- Rate Limiting (1000 req/5min)
- SQL Injection Protection

## Architecture Diagram

```
┌─────────────────┐
│   User Browser  │
└────────┬────────┘
         │
         ├──────────────────────────────────────┐
         │                                      │
         v                                      v
┌─────────────────────┐              ┌──────────────────┐
│  S3 Frontend Bucket │              │   API Gateway    │
│  (Static Website)   │              │   (REST API)     │
└─────────────────────┘              └────────┬─────────┘
                                              │
                                              v
                                     ┌────────────────────┐
                                     │    AWS WAF         │
                                     │  (Security Rules)  │
                                     └────────┬───────────┘
                                              │
                                              v
                                     ┌────────────────────┐
                                     │  Lambda Function   │
                                     │   (FastAPI App)    │
                                     └────────┬───────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────┐
                    │                         │                     │
                    v                         v                     v
           ┌─────────────────┐      ┌──────────────┐      ┌─────────────┐
           │  DynamoDB       │      │   Cognito    │      │  S3 Bucket  │
           │  (6 Tables)     │      │  User Pool   │      │  (Content)  │
           └─────────────────┘      └──────────────┘      └─────────────┘
                    │
                    v
           ┌─────────────────┐
           │  Amazon Bedrock │
           │  Claude 3.5     │
           └─────────────────┘
                    │
                    v
           ┌─────────────────┐
           │   CloudWatch    │
           │   Monitoring    │
           └─────────────────┘
```

## Cost Estimate

### Free Tier (First 12 Months)
- Lambda: 1M requests/month
- DynamoDB: 25 GB storage, 25 WCU, 25 RCU
- S3: 5 GB storage, 20k GET, 2k PUT
- Cognito: 50k MAU
- CloudWatch: 10 metrics, 10 alarms

### Estimated Monthly Cost (After Free Tier)
- Lambda: ~$1-5 (depends on usage)
- DynamoDB: ~$1-3 (pay-per-request)
- S3 (Content): ~$0.50
- S3 (Frontend): ~$0.01-0.10
- API Gateway: ~$1-3
- Bedrock: Pay per token (~$3-15 per 1M tokens)
- Cognito: Free up to 50k MAU
- AWS WAF: ~$5 base + $1 per rule
- CloudWatch: ~$1-2

**Total**: ~$15-35/month (excluding Bedrock usage)

## Troubleshooting

### Script Fails at Prerequisites

**Error**: `Python not found`
- Install Python from https://www.python.org
- Restart PowerShell

**Error**: `AWS Profile 'hackathon' not found`
- Run: `aws configure --profile hackathon`
- Enter your AWS Access Key ID and Secret Key

### Script Fails at Bedrock Access Check

**Error**: `Claude 3.5 Sonnet not accessible`

1. Go to: https://console.aws.amazon.com/bedrock
2. **IMPORTANT**: Switch region to **US East (N. Virginia)**
3. Click "Model access" in left sidebar
4. Click "Request model access"
5. Enable "Anthropic Claude 3.5 Sonnet"
6. Wait 10 seconds, refresh page
7. Verify "Access granted" status

### Frontend Build Fails

**Error**: `npm run build failed`

Check for:
- Node.js version (need 18+): `node --version`
- Memory issues: Close other apps
- Missing dependencies: Delete `node_modules`, run `npm install`

### Deployment Fails

**Error**: `CDK deploy failed`

1. Check CloudFormation console:
   - https://console.aws.amazon.com/cloudformation
   - Look for stack "SnapStudyStack"
   - Check "Events" tab for error details

2. Common issues:
   - **IAM Permissions**: Need AdministratorAccess or PowerUser role
   - **Service Quotas**: Check AWS service limits
   - **Region**: Ensure using `us-east-1`

### Frontend Not Loading

**Issue**: S3 website URL shows error

1. Check bucket policy:
   ```powershell
   aws s3api get-bucket-policy --bucket FRONTEND-BUCKET-NAME --profile hackathon
   ```

2. Verify files uploaded:
   ```powershell
   aws s3 ls s3://FRONTEND-BUCKET-NAME/ --profile hackathon
   ```

3. Check website configuration:
   ```powershell
   aws s3api get-bucket-website --bucket FRONTEND-BUCKET-NAME --profile hackathon
   ```

4. Re-upload frontend:
   ```powershell
   cd frontend
   npm run build
   aws s3 sync build/ s3://FRONTEND-BUCKET-NAME --delete --profile hackathon
   ```

### API Not Responding

**Issue**: API health check fails

1. Wait 2-3 minutes for Lambda cold start

2. Check Lambda logs:
   ```powershell
   aws logs tail /aws/lambda/SnapStudyStack-ApiLambda --follow --region us-east-1 --profile hackathon
   ```

3. Test directly:
   ```powershell
   aws lambda invoke --function-name SnapStudyStack-ApiLambda --region us-east-1 --profile hackathon output.json
   cat output.json
   ```

## Cleanup

To remove all deployed resources:

```powershell
cd backend\infrastructure
cdk destroy --profile hackathon
```

**Warning**: This will delete all data in DynamoDB tables and S3 buckets (if not retained).

## Security Best Practices

### Production Deployment Checklist

Before going to production, update these configurations:

1. **API Gateway CORS** (snapstudy_stack.py:498)
   ```python
   allow_origins=["https://yourdomain.com"]  # Don't use ALL_ORIGINS
   ```

2. **Cognito Callback URLs** (snapstudy_stack.py:307)
   ```python
   callback_urls=["https://yourdomain.com/auth/callback"]
   ```

3. **S3 Bucket Policies**
   - Restrict frontend bucket to CloudFront only
   - Enable CloudFront for HTTPS

4. **Environment Variables**
   - Don't commit `.env` files
   - Use AWS Secrets Manager for sensitive data

5. **CloudWatch Alarms**
   - Add SNS topic for email notifications
   - Set up alerts for security events

6. **WAF Rules**
   - Review and customize rate limits
   - Add geo-blocking if needed
   - Enable logging

## Next Steps

After successful deployment:

1. **Upload Content**
   - Use the API to upload educational content
   - Test document processing (PDF, images)

2. **Create Users**
   - Use Cognito console or API
   - Test authentication flow

3. **Monitor Performance**
   - Check CloudWatch Dashboard daily
   - Review Lambda execution times
   - Monitor DynamoDB capacity

4. **Configure Custom Domain** (Optional)
   - Register domain in Route 53
   - Create CloudFront distribution
   - Configure ACM certificate

5. **Submit to Hackathon**
   - Prepare demo video
   - Document use cases
   - Highlight AgentCore usage

## Support

For issues or questions:

1. Check deployment logs: `deployment-outputs.json`
2. Review CloudFormation events in AWS Console
3. Check Lambda logs in CloudWatch
4. Verify all services in correct region (`us-east-1`)

## Congratulations!

Your SnapStudy application is now fully deployed on AWS with:
- ✅ Autonomous AI agents using Bedrock AgentCore
- ✅ Secure API with AWS WAF protection
- ✅ Scalable infrastructure with DynamoDB
- ✅ Production-ready monitoring
- ✅ Fully hosted frontend website

Good luck with the hackathon! 🚀
