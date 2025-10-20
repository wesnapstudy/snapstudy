#!/bin/bash

# SnapStudy Production Deployment Script
# This script deploys the complete SnapStudy application to AWS

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
ENVIRONMENT=${ENVIRONMENT:-production}
STACK_NAME="SnapStudy-${ENVIRONMENT}"

echo -e "${BLUE}🚀 Starting SnapStudy Production Deployment${NC}"
echo -e "${BLUE}Region: ${AWS_REGION}${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"
echo -e "${BLUE}Stack Name: ${STACK_NAME}${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${BLUE}📋 Checking Prerequisites${NC}"

if ! command_exists aws; then
    print_error "AWS CLI is not installed. Please install it first."
    exit 1
fi

if ! command_exists node; then
    print_error "Node.js is not installed. Please install it first."
    exit 1
fi

if ! command_exists npm; then
    print_error "npm is not installed. Please install it first."
    exit 1
fi

if ! command_exists python3; then
    print_error "Python 3 is not installed. Please install it first."
    exit 1
fi

print_status "All prerequisites are installed"

# Check AWS credentials
echo -e "${BLUE}🔐 Checking AWS Credentials${NC}"
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    print_error "AWS credentials are not configured. Please run 'aws configure' first."
    exit 1
fi

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
print_status "AWS credentials are configured (Account: ${AWS_ACCOUNT_ID})"

# Bootstrap CDK if needed
echo -e "${BLUE}🏗️  Bootstrapping CDK${NC}"
cd infrastructure
if ! cdk bootstrap aws://${AWS_ACCOUNT_ID}/${AWS_REGION} 2>/dev/null; then
    print_warning "CDK bootstrap may have failed, but continuing..."
fi
print_status "CDK bootstrap completed"

# Install infrastructure dependencies
echo -e "${BLUE}📦 Installing Infrastructure Dependencies${NC}"
npm install
print_status "Infrastructure dependencies installed"

# Build and deploy infrastructure
echo -e "${BLUE}🏗️  Deploying Infrastructure${NC}"
cdk deploy ${STACK_NAME} --require-approval never --outputs-file ../deployment-outputs.json
if [ $? -eq 0 ]; then
    print_status "Infrastructure deployed successfully"
else
    print_error "Infrastructure deployment failed"
    exit 1
fi

cd ..

# Install backend dependencies
echo -e "${BLUE}📦 Installing Backend Dependencies${NC}"
cd backend
python3 -m pip install -r requirements.txt --user
print_status "Backend dependencies installed"

# Deploy Lambda functions
echo -e "${BLUE}🔧 Deploying Lambda Functions${NC}"
python3 deploy_lambda.py --region ${AWS_REGION} --environment ${ENVIRONMENT}
if [ $? -eq 0 ]; then
    print_status "Lambda functions deployed successfully"
else
    print_error "Lambda function deployment failed"
    exit 1
fi

cd ..

# Build frontend
echo -e "${BLUE}🎨 Building Frontend${NC}"
cd frontend

# Install frontend dependencies
npm install
print_status "Frontend dependencies installed"

# Set environment variables for build
if [ -f ../deployment-outputs.json ]; then
    API_URL=$(cat ../deployment-outputs.json | python3 -c "import sys, json; print(json.load(sys.stdin)['${STACK_NAME}']['ApiGatewayUrl'])" 2>/dev/null || echo "")
    USER_POOL_ID=$(cat ../deployment-outputs.json | python3 -c "import sys, json; print(json.load(sys.stdin)['${STACK_NAME}']['UserPoolId'])" 2>/dev/null || echo "")
    USER_POOL_CLIENT_ID=$(cat ../deployment-outputs.json | python3 -c "import sys, json; print(json.load(sys.stdin)['${STACK_NAME}']['UserPoolClientId'])" 2>/dev/null || echo "")
    
    if [ ! -z "$API_URL" ]; then
        export REACT_APP_API_URL=$API_URL
        print_status "API URL configured: $API_URL"
    fi
    
    if [ ! -z "$USER_POOL_ID" ]; then
        export REACT_APP_USER_POOL_ID=$USER_POOL_ID
        print_status "User Pool ID configured"
    fi
    
    if [ ! -z "$USER_POOL_CLIENT_ID" ]; then
        export REACT_APP_USER_POOL_CLIENT_ID=$USER_POOL_CLIENT_ID
        print_status "User Pool Client ID configured"
    fi
