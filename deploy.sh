#!/bin/bash

################################################################################
# SnapStudy - Automated AWS Deployment Script
# This script deploys the complete SnapStudy application to AWS
################################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo "========================================="
    echo "$1"
    echo "========================================="
    echo ""
}

################################################################################
# STEP 1: Prerequisites Check
################################################################################

check_prerequisites() {
    print_header "STEP 1: Checking Prerequisites"

    local missing_tools=0

    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_success "Python installed: $PYTHON_VERSION"
    else
        log_error "Python 3.11+ is required but not found"
        missing_tools=1
    fi

    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        log_success "Node.js installed: $NODE_VERSION"
    else
        log_error "Node.js 16+ is required but not found"
        missing_tools=1
    fi

    # Check npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        log_success "npm installed: $NPM_VERSION"
    else
        log_error "npm is required but not found"
        missing_tools=1
    fi

    # Check AWS CLI
    if command -v aws &> /dev/null; then
        AWS_VERSION=$(aws --version | cut -d' ' -f1)
        log_success "AWS CLI installed: $AWS_VERSION"
    else
        log_error "AWS CLI is required but not found"
        log_info "Install from: https://aws.amazon.com/cli/"
        missing_tools=1
    fi

    # Check CDK
    if command -v cdk &> /dev/null; then
        CDK_VERSION=$(cdk --version)
        log_success "AWS CDK installed: $CDK_VERSION"
    else
        log_warning "AWS CDK not found. Installing..."
        npm install -g aws-cdk
        log_success "AWS CDK installed"
    fi

    if [ $missing_tools -eq 1 ]; then
        log_error "Missing required tools. Please install them and try again."
        exit 1
    fi

    log_success "All prerequisites met!"
}

################################################################################
# STEP 2: AWS Credentials Configuration
################################################################################

configure_aws_credentials() {
    print_header "STEP 2: AWS Credentials Configuration"

    # Check if AWS credentials are already configured
    if aws sts get-caller-identity &> /dev/null; then
        ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
        USER_ARN=$(aws sts get-caller-identity --query Arn --output text)
        log_success "AWS credentials already configured"
        log_info "Account ID: $ACCOUNT_ID"
        log_info "User: $USER_ARN"

        read -p "Do you want to use these credentials? (y/n): " use_existing
        if [[ $use_existing == "n" || $use_existing == "N" ]]; then
            setup_new_credentials
        fi
    else
        log_warning "AWS credentials not configured"
        setup_new_credentials
    fi

    # Export for use in script
    export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    export AWS_REGION=${AWS_REGION:-us-east-1}

    log_success "AWS Account ID: $AWS_ACCOUNT_ID"
    log_success "AWS Region: $AWS_REGION"
}

setup_new_credentials() {
    log_info "Please enter your AWS credentials"

    read -p "AWS Access Key ID: " aws_access_key
    read -sp "AWS Secret Access Key: " aws_secret_key
    echo ""
    read -p "AWS Region [us-east-1]: " aws_region
    aws_region=${aws_region:-us-east-1}

    # Configure AWS CLI
    aws configure set aws_access_key_id "$aws_access_key"
    aws configure set aws_secret_access_key "$aws_secret_key"
    aws configure set region "$aws_region"
    aws configure set output json

    export AWS_REGION=$aws_region

    # Verify credentials
    if aws sts get-caller-identity &> /dev/null; then
        log_success "AWS credentials configured successfully"
    else
        log_error "Failed to configure AWS credentials"
        exit 1
    fi
}

################################################################################
# STEP 3: Check Bedrock Access
################################################################################

check_bedrock_access() {
    print_header "STEP 3: Checking Amazon Bedrock Access"

    log_info "Checking if Claude 3.5 Sonnet is available..."

    if aws bedrock list-foundation-models \
        --region us-east-1 \
        --query 'modelSummaries[?modelId==`anthropic.claude-3-5-sonnet-20240620-v1:0`]' \
        --output text &> /dev/null; then
        log_success "Claude 3.5 Sonnet model access confirmed"
    else
        log_error "Claude 3.5 Sonnet model access not found"
        log_warning "You need to request model access in AWS Console:"
        log_info "1. Go to AWS Console → Amazon Bedrock"
        log_info "2. Select region: us-east-1"
        log_info "3. Click 'Model access' in left sidebar"
        log_info "4. Click 'Request model access'"
        log_info "5. Enable 'Anthropic Claude 3.5 Sonnet'"
        log_info "6. Wait for approval (usually instant)"
        echo ""
        read -p "Press Enter after you've enabled model access..."

        # Re-check
        if aws bedrock list-foundation-models \
            --region us-east-1 \
            --query 'modelSummaries[?modelId==`anthropic.claude-3-5-sonnet-20240620-v1:0`]' \
            --output text &> /dev/null; then
            log_success "Model access confirmed!"
        else
            log_error "Still cannot access model. Please check AWS Console."
            exit 1
        fi
    fi
}

