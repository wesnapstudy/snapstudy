# SnapStudy Infrastructure Deployment Guide

This guide walks you through deploying the SnapStudy AWS infrastructure using AWS CDK.

## Prerequisites

### 1. AWS Account Setup
- AWS account with appropriate permissions
- AWS CLI installed and configured
- Sufficient service limits for the resources being created

### 2. Development Environment
- Node.js 18+ installed
- AWS CDK 2.87.0+ installed globally: `npm install -g aws-cdk`
- TypeScript installed: `npm install -g typescript`

### 3. Required AWS Services
Ensure the following services are available in your target region:
- DynamoDB
- S3
- Cognito
- API Gateway
- Lambda
- Bedrock (for Claude models)
- CloudWatch
- IAM

## Step-by-Step Deployment

### 1. Clone and Setup
```bash
cd snapstudy/infrastructure
npm install
```

### 2. Configure Environment and AWS Credentials

#### Option 1: Environment Variables (Recommended)
Set AWS credentials as environment variables:
```bash
# Windows PowerShell
$env:AWS_ACCESS_KEY_ID="your_access_key_here"
$env:AWS_SECRET_ACCESS_KEY="your_secret_key_here"
$env:AWS_REGION="us-east-1"

# Windows Command Prompt
set AWS_ACCESS_KEY_ID=your_access_key_here
set AWS_SECRET_ACCESS_KEY=your_secret_key_here
set AWS_REGION=us-east-1

# Linux/Mac
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
export AWS_REGION=us-east-1
```

#### Option 2: .env File (Fallback)
```bash
cp .env.example .env
```

Edit `.env` with your specific values:
```bash
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012

# AWS Credentials (uncomment and fill in if not using environment variables)
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

ENVIRONMENT=dev
ALERT_EMAIL=your-email@example.com
```

#### Option 3: AWS CLI Configuration
```bash
aws configure
```

#### Verify Credentials
Run the credential loading script to verify your setup:
```bash
# PowerShell
powershell -ExecutionPolicy Bypass -File "scripts/load-aws-credentials.ps1" -Verbose

# Or use the simple check
powershell -ExecutionPolicy Bypass -File "scripts/check.ps1"
```

### 3. Validate Configuration
```bash
npm run build
npm test
```

### 4. Bootstrap CDK (First Time Only)
```bash
cdk bootstrap aws://ACCOUNT-NUMBER/REGION
```

### 5. Review Infrastructure
```bash
cdk synth
```

This generates CloudFormation templates. Review them before deployment.

### 6. Deploy Infrastructure

#### Load AWS Credentials First
```bash
# Load and verify AWS credentials
powershell -ExecutionPolicy Bypass -File "scripts/load-aws-credentials.ps1" -Verbose
```

#### Quick Deployment
```bash
# Windows PowerShell (Recommended)
powershell -ExecutionPolicy Bypass -File "scripts/deploy.ps1"

# With options
powershell -ExecutionPolicy Bypass -File "scripts/deploy.ps1" -Environment dev -Verbose

# Or using bash (if available)
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

#### Manual Deployment
```bash
# Build the project
npm run build

# Synthesize the CloudFormation template
cdk synth

# Deploy the stack
cdk deploy --require-approval never
```

#### Environment-Specific Deployment
```bash
# Development
powershell -ExecutionPolicy Bypass -File "scripts/deploy-with-config.sh" -e dev

# Staging
powershell -ExecutionPolicy Bypass -File "scripts/deploy-with-config.sh" -e staging

# Production (requires additional confirmation)
powershell -ExecutionPolicy Bypass -File "scripts/deploy-with-config.sh" -e prod --alert-email admin@company.com
```

### 7. Verify Deployment
After deployment, verify the following resources were created:

#### DynamoDB Tables
- SnapStudy-Users
- SnapStudy-Lessons  
- SnapStudy-MicroLessons
- SnapStudy-Quizzes
- SnapStudy-UserEngagement
- SnapStudy-ChatHistory

#### S3 Bucket
- snapstudy-content-{account}-{region}

#### Cognito
- User Pool: SnapStudy-UserPool
- User Pool Client: SnapStudy-WebClient
- Identity Pool: SnapStudy-IdentityPool

#### API Gateway
- REST API: SnapStudy-RestApi
- WebSocket API: SnapStudy-WebSocketApi

#### IAM Roles
- SnapStudy-AuthLambdaRole
- SnapStudy-ContentLambdaRole
- SnapStudy-AdaptiveLambdaRole
- SnapStudy-ChatLambdaRole
- SnapStudy-StepFunctionsRole

## Post-Deployment Configuration

### 1. Note Output Values
The deployment will output important values:
```
UserPoolId = us-east-1_XXXXXXXXX
UserPoolClientId = XXXXXXXXXXXXXXXXXXXXXXXXXX
IdentityPoolId = us-east-1:XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
RestApiUrl = https://XXXXXXXXXX.execute-api.us-east-1.amazonaws.com/prod/
WebSocketApiUrl = wss://XXXXXXXXXX.execute-api.us-east-1.amazonaws.com/prod
ContentBucketName = snapstudy-content-123456789012-us-east-1
```

### 2. Configure Frontend Application
Use these values to configure your frontend application:
```javascript
const config = {
  cognito: {
    userPoolId: 'us-east-1_XXXXXXXXX',
    userPoolClientId: 'XXXXXXXXXXXXXXXXXXXXXXXXXX',
    identityPoolId: 'us-east-1:XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
  },
  api: {
    restApiUrl: 'https://XXXXXXXXXX.execute-api.us-east-1.amazonaws.com/prod/',
    webSocketApiUrl: 'wss://XXXXXXXXXX.execute-api.us-east-1.amazonaws.com/prod'
  },
  s3: {
    bucketName: 'snapstudy-content-123456789012-us-east-1'
  }
};
```

### 3. Set Up Monitoring
- Access CloudWatch Dashboard: Check the DashboardUrl output
- Configure SNS topic subscriptions for alerts
- Set up additional monitoring as needed

### 4. Enable Bedrock Models
Ensure Claude models are enabled in your AWS account:
1. Go to AWS Bedrock console
2. Navigate to Model access
3. Enable access to:
   - Claude 3.5 Sonnet
   - Claude 3 Haiku

## Environment-Specific Deployments

### Development
```bash
ENVIRONMENT=dev cdk deploy
```

### Staging
```bash
ENVIRONMENT=staging cdk deploy --profile staging
```

### Production
```bash
ENVIRONMENT=prod cdk deploy --profile production
```

## AWS Credentials Priority

The deployment system loads AWS credentials in the following order:

1. **Environment Variables** (highest priority)
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_SESSION_TOKEN` (for temporary credentials)
   - `AWS_REGION`

