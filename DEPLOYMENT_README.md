# SnapStudy Deployment Guide

This guide covers the deployment of the SnapStudy platform to AWS, including both backend and frontend components.

## 🚀 Quick Start

### Option 1: Complete Deployment (Recommended)
```powershell
./deploy-snapstudy.ps1
```

### Option 2: Windows Batch File
Double-click `deploy.bat` and follow the menu prompts.

### Option 3: Individual Components
```powershell
# Backend only
./deploy-backend.ps1

# Frontend only (after backend is deployed)
./deploy-frontend.ps1
```

## 📋 Prerequisites

### Required Tools
- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **AWS CLI** configured with credentials
- **AWS CDK** (`npm install -g aws-cdk`)
- **PowerShell** (Windows/Linux/macOS)

### AWS Requirements
- AWS account with appropriate permissions
- AWS CLI configured (`aws configure`)
- CDK bootstrapped in target region (`cdk bootstrap`)

### Permissions Required
The AWS user/role needs permissions for:
- CloudFormation (full access)
- IAM (create/manage roles and policies)
- Lambda (create/manage functions)
- API Gateway (create/manage APIs)
- DynamoDB (create/manage tables)
- S3 (create/manage buckets)
- Cognito (create/manage user pools)
- Bedrock (invoke models)
- Textract, Transcribe, Polly (invoke services)

## 🏗️ Architecture Overview

### Backend Deployment
- **Target**: AWS Lambda + API Gateway (serverless)
- **Infrastructure**: AWS CDK (Python)
- **Services**: DynamoDB, S3, Cognito, Bedrock, etc.
- **Location**: `backend/` directory

### Frontend Deployment
- **Target**: S3 Static Website Hosting
- **Build**: React production build
- **CDN**: CloudFront (optional)
- **Location**: `frontend/` directory

## 📝 Deployment Scripts

### `deploy-snapstudy.ps1` (Master Script)
Complete deployment orchestration with the following options:

```powershell
# Deploy to development environment
./deploy-snapstudy.ps1 -Environment dev

# Deploy to production
./deploy-snapstudy.ps1 -Environment prod

# Deploy backend only
./deploy-snapstudy.ps1 -BackendOnly

# Deploy frontend only
./deploy-snapstudy.ps1 -FrontendOnly

# Skip tests and force deployment
./deploy-snapstudy.ps1 -SkipTests -Force
```

### `deploy-backend.ps1` (Backend Script)
Deploys AWS infrastructure and Lambda functions:

```powershell
# Basic deployment
./deploy-backend.ps1

# Production deployment
./deploy-backend.ps1 -Environment prod

# Skip tests
./deploy-backend.ps1 -SkipTests

# Force deployment without confirmation
./deploy-backend.ps1 -Force
```

### `deploy-frontend.ps1` (Frontend Script)
Builds and deploys React application:

```powershell
# Basic deployment
./deploy-frontend.ps1

# Specify API URL manually
./deploy-frontend.ps1 -ApiUrl "https://api.example.com"

# Skip build process
./deploy-frontend.ps1 -SkipBuild

# Production deployment
./deploy-frontend.ps1 -Environment prod
```

## 🔧 Configuration

### Environment Variables
The deployment uses environment variables from:
1. `infrastructure/.env` file
2. System environment variables
3. AWS CloudFormation outputs

### Key Configuration Files
- `infrastructure/.env` - AWS configuration
- `backend/requirements.txt` - Python dependencies
- `backend/infrastructure/requirements.txt` - CDK dependencies
- `frontend/package.json` - Node.js dependencies

## 📊 Deployment Process

### Backend Deployment Steps
1. **Prerequisites Check** - Verify tools and AWS credentials
2. **Dependencies Installation** - Install Python packages
3. **Testing** - Run backend tests (optional)
4. **CDK Bootstrap** - Bootstrap CDK if needed
5. **Infrastructure Synthesis** - Generate CloudFormation template
6. **Deployment** - Deploy to AWS
7. **Validation** - Test deployed services
8. **Output Generation** - Save deployment outputs