################################################################################
# STEP 4: Backend Setup
################################################################################

setup_backend() {
    print_header "STEP 4: Backend Setup"

    log_info "Navigating to backend directory..."
    cd backend

    # Create virtual environment
    log_info "Creating Python virtual environment..."
    python3 -m venv venv
    log_success "Virtual environment created"

    # Activate virtual environment
    log_info "Activating virtual environment..."
    source venv/bin/activate || . venv/Scripts/activate
    log_success "Virtual environment activated"

    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip --quiet

    # Install dependencies
    log_info "Installing Python dependencies (this may take a few minutes)..."
    pip install -r requirements.txt --quiet
    log_success "Python dependencies installed"

    # Create .env file
    log_info "Creating .env file..."
    cat > .env << EOF
AWS_REGION=$AWS_REGION
AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
JWT_SECRET_KEY=$(openssl rand -hex 32 || echo "change-this-in-production-$(date +%s)")
EOF
    log_success ".env file created"

    cd ..
}

################################################################################
# STEP 5: CDK Bootstrap
################################################################################

bootstrap_cdk() {
    print_header "STEP 5: CDK Bootstrap"

    log_info "Checking if CDK is already bootstrapped..."

    if aws cloudformation describe-stacks \
        --stack-name CDKToolkit \
        --region $AWS_REGION &> /dev/null; then
        log_success "CDK already bootstrapped in this account/region"
    else
        log_info "Bootstrapping CDK (first-time setup)..."
        log_warning "This creates an S3 bucket and IAM roles for CDK deployments"

        cd backend/infrastructure
        cdk bootstrap aws://$AWS_ACCOUNT_ID/$AWS_REGION

        if [ $? -eq 0 ]; then
            log_success "CDK bootstrap completed"
        else
            log_error "CDK bootstrap failed"
            exit 1
        fi

        cd ../..
    fi
}

################################################################################
# STEP 6: Install CDK Dependencies
################################################################################

install_cdk_dependencies() {
    print_header "STEP 6: Installing CDK Dependencies"

    cd backend/infrastructure

    log_info "Installing Node.js dependencies..."
    npm install
    log_success "CDK dependencies installed"

    cd ../..
}

################################################################################
# STEP 7: Synthesize CloudFormation Template
################################################################################

synthesize_template() {
    print_header "STEP 7: Synthesizing CloudFormation Template"

    cd backend/infrastructure

    log_info "Generating CloudFormation template..."
    cdk synth > /dev/null

    if [ $? -eq 0 ]; then
        log_success "CloudFormation template generated successfully"
        log_info "Template location: backend/infrastructure/cdk.out/"
    else
        log_error "Failed to synthesize template"
        exit 1
    fi

    cd ../..
}

################################################################################
# STEP 8: Deploy Infrastructure
################################################################################

deploy_infrastructure() {
    print_header "STEP 8: Deploying Infrastructure to AWS"

    log_warning "This will create AWS resources in your account"
    log_info "Estimated deployment time: 5-10 minutes"
    log_info "Resources to be created:"
    log_info "  - Lambda Function (API)"
    log_info "  - API Gateway (REST API)"
    log_info "  - DynamoDB Tables (6 tables)"
    log_info "  - S3 Bucket (content storage)"
    log_info "  - Cognito User Pool"
    log_info "  - CloudWatch Dashboard"
    log_info "  - AWS WAF Web ACL"
    echo ""

    read -p "Continue with deployment? (y/n): " confirm_deploy
    if [[ $confirm_deploy != "y" && $confirm_deploy != "Y" ]]; then
        log_warning "Deployment cancelled"
        exit 0
    fi

    cd backend/infrastructure

    log_info "Starting deployment..."
    cdk deploy --require-approval never

    if [ $? -eq 0 ]; then
        log_success "Infrastructure deployed successfully!"
    else
        log_error "Deployment failed"
        exit 1
    fi

    cd ../..
}