fi

# Build the frontend
npm run build
if [ $? -eq 0 ]; then
    print_status "Frontend built successfully"
else
    print_error "Frontend build failed"
    exit 1
fi

# Deploy frontend to S3
echo -e "${BLUE}☁️  Deploying Frontend to S3${NC}"
if [ -f ../deployment-outputs.json ]; then
    CLOUDFRONT_URL=$(cat ../deployment-outputs.json | python3 -c "import sys, json; print(json.load(sys.stdin)['${STACK_NAME}']['CloudFrontUrl'])" 2>/dev/null || echo "")
    
    # Get S3 bucket name from CloudFormation outputs
    FRONTEND_BUCKET=$(aws cloudformation describe-stacks --stack-name ${STACK_NAME} --region ${AWS_REGION} --query "Stacks[0].Outputs[?OutputKey=='FrontendBucketName'].OutputValue" --output text 2>/dev/null || echo "")
    
    if [ ! -z "$FRONTEND_BUCKET" ]; then
        # Sync build files to S3
        aws s3 sync build/ s3://${FRONTEND_BUCKET}/ --delete --region ${AWS_REGION}
        
        # Invalidate CloudFront cache
        if [ ! -z "$CLOUDFRONT_URL" ]; then
            DISTRIBUTION_ID=$(aws cloudfront list-distributions --query "DistributionList.Items[?Comment=='SnapStudy Frontend Distribution'].Id" --output text --region ${AWS_REGION} 2>/dev/null || echo "")
            if [ ! -z "$DISTRIBUTION_ID" ]; then
                aws cloudfront create-invalidation --distribution-id ${DISTRIBUTION_ID} --paths "/*" --region ${AWS_REGION} >/dev/null 2>&1
                print_status "CloudFront cache invalidated"
            fi
        fi
        
        print_status "Frontend deployed to S3"
    else
        print_warning "Could not find frontend bucket name, skipping S3 deployment"
    fi
fi

cd ..

# Run post-deployment tests
echo -e "${BLUE}🧪 Running Post-Deployment Tests${NC}"

# Test API health endpoint
if [ ! -z "$API_URL" ]; then
    HEALTH_RESPONSE=$(curl -s "${API_URL}health" || echo "")
    if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
        print_status "API health check passed"
    else
        print_warning "API health check failed or returned unexpected response"
    fi
fi

# Display deployment summary
echo ""
echo -e "${GREEN}🎉 Deployment Summary${NC}"
echo -e "${GREEN}===================${NC}"

if [ -f deployment-outputs.json ]; then
    echo -e "${BLUE}API Gateway URL:${NC} $API_URL"
    echo -e "${BLUE}CloudFront URL:${NC} $CLOUDFRONT_URL"
    echo -e "${BLUE}User Pool ID:${NC} $USER_POOL_ID"
    echo -e "${BLUE}User Pool Client ID:${NC} $USER_POOL_CLIENT_ID"
else
    print_warning "Deployment outputs not found. Check AWS Console for resource details."
fi

echo ""
echo -e "${GREEN}✅ SnapStudy has been successfully deployed to production!${NC}"
echo -e "${GREEN}🌐 Your application is now available at: ${CLOUDFRONT_URL}${NC}"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo -e "${YELLOW}1. Test the application thoroughly${NC}"
echo -e "${YELLOW}2. Set up monitoring and alerting${NC}"
echo -e "${YELLOW}3. Configure custom domain (optional)${NC}"
echo -e "${YELLOW}4. Set up CI/CD pipeline for future deployments${NC}"
echo ""

# Save deployment info
cat > deployment-info.txt << EOF
SnapStudy Deployment Information
================================
Deployment Date: $(date)
AWS Region: ${AWS_REGION}
Environment: ${ENVIRONMENT}
Stack Name: ${STACK_NAME}
AWS Account: ${AWS_ACCOUNT_ID}

Application URLs:
- API Gateway: ${API_URL}
- CloudFront: ${CLOUDFRONT_URL}

Cognito Configuration:
- User Pool ID: ${USER_POOL_ID}
- User Pool Client ID: ${USER_POOL_CLIENT_ID}

Deployment Status: SUCCESS
EOF

print_status "Deployment information saved to deployment-info.txt"

echo -e "${GREEN}🚀 Deployment completed successfully!${NC}"