### Frontend Deployment Steps
1. **Prerequisites Check** - Verify tools and AWS credentials
2. **API URL Resolution** - Get backend API URL
3. **Environment Configuration** - Create `.env.production`
4. **Dependencies Installation** - Install Node.js packages
5. **Testing** - Run frontend tests (optional)
6. **Build** - Create production build
7. **S3 Deployment** - Upload to S3 bucket
8. **Website Configuration** - Configure S3 website
9. **Validation** - Test deployed website

## 🎯 Deployment Outputs

### Backend Outputs
Saved to `backend-outputs-{environment}.json`:
- REST API URL
- User Pool ID
- User Pool Client ID
- S3 Bucket Names
- DynamoDB Table Names

### Frontend Outputs
Saved to `frontend-deployment-{environment}.json`:
- Website URL
- S3 Bucket Name
- API URL
- Deployment timestamp

## 🔍 Troubleshooting

### Common Issues

#### 1. CDK Bootstrap Error
```
Error: This stack uses assets, so the toolkit stack must be deployed
```
**Solution**: Run `cdk bootstrap` in the infrastructure directory

#### 2. AWS Credentials Not Found
```
Error: Unable to locate credentials
```
**Solution**: Run `aws configure` or set environment variables

#### 3. Permission Denied
```
Error: User is not authorized to perform action
```
**Solution**: Ensure AWS user has required permissions (see Prerequisites)

#### 4. S3 Bucket Not Found
```
Error: S3 bucket does not exist
```
**Solution**: Deploy backend first to create the S3 bucket

#### 5. API URL Not Found
```
Error: Could not determine backend API URL
```
**Solution**: Deploy backend first or specify `-ApiUrl` parameter

### Debug Commands

```powershell
# Check AWS credentials
aws sts get-caller-identity

# Check CDK status
cdk list

# Check CloudFormation stacks
aws cloudformation list-stacks

# Check S3 buckets
aws s3 ls

# Test API endpoint
curl https://your-api-url/health
```

## 🌍 Environment Management

### Development Environment
```powershell
./deploy-snapstudy.ps1 -Environment dev
```
- Uses development configurations
- Enables debug logging
- Relaxed security settings

### Staging Environment
```powershell
./deploy-snapstudy.ps1 -Environment staging
```
- Production-like configuration
- Full security settings
- Performance monitoring

### Production Environment
```powershell
./deploy-snapstudy.ps1 -Environment prod
```
- Production optimizations
- Enhanced security
- Comprehensive monitoring
- No rollback on failure

## 📈 Monitoring and Maintenance

### Post-Deployment Checks
1. **API Health Check** - Test `/health` endpoint
2. **Frontend Loading** - Verify website loads correctly
3. **Authentication** - Test user registration/login
4. **Core Features** - Test lesson upload and processing
5. **AI Services** - Test chat and quiz generation

### Monitoring Setup
- CloudWatch dashboards for metrics
- CloudWatch alarms for errors
- API Gateway logging
- Lambda function monitoring

### Maintenance Tasks
- Regular dependency updates
- Security patches
- Performance optimization
- Cost optimization reviews

## 🔒 Security Considerations

### Production Deployment
- Use least privilege IAM roles
- Enable CloudTrail logging
- Configure WAF rules
- Set up VPC endpoints (optional)
- Enable encryption at rest and in transit

### Environment Separation
- Use separate AWS accounts for environments
- Implement proper access controls
- Use different domain names
- Separate monitoring and alerting

## 📞 Support

### Getting Help
1. Check the troubleshooting section above
2. Review CloudFormation events in AWS Console
3. Check CloudWatch logs for detailed errors
4. Verify all prerequisites are met

### Useful Resources
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [React Deployment Guide](https://create-react-app.dev/docs/deployment/)

---

## 🎉 Success!

After successful deployment, you'll have:
- ✅ Serverless backend running on AWS Lambda
- ✅ React frontend hosted on S3
- ✅ Complete AI-powered learning platform
- ✅ Scalable and cost-effective architecture

Your SnapStudy platform is now ready for users! 🚀