################################################################################
# STEP 9: Save Deployment Outputs
################################################################################

save_outputs() {
    print_header "STEP 9: Saving Deployment Outputs"

    log_info "Retrieving CloudFormation outputs..."

    aws cloudformation describe-stacks \
        --stack-name SnapStudyStack \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs' \
        --output json > deployment-outputs.json

    if [ $? -eq 0 ]; then
        log_success "Outputs saved to deployment-outputs.json"

        # Extract key outputs
        export API_URL=$(jq -r '.[] | select(.OutputKey=="RestApiUrl") | .OutputValue' deployment-outputs.json)
        export USER_POOL_ID=$(jq -r '.[] | select(.OutputKey=="UserPoolId") | .OutputValue' deployment-outputs.json)
        export USER_POOL_CLIENT_ID=$(jq -r '.[] | select(.OutputKey=="UserPoolClientId") | .OutputValue' deployment-outputs.json)
        export CONTENT_BUCKET=$(jq -r '.[] | select(.OutputKey=="ContentBucketName") | .OutputValue' deployment-outputs.json)

        echo ""
        log_success "Deployment Outputs:"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "API URL: $API_URL"
        echo "User Pool ID: $USER_POOL_ID"
        echo "User Pool Client ID: $USER_POOL_CLIENT_ID"
        echo "Content Bucket: $CONTENT_BUCKET"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
    else
        log_error "Failed to retrieve outputs"
    fi
}

################################################################################
# STEP 10: Test Deployment
################################################################################

test_deployment() {
    print_header "STEP 10: Testing Deployment"

    log_info "Testing API health endpoint..."

    HEALTH_RESPONSE=$(curl -s "$API_URL/health")

    if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
        log_success "API is healthy!"
        log_info "Response: $HEALTH_RESPONSE"
    else
        log_warning "API health check returned unexpected response"
        log_info "Response: $HEALTH_RESPONSE"
    fi

    # Test root endpoint
    log_info "Testing root endpoint..."
    ROOT_RESPONSE=$(curl -s "$API_URL/")

    if [[ $ROOT_RESPONSE == *"SnapStudy"* ]]; then
        log_success "Root endpoint is working!"
    else
        log_warning "Root endpoint returned unexpected response"
    fi
}

################################################################################
# STEP 11: Create Test User
################################################################################

create_test_user() {
    print_header "STEP 11: Creating Test User"

    read -p "Do you want to create a test user? (y/n): " create_user
    if [[ $create_user != "y" && $create_user != "Y" ]]; then
        log_info "Skipping test user creation"
        return
    fi

    read -p "Test user email [test@example.com]: " test_email
    test_email=${test_email:-test@example.com}

    read -sp "Test user password [TestPassword123!]: " test_password
    echo ""
    test_password=${test_password:-TestPassword123!}

    log_info "Creating test user..."

    # Create user
    aws cognito-idp admin-create-user \
        --user-pool-id $USER_POOL_ID \
        --username "$test_email" \
        --user-attributes Name=email,Value="$test_email" Name=email_verified,Value=true Name=name,Value="Test User" \
        --message-action SUPPRESS \
        --region $AWS_REGION &> /dev/null

    # Set permanent password
    aws cognito-idp admin-set-user-password \
        --user-pool-id $USER_POOL_ID \
        --username "$test_email" \
        --password "$test_password" \
        --permanent \
        --region $AWS_REGION &> /dev/null

    if [ $? -eq 0 ]; then
        log_success "Test user created successfully!"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Test User Credentials:"
        echo "Email: $test_email"
        echo "Password: $test_password"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
    else
        log_warning "Failed to create test user (may already exist)"
    fi
}

################################################################################
# STEP 12: Frontend Setup (Optional)
################################################################################

