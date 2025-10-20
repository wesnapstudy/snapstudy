# 🚀 SnapStudy - Complete Deployment Guide

This guide will walk you through deploying SnapStudy from scratch to a fully functional production environment on AWS.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS Account Setup](#aws-account-setup)
3. [Local Development Setup](#local-development-setup)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [Post-Deployment Configuration](#post-deployment-configuration)
7. [Testing the Deployment](#testing-the-deployment)
8. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
9. [Cleanup](#cleanup)

---

## 📌 Prerequisites

### **Required Software**

| Software | Version | Download Link | Purpose |
|----------|---------|---------------|---------|
| **Python** | 3.11+ | [python.org](https://www.python.org/downloads/) | Backend runtime |
| **Node.js** | 16+ | [nodejs.org](https://nodejs.org/) | Frontend build & CDK |
| **AWS CLI** | 2.x | [AWS CLI](https://aws.amazon.com/cli/) | AWS operations |
| **Git** | 2.x | [git-scm.com](https://git-scm.com/) | Version control |
| **AWS CDK** | 2.x | `npm install -g aws-cdk` | Infrastructure deployment |

### **AWS Account Requirements**

- ✅ Active AWS account with admin access
- ✅ **Amazon Bedrock** access in `us-east-1` region
- ✅ **Claude 3.5 Sonnet** model access enabled
- ✅ Billing enabled (Free tier eligible for most services)
- ✅ AWS CLI configured with credentials

### **Estimated Costs**

| Service | Free Tier | After Free Tier |
|---------|-----------|-----------------|
| Lambda | 1M requests/month free | $0.20 per 1M requests |
| DynamoDB | 25GB storage free | $0.25 per GB/month |
| S3 | 5GB storage free | $0.023 per GB/month |
| Bedrock | No free tier | ~$0.003 per 1K tokens |
| API Gateway | 1M requests free | $1.00 per 1M requests |
| **Estimated Total** | **$0-5/month** (development) | **$20-50/month** (production) |

---

## 🔧 AWS Account Setup

### **Step 1: Create AWS Account**

If you don't have an AWS account:

1. Go to [aws.amazon.com](https://aws.amazon.com)
2. Click "Create an AWS Account"
3. Follow the registration process
4. Enter payment information (required, even for free tier)

### **Step 2: Enable Amazon Bedrock Access**

**CRITICAL:** You must request access to Claude models in Bedrock.

```bash
# 1. Open AWS Console
# 2. Navigate to Amazon Bedrock service
# 3. Select region: us-east-1 (N. Virginia)
# 4. Go to "Model access" in the left sidebar
# 5. Click "Request model access"
# 6. Find and enable:
#    - Anthropic Claude 3.5 Sonnet v1
# 7. Wait for approval (usually instant, but can take up to 24 hours)
```

**Verify Access:**
```bash
aws bedrock list-foundation-models --region us-east-1 --by-provider anthropic
```

You should see `anthropic.claude-3-5-sonnet-20240620-v1:0` in the output.

### **Step 3: Configure AWS CLI**

```bash
# Install AWS CLI (if not already installed)
# Windows: Download from https://aws.amazon.com/cli/
# macOS: brew install awscli
# Linux: sudo apt-get install awscli

# Configure credentials
aws configure

# Enter when prompted:
# AWS Access Key ID: <your-access-key>
# AWS Secret Access Key: <your-secret-key>
# Default region name: us-east-1
# Default output format: json
```

**Create Access Keys:**
1. AWS Console → IAM → Users → Your User
2. Security credentials tab
3. Create access key → CLI
4. Save the Access Key ID and Secret Access Key

**Verify Configuration:**
```bash
aws sts get-caller-identity
```

Expected output:
```json
{
    "UserId": "AIDAXXXXXXXXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/yourname"
}
```

### **Step 4: Set Environment Variables**

**Windows (PowerShell):**
```powershell
$env:AWS_REGION = "us-east-1"
$env:AWS_ACCOUNT_ID = "123456789012"  # Replace with your account ID
```

**macOS/Linux (Bash):**
```bash
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=123456789012  # Replace with your account ID
```

**Permanent Configuration** (recommended):

Create `.env` file in project root:
```bash
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
```

---

## 💻 Local Development Setup

### **Step 1: Clone Repository**

```bash
# Clone the repository
git clone https://github.com/yourusername/snapstudy.git
cd snapstudy

# Verify structure
ls -la
# You should see: backend/ frontend/ README.md SUBMISSION.md
```

### **Step 2: Backend Setup**

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; import boto3; print('Dependencies installed successfully')"
```

**Expected output:**
```
Dependencies installed successfully
```

### **Step 3: Frontend Setup**

```bash
# Navigate to frontend (from project root)
cd frontend

# Install dependencies
npm install

# Verify installation
npm list --depth=0
```

**Expected output:**
```
snapstudy-frontend@0.1.0
├── @types/node@16.18.0
├── @types/react@18.2.0
├── @types/react-dom@18.2.0
├── axios@1.6.0
├── react@18.2.0
├── react-dom@18.2.0
├── react-scripts@5.0.1
└── typescript@4.9.5
```

---

## 🏗️ Backend Deployment

### **Step 1: Install CDK Dependencies**

```bash
# Navigate to infrastructure directory
cd backend/infrastructure

# Install Node.js dependencies
npm install

# Verify CDK installation
cdk --version
# Expected: 2.x.x
```

### **Step 2: Bootstrap CDK (First Time Only)**

```bash
# Bootstrap CDK in your AWS account
cdk bootstrap aws://123456789012/us-east-1

# Replace 123456789012 with your AWS Account ID
# Or use environment variable:
cdk bootstrap aws://$AWS_ACCOUNT_ID/$AWS_REGION
```

**Expected output:**
```
⏳  Bootstrapping environment aws://123456789012/us-east-1...
✅  Environment aws://123456789012/us-east-1 bootstrapped.
```

**What this does:**
- Creates an S3 bucket for CDK assets
- Creates IAM roles for CloudFormation
- Sets up necessary permissions
- **Only needs to be done once per account/region**

### **Step 3: Synthesize CloudFormation Template**

```bash
# Generate CloudFormation template
cdk synth

# This creates a cdk.out/ directory with the template
```

**Expected output:**
```
Successfully synthesized to /path/to/backend/infrastructure/cdk.out
Supply a stack id (SnapStudyStack) to display its template.
```

### **Step 4: Review Changes (Optional)**

```bash
# See what will be deployed
cdk diff
```

This shows:
- New resources to be created
- Existing resources to be modified
- Resources to be deleted (if any)

### **Step 5: Deploy Infrastructure**

```bash
# Deploy the stack
cdk deploy

# You'll be prompted to approve security changes
# Type 'y' to approve
```

**Expected output:**
```
SnapStudyStack: deploying...
[0%] start: Publishing...
[50%] success: Published...
[100%] success: Published...
SnapStudyStack: creating CloudFormation changeset...

✅  SnapStudyStack

Outputs:
SnapStudyStack.UserPoolId = us-east-1_XXXXXXXXX
SnapStudyStack.UserPoolClientId = 1a2b3c4d5e6f7g8h9i0j
SnapStudyStack.RestApiUrl = https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/
SnapStudyStack.ContentBucketName = snapstudy-content-123456789012-us-east-1

Stack ARN:
arn:aws:cloudformation:us-east-1:123456789012:stack/SnapStudyStack/...
```

**⏱️ Deployment Time:** 5-10 minutes

### **Step 6: Save CDK Outputs**

**IMPORTANT:** Save these outputs - you'll need them for frontend configuration!

```bash
# Get stack outputs
aws cloudformation describe-stacks \
  --stack-name SnapStudyStack \
  --query 'Stacks[0].Outputs' \
  --region us-east-1

# Save to file
aws cloudformation describe-stacks \
  --stack-name SnapStudyStack \
  --query 'Stacks[0].Outputs' \
  --region us-east-1 > outputs.json
```

**Example outputs.json:**
```json
[
  {
    "OutputKey": "RestApiUrl",
    "OutputValue": "https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/"
  },
  {
    "OutputKey": "UserPoolId",
    "OutputValue": "us-east-1_ABC123XYZ"
  },
  {
    "OutputKey": "UserPoolClientId",
    "OutputValue": "1a2b3c4d5e6f7g8h9i0j1k2l3m"
  },
  {
    "OutputKey": "ContentBucketName",
    "OutputValue": "snapstudy-content-123456789012-us-east-1"
  }
]
```

### **Step 7: Verify Deployment**

```bash
# Test API health endpoint
curl https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/health

# Expected response:
# {"status":"healthy","timestamp":"2024-01-01T00:00:00Z"}
```

**Verify in AWS Console:**

1. **Lambda Functions:**
   - AWS Console → Lambda → Functions
   - Should see: `SnapStudyStack-ApiLambda...`

2. **DynamoDB Tables:**
   - AWS Console → DynamoDB → Tables
   - Should see: 6 tables (Users, Lessons, MicroLessons, Quizzes, UserEngagement, ChatHistory)

3. **API Gateway:**
   - AWS Console → API Gateway → APIs
   - Should see: `SnapStudy-RestApi`

4. **S3 Buckets:**
   - AWS Console → S3 → Buckets
   - Should see: `snapstudy-content-...`

5. **CloudWatch Dashboard:**
   - AWS Console → CloudWatch → Dashboards
   - Should see: `SnapStudy-Metrics`

6. **AWS WAF:**
   - AWS Console → WAF & Shield → Web ACLs
   - Should see: `SnapStudyApiWaf`

---

## 🌐 Frontend Deployment

### **Step 1: Configure Frontend Environment**

Create `frontend/.env.local`:

```bash
# Navigate to frontend directory
cd ../../frontend

# Create environment file
cat > .env.local << EOF
REACT_APP_API_URL=https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod
REACT_APP_USER_POOL_ID=us-east-1_ABC123XYZ
REACT_APP_USER_POOL_CLIENT_ID=1a2b3c4d5e6f7g8h9i0j1k2l3m
REACT_APP_AWS_REGION=us-east-1
EOF
```

**Replace with your actual values from CDK outputs!**

### **Step 2: Test Frontend Locally**

```bash
# Start development server
npm start

# Application should open at http://localhost:3000
```

**Expected behavior:**
- ✅ Page loads without errors
- ✅ Can see login/signup form
- ✅ API calls to backend work (check browser console)

**Browser Console Check:**
```javascript
// Open browser console (F12)
// You should see:
"SnapStudy frontend initialized"
"API URL: https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod"
```

### **Step 3: Build Production Frontend**

```bash
# Create production build
npm run build

# This creates an optimized build/ directory
```

**Expected output:**
```
Creating an optimized production build...
Compiled successfully.

File sizes after gzip:

  52.1 kB  build/static/js/main.abc123.js
  1.2 kB   build/static/css/main.def456.css

The build folder is ready to be deployed.
```

### **Step 4: Deploy Frontend to S3 (Optional)**

**Option A: Deploy to S3 + CloudFront**

```bash
# Create S3 bucket for frontend
aws s3 mb s3://snapstudy-frontend-$AWS_ACCOUNT_ID --region us-east-1

# Enable static website hosting
aws s3 website s3://snapstudy-frontend-$AWS_ACCOUNT_ID \
  --index-document index.html \
  --error-document index.html

# Upload build files
aws s3 sync build/ s3://snapstudy-frontend-$AWS_ACCOUNT_ID --delete

# Set public read policy
cat > bucket-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::snapstudy-frontend-$AWS_ACCOUNT_ID/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy \
  --bucket snapstudy-frontend-$AWS_ACCOUNT_ID \
  --policy file://bucket-policy.json

# Get website URL
echo "Frontend URL: http://snapstudy-frontend-$AWS_ACCOUNT_ID.s3-website-us-east-1.amazonaws.com"
```

**Option B: Use Vercel (Recommended for Demo)**

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Follow prompts:
# - Set up and deploy: Yes
# - Which scope: Your account
# - Link to existing project: No
# - Project name: snapstudy
# - Directory: ./
# - Override settings: No

# Production deployment
vercel --prod
```

**Option C: Use Netlify**

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy

# Follow prompts, then:
netlify deploy --prod
```

---

## ⚙️ Post-Deployment Configuration

### **Step 1: Create Test User**

```bash
# Navigate to backend
cd ../backend
source venv/bin/activate  # Activate virtual environment

# Run user creation script
python -c "
import boto3
import bcrypt
from datetime import datetime, timezone

cognito = boto3.client('cognito-idp', region_name='us-east-1')

user_pool_id = 'us-east-1_ABC123XYZ'  # Replace with your User Pool ID

# Create test user
response = cognito.admin_create_user(
    UserPoolId=user_pool_id,
    Username='test@example.com',
    UserAttributes=[
        {'Name': 'email', 'Value': 'test@example.com'},
        {'Name': 'email_verified', 'Value': 'true'},
        {'Name': 'name', 'Value': 'Test User'}
    ],
    MessageAction='SUPPRESS'  # Don't send welcome email
)

# Set permanent password
cognito.admin_set_user_password(
    UserPoolId=user_pool_id,
    Username='test@example.com',
    Password='TestPassword123!',
    Permanent=True
)

print('Test user created successfully!')
print('Email: test@example.com')
print('Password: TestPassword123!')
"
```

### **Step 2: Configure Cognito Callback URLs**

If deploying frontend to custom domain:

```bash
# Update User Pool Client with your frontend URL
aws cognito-idp update-user-pool-client \
  --user-pool-id us-east-1_ABC123XYZ \
  --client-id 1a2b3c4d5e6f7g8h9i0j1k2l3m \
  --callback-urls "http://localhost:3000/auth/callback","https://your-frontend-domain.com/auth/callback" \
  --logout-urls "http://localhost:3000/auth/logout","https://your-frontend-domain.com/auth/logout" \
  --region us-east-1
```

### **Step 3: Upload Sample Content (Optional)**

```bash
# Create sample PDF
cat > sample-lesson.txt << EOF
Introduction to AWS Lambda

AWS Lambda is a serverless compute service that runs your code in response to events.

Key Concepts:
1. Functions: Your code packaged as a Lambda function
2. Triggers: Events that invoke your function
3. Execution Role: IAM role for permissions
4. Layers: Shared code and dependencies

Benefits:
- No server management
- Automatic scaling
- Pay per use
- High availability
EOF

# Upload to S3
aws s3 cp sample-lesson.txt s3://snapstudy-content-$AWS_ACCOUNT_ID-us-east-1/samples/
```

### **Step 4: Enable CloudWatch Logs Insights**

```bash
# Create log group insights query
aws logs put-query-definition \
  --name "SnapStudy-Errors" \
  --query-string "fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc | limit 20" \
  --log-group-names "/aws/lambda/SnapStudyStack-ApiLambda" \
  --region us-east-1
```

---

## 🧪 Testing the Deployment

### **Test 1: API Health Check**

```bash
# Test health endpoint
curl https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/health

# Expected: {"status":"healthy","timestamp":"..."}
```

### **Test 2: User Authentication**

```bash
# Test login
curl -X POST https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'

# Expected: {"token":"eyJ...","user":{...}}
```

### **Test 3: Content Upload**

```bash
# Get auth token first (from login response)
TOKEN="eyJhbGciOiJIUzI1NiIs..."

# Test content upload
curl -X POST https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/api/v1/content/upload \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "text",
    "content": "This is a test lesson about Python programming.",
    "title": "Python Basics"
  }'

# Expected: {"lesson_id":"...","status":"processing"}
```

### **Test 4: Frontend Integration**

1. Open frontend URL in browser
2. **Sign up** with new account
3. **Upload** a PDF or text content
4. **Wait** for AI to generate micro-lessons
5. **Take** a quiz
6. **Verify** adaptive behavior (different difficulty based on score)
7. **Chat** with AI tutor

### **Test 5: CloudWatch Monitoring**

```bash
# Check Lambda logs
aws logs tail /aws/lambda/SnapStudyStack-ApiLambda --follow --region us-east-1

# Check DynamoDB metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=SnapStudy-Users \
  --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum \
  --region us-east-1
```

### **Test 6: Load Testing (Optional)**

```bash
# Install artillery
npm install -g artillery

# Create load test config
cat > load-test.yml << EOF
config:
  target: "https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod"
  phases:
    - duration: 60
      arrivalRate: 10
scenarios:
  - flow:
      - get:
          url: "/health"
EOF

# Run load test
artillery run load-test.yml
```

---

## 📊 Monitoring & Troubleshooting

### **CloudWatch Dashboard**

1. AWS Console → CloudWatch → Dashboards
2. Select `SnapStudy-Metrics`
3. View real-time metrics:
   - Lambda invocations, errors, duration
   - API Gateway requests, latency
   - DynamoDB throughput

### **CloudWatch Alarms**

Check alarm status:
```bash
aws cloudwatch describe-alarms --region us-east-1
```

### **Common Issues**

#### **Issue 1: "AccessDeniedException" from Bedrock**

**Cause:** Model access not enabled

**Solution:**
```bash
# Verify model access
aws bedrock list-foundation-models --region us-east-1 | grep claude-3-5-sonnet

# If empty, request access in AWS Console:
# Bedrock → Model access → Request access → Claude 3.5 Sonnet
```

#### **Issue 2: Lambda timeout errors**

**Cause:** Complex content processing taking too long

**Solution:**
```python
# Edit backend/infrastructure/stacks/snapstudy_stack.py:450
timeout=Duration.seconds(60)  # Increase from 30 to 60

# Redeploy
cdk deploy
```

#### **Issue 3: CORS errors in frontend**

**Cause:** API Gateway CORS not configured for your domain

**Solution:**
```python
# Edit backend/infrastructure/stacks/snapstudy_stack.py:418
allow_origins=["http://localhost:3000", "https://your-domain.com"]

# Redeploy
cdk deploy
```

#### **Issue 4: "ResourceNotFoundException" for DynamoDB**

**Cause:** Tables not created properly

**Solution:**
```bash
# Verify tables exist
aws dynamodb list-tables --region us-east-1

# If missing, redeploy stack
cdk destroy
cdk deploy
```

#### **Issue 5: High Bedrock costs**

**Cause:** Large prompts or too many requests

**Solution:**
```python
# Edit backend/src/services/bedrock.py:129
max_tokens=2000  # Reduce from 4000

# Add caching (advanced)
# Implement prompt caching to reduce token usage
```

### **Debugging Lambda Functions**

```bash
# View recent logs
aws logs tail /aws/lambda/SnapStudyStack-ApiLambda \
  --since 1h \
  --filter-pattern "ERROR" \
  --region us-east-1

# Invoke Lambda directly for testing
aws lambda invoke \
  --function-name SnapStudyStack-ApiLambda \
  --payload '{"httpMethod":"GET","path":"/health"}' \
  --region us-east-1 \
  response.json

cat response.json
```

### **Checking WAF Blocks**

```bash
# Get WAF metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/WAFV2 \
  --metric-name BlockedRequests \
  --dimensions Name=Rule,Value=ALL Name=WebACL,Value=SnapStudyApiWaf \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum \
  --region us-east-1
```

---

## 🧹 Cleanup

### **Warning:** This will delete all resources and data!

### **Step 1: Empty S3 Buckets**

```bash
# Empty content bucket
aws s3 rm s3://snapstudy-content-$AWS_ACCOUNT_ID-us-east-1 --recursive

# Empty frontend bucket (if created)
aws s3 rm s3://snapstudy-frontend-$AWS_ACCOUNT_ID --recursive

# Empty CDK bootstrap bucket
aws s3 rm s3://cdk-hnb659fds-assets-$AWS_ACCOUNT_ID-us-east-1 --recursive
```

### **Step 2: Destroy CDK Stack**

```bash
cd backend/infrastructure

# Destroy the stack
cdk destroy

# Confirm when prompted (type 'y')
```

**Expected output:**
```
Are you sure you want to delete: SnapStudyStack (y/n)? y
SnapStudyStack: destroying...

✅  SnapStudyStack: destroyed
```

### **Step 3: Delete S3 Buckets**

```bash
# Delete content bucket
aws s3 rb s3://snapstudy-content-$AWS_ACCOUNT_ID-us-east-1 --force

# Delete frontend bucket (if created)
aws s3 rb s3://snapstudy-frontend-$AWS_ACCOUNT_ID --force
```

### **Step 4: Delete CloudWatch Logs (Optional)**

```bash
# List log groups
aws logs describe-log-groups --region us-east-1 | grep SnapStudy

# Delete log groups
aws logs delete-log-group --log-group-name /aws/lambda/SnapStudyStack-ApiLambda --region us-east-1
```

### **Step 5: Verify Cleanup**

```bash
# Check CloudFormation stacks
aws cloudformation list-stacks --region us-east-1 | grep SnapStudy

# Should show status: DELETE_COMPLETE

# Check remaining resources
aws lambda list-functions --region us-east-1 | grep SnapStudy
aws dynamodb list-tables --region us-east-1 | grep SnapStudy
aws s3 ls | grep snapstudy

# All should return empty
```

---

## 📚 Additional Resources

### **AWS Documentation**
- [AWS Bedrock](https://docs.aws.amazon.com/bedrock/)
- [AWS CDK Python](https://docs.aws.amazon.com/cdk/v2/guide/work-with-cdk-python.html)
- [AWS Lambda](https://docs.aws.amazon.com/lambda/)
- [Amazon DynamoDB](https://docs.aws.amazon.com/dynamodb/)

### **SnapStudy Documentation**
- [README.md](./README.md) - Project overview
- [SUBMISSION.md](./SUBMISSION.md) - Hackathon submission details
- [AGENTCORE_INTEGRATION.md](./backend/AGENTCORE_INTEGRATION.md) - Agent architecture
- [ANALYTICS_SYSTEM_IMPLEMENTATION.md](./backend/ANALYTICS_SYSTEM_IMPLEMENTATION.md) - Analytics details

### **Troubleshooting**
- [GitHub Issues](https://github.com/yourusername/snapstudy/issues)
- [AWS Support](https://console.aws.amazon.com/support/)

### **Community**
- [AWS re:Post](https://repost.aws/)
- [Stack Overflow - AWS](https://stackoverflow.com/questions/tagged/amazon-web-services)

---

## 🎯 Quick Reference Commands

```bash
# Deploy backend
cd backend/infrastructure
cdk deploy

# Start frontend locally
cd frontend
npm start

# View Lambda logs
aws logs tail /aws/lambda/SnapStudyStack-ApiLambda --follow

# Check API health
curl https://YOUR-API-URL/prod/health

# Redeploy after changes
cd backend/infrastructure
cdk deploy --hotswap  # Fast deployment for Lambda code changes

# Full redeploy
cdk destroy && cdk deploy

# Check costs
aws ce get-cost-and-usage \
  --time-period Start=2025-10-01,End=2025-10-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

---

## 🚀 Next Steps

After successful deployment:

1. ✅ **Create demo video** showing the system in action
2. ✅ **Submit to hackathon** via DevPost
3. ✅ **Share with users** for feedback
4. ✅ **Monitor costs** and optimize if needed
5. ✅ **Add features** from the roadmap

---

## 📞 Support

If you encounter issues:

1. Check [Troubleshooting](#monitoring--troubleshooting) section
2. Review CloudWatch logs
3. Verify all prerequisites are met
4. Open GitHub issue with error details

---

**Deployment complete! 🎉**

Your SnapStudy AI learning platform is now live on AWS!