2. **.env File** (fallback)
   - Loads credentials from `.env` file if not found in environment variables
   - Uncomment and fill in the AWS credential lines

3. **AWS CLI Configuration** (lowest priority)
   - Uses credentials from `~/.aws/credentials`
   - Set up with `aws configure`

### Credential Verification

Always verify your credentials before deployment:
```bash
# Comprehensive check with verbose output
powershell -ExecutionPolicy Bypass -File "scripts/load-aws-credentials.ps1" -Verbose

# Quick validation
aws sts get-caller-identity
```

## Troubleshooting

### Common Issues

#### 1. AWS Credentials Issues
```
Unable to locate credentials
```
**Solution**: 
1. Run the credential loading script: `scripts/load-aws-credentials.ps1`
2. Check if credentials are set in environment variables
3. Verify `.env` file has correct credentials
4. Run `aws configure` as fallback

#### 2. Bootstrap Error
```
Error: This stack uses assets, so the toolkit stack must be deployed to the environment
```
**Solution**: Run `cdk bootstrap` first

#### 2. Permission Denied
```
User: arn:aws:iam::123456789012:user/username is not authorized to perform: iam:CreateRole
```
**Solution**: Ensure your AWS user has sufficient IAM permissions

#### 3. Service Limit Exceeded
```
LimitExceededException: Too many tables
```
**Solution**: Check AWS service limits and request increases if needed

#### 4. Region Not Supported
```
ValidationException: Bedrock is not supported in this region
```
**Solution**: Deploy to a region that supports all required services

### Validation Commands

```bash
# Check stack status
aws cloudformation describe-stacks --stack-name SnapStudyStack

# List DynamoDB tables
aws dynamodb list-tables --query 'TableNames[?starts_with(@, `SnapStudy`)]'

# Check S3 bucket
aws s3 ls | grep snapstudy-content

# Verify Cognito User Pool
aws cognito-idp list-user-pools --max-results 10 --query 'UserPools[?Name==`SnapStudy-UserPool`]'

# Test API Gateway
curl -X GET https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/prod/health
```

## Cleanup

To destroy the infrastructure:

```bash
# Using script
chmod +x scripts/destroy.sh
./scripts/destroy.sh

# Or manual
cdk destroy
```

**Warning**: This will permanently delete all resources and data.

## Security Considerations

### 1. IAM Roles
- All roles follow least privilege principle
- Regular review and rotation of permissions

### 2. Data Encryption
- All DynamoDB tables encrypted at rest
- S3 bucket encrypted with AES-256
- API Gateway uses HTTPS/TLS

### 3. Network Security
- API Gateway configured with CORS
- S3 bucket blocks public access
- CloudWatch logging enabled

### 4. Monitoring
- CloudWatch alarms for critical metrics
- SNS notifications for alerts
- Detailed logging for audit trails

## Cost Optimization

### 1. DynamoDB
- On-demand billing for variable workloads
- TTL configured for temporary data

### 2. S3
- Lifecycle policies for cost optimization
- Intelligent tiering for long-term storage

### 3. API Gateway
- Throttling to prevent unexpected costs
- Caching for frequently accessed data

### 4. CloudWatch
- Log retention policies to manage costs
- Metric filters for relevant data only

## Next Steps

After successful infrastructure deployment:

1. **Deploy Lambda Functions**: Set up the backend Lambda functions
2. **Configure Frontend**: Update frontend with infrastructure outputs
3. **Set Up CI/CD**: Implement automated deployment pipelines
4. **Load Testing**: Validate performance under expected load
5. **Security Review**: Conduct security assessment
6. **Monitoring Setup**: Configure additional monitoring and alerting
7. **Documentation**: Update API documentation and user guides

## Support

For infrastructure-related issues:

1. Check CloudFormation events in AWS Console
2. Review CloudWatch logs for detailed error messages
3. Validate AWS service limits and quotas
4. Ensure all required services are available in your region

For additional help, refer to:
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [AWS CloudFormation Documentation](https://docs.aws.amazon.com/cloudformation/)
- [AWS Service Documentation](https://docs.aws.amazon.com/)