setup_frontend() {
    print_header "STEP 12: Frontend Setup (Optional)"

    read -p "Do you want to set up the frontend? (y/n): " setup_fe
    if [[ $setup_fe != "y" && $setup_fe != "Y" ]]; then
        log_info "Skipping frontend setup"
        return
    fi

    cd frontend

    log_info "Installing frontend dependencies..."
    npm install
    log_success "Frontend dependencies installed"

    # Create .env.local
    log_info "Creating frontend configuration..."
    cat > .env.local << EOF
REACT_APP_API_URL=$API_URL
REACT_APP_USER_POOL_ID=$USER_POOL_ID
REACT_APP_USER_POOL_CLIENT_ID=$USER_POOL_CLIENT_ID
REACT_APP_AWS_REGION=$AWS_REGION
EOF
    log_success "Frontend configuration created"

    log_info "Building frontend..."
    npm run build

    if [ $? -eq 0 ]; then
        log_success "Frontend build completed"
        log_info "Build files located in: frontend/build/"
    else
        log_error "Frontend build failed"
    fi

    cd ..
}

################################################################################
# STEP 13: Display Final Summary
################################################################################

display_summary() {
    print_header "🎉 DEPLOYMENT COMPLETE!"

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "                    SnapStudy Deployment Summary"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "✅ Backend Infrastructure:"
    echo "   API URL: $API_URL"
    echo "   Region: $AWS_REGION"
    echo "   Account: $AWS_ACCOUNT_ID"
    echo ""
    echo "✅ Cognito Authentication:"
    echo "   User Pool ID: $USER_POOL_ID"
    echo "   Client ID: $USER_POOL_CLIENT_ID"
    echo ""
    echo "✅ Storage:"
    echo "   S3 Bucket: $CONTENT_BUCKET"
    echo ""
    echo "📝 Next Steps:"
    echo "   1. Test the API: curl $API_URL/health"
    echo "   2. View CloudWatch Dashboard: AWS Console → CloudWatch → Dashboards"
    echo "   3. Check WAF Rules: AWS Console → WAF & Shield"
    echo "   4. Deploy frontend: cd frontend && npm start"
    echo ""
    echo "📚 Documentation:"
    echo "   - README.md - Project overview"
    echo "   - DEPLOYMENT_GUIDE.md - Detailed deployment guide"
    echo "   - SUBMISSION.md - Hackathon submission details"
    echo ""
    echo "🔧 Useful Commands:"
    echo "   - View logs: aws logs tail /aws/lambda/SnapStudyStack-ApiLambda --follow"
    echo "   - Redeploy: cd backend/infrastructure && cdk deploy"
    echo "   - Destroy: cd backend/infrastructure && cdk destroy"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Save summary to file
    cat > DEPLOYMENT_SUMMARY.txt << EOF
SnapStudy Deployment Summary
Generated: $(date)

API URL: $API_URL
User Pool ID: $USER_POOL_ID
User Pool Client ID: $USER_POOL_CLIENT_ID
Content Bucket: $CONTENT_BUCKET
Region: $AWS_REGION
Account ID: $AWS_ACCOUNT_ID

CloudFormation Stack: SnapStudyStack
Status: Deployed

Resources Created:
- Lambda Function: SnapStudyStack-ApiLambda
- API Gateway: SnapStudy-RestApi
- DynamoDB Tables: 6 (Users, Lessons, MicroLessons, Quizzes, UserEngagement, ChatHistory)
- S3 Bucket: $CONTENT_BUCKET
- Cognito User Pool: $USER_POOL_ID
- CloudWatch Dashboard: SnapStudy-Metrics
- AWS WAF: SnapStudyApiWaf

Next Steps:
1. Test API: curl $API_URL/health
2. Access CloudWatch Dashboard
3. Deploy frontend
4. Create demo video
5. Submit to hackathon

Deployment Time: $(date)
EOF

    log_success "Deployment summary saved to DEPLOYMENT_SUMMARY.txt"
}

################################################################################
# MAIN EXECUTION
################################################################################

main() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                                                               ║"
    echo "║              SnapStudy AWS Deployment Script                  ║"
    echo "║                                                               ║"
    echo "║  This script will deploy SnapStudy to your AWS account       ║"
    echo "║                                                               ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""

    # Execute deployment steps
    check_prerequisites
    configure_aws_credentials
    check_bedrock_access
    setup_backend
    bootstrap_cdk
    install_cdk_dependencies
    synthesize_template
    deploy_infrastructure
    save_outputs
    test_deployment
    create_test_user
    setup_frontend
    display_summary

    log_success "Deployment script completed successfully! 🎉"
}

# Run main function
main "$@"
