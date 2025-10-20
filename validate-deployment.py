#!/usr/bin/env python3
"""
SnapStudy Deployment Validation Script

This script validates that all components of SnapStudy are properly deployed and functioning.
"""

import json
import requests
import boto3
import time
import sys
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeploymentValidator:
    """Validates SnapStudy deployment."""
    
    def __init__(self, region: str = 'us-east-1', stack_name: str = 'SnapStudy-production'):
        self.region = region
        self.stack_name = stack_name
        self.cloudformation = boto3.client('cloudformation', region_name=region)
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.dynamodb = boto3.client('dynamodb', region_name=region)
        self.s3 = boto3.client('s3', region_name=region)
        self.cognito = boto3.client('cognito-idp', region_name=region)
        self.apigateway = boto3.client('apigateway', region_name=region)
        
        self.validation_results = []
        self.stack_outputs = {}
    
    def validate_deployment(self) -> bool:
        """Run complete deployment validation."""
        logger.info("🔍 Starting SnapStudy deployment validation")
        
        try:
            # Get stack outputs
            self._get_stack_outputs()
            
            # Run validation tests
            self._validate_infrastructure()
            self._validate_lambda_functions()
            self._validate_dynamodb_tables()
            self._validate_s3_buckets()
            self._validate_cognito()
            self._validate_api_gateway()
            self._validate_frontend()
            self._validate_end_to_end()
            
            # Generate report
            self._generate_report()
            
            # Check if all validations passed
            failed_tests = [result for result in self.validation_results if not result['passed']]
            
            if failed_tests:
                logger.error(f"❌ {len(failed_tests)} validation tests failed")
                return False
            else:
                logger.info("✅ All validation tests passed")
                return True
                
        except Exception as e:
            logger.error(f"❌ Validation failed with error: {str(e)}")
            return False
    
    def _get_stack_outputs(self):
        """Get CloudFormation stack outputs."""
        try:
            response = self.cloudformation.describe_stacks(StackName=self.stack_name)
            stack = response['Stacks'][0]
            
            for output in stack.get('Outputs', []):
                self.stack_outputs[output['OutputKey']] = output['OutputValue']
            
            logger.info(f"✅ Retrieved {len(self.stack_outputs)} stack outputs")
            
        except Exception as e:
            logger.error(f"❌ Failed to get stack outputs: {str(e)}")
            raise
    
    def _validate_infrastructure(self):
        """Validate CloudFormation infrastructure."""
        logger.info("🏗️  Validating infrastructure...")
        
        try:
            # Check stack status
            response = self.cloudformation.describe_stacks(StackName=self.stack_name)
            stack = response['Stacks'][0]
            stack_status = stack['StackStatus']
            
            if stack_status == 'CREATE_COMPLETE' or stack_status == 'UPDATE_COMPLETE':
                self._add_result("Infrastructure", "Stack Status", True, f"Stack is in {stack_status} state")
            else:
                self._add_result("Infrastructure", "Stack Status", False, f"Stack is in {stack_status} state")
            
            # Check required outputs exist
            required_outputs = [
                'ApiGatewayUrl',
                'CloudFrontUrl',
                'UserPoolId',
                'UserPoolClientId',
                'ContentBucketName',
                'MainApiFunctionArn'
            ]
            
            for output_key in required_outputs:
                if output_key in self.stack_outputs:
                    self._add_result("Infrastructure", f"Output {output_key}", True, "Output exists")
                else:
                    self._add_result("Infrastructure", f"Output {output_key}", False, "Output missing")
            
        except Exception as e:
            self._add_result("Infrastructure", "Stack Validation", False, str(e))
    
    def _validate_lambda_functions(self):
        """Validate Lambda functions."""
        logger.info("🔧 Validating Lambda functions...")
        
        expected_functions = [
            'snapstudy-api',
            'snapstudy-content-processor',
            'snapstudy-multimedia-processor'
        ]
        
        for function_name in expected_functions:
            try:
                response = self.lambda_client.get_function(FunctionName=function_name)
                
                # Check function state
                state = response['Configuration']['State']
                if state == 'Active':
                    self._add_result("Lambda", f"{function_name} State", True, "Function is active")
                else:
                    self._add_result("Lambda", f"{function_name} State", False, f"Function state is {state}")
                
                # Check runtime
                runtime = response['Configuration']['Runtime']
                if runtime.startswith('python3'):
                    self._add_result("Lambda", f"{function_name} Runtime", True, f"Runtime is {runtime}")
                else:
                    self._add_result("Lambda", f"{function_name} Runtime", False, f"Unexpected runtime: {runtime}")
                
                # Test function invocation (for API function only)
                if function_name == 'snapstudy-api':
                    self._test_lambda_invocation(function_name)
                
            except Exception as e:
                self._add_result("Lambda", f"{function_name} Existence", False, str(e))
    
    def _test_lambda_invocation(self, function_name: str):
        """Test Lambda function invocation."""
        try:
            # Create a test event
            test_event = {
                "httpMethod": "GET",
                "path": "/health",
                "headers": {},
                "queryStringParameters": None,
                "body": None,
                "requestContext": {
                    "requestId": "test-validation-request"
                }
            }
            
            response = self.lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(test_event)
            )
            
            if response['StatusCode'] == 200:
                payload = json.loads(response['Payload'].read())
                if payload.get('statusCode') == 200:
                    self._add_result("Lambda", f"{function_name} Invocation", True, "Function responds correctly")
                else:
                    self._add_result("Lambda", f"{function_name} Invocation", False, f"Function returned status {payload.get('statusCode')}")
            else:
                self._add_result("Lambda", f"{function_name} Invocation", False, f"Invocation failed with status {response['StatusCode']}")
                
        except Exception as e:
            self._add_result("Lambda", f"{function_name} Invocation", False, str(e))
    
    def _validate_dynamodb_tables(self):
        """Validate DynamoDB tables."""
        logger.info("🗄️  Validating DynamoDB tables...")
        
        expected_tables = [
            'SnapStudy-Users',
            'SnapStudy-Lessons',
            'SnapStudy-MicroLessons',
            'SnapStudy-Quizzes',
            'SnapStudy-UserEngagement',
            'SnapStudy-ChatHistory',
            'SnapStudy-AudioLessons',
            'SnapStudy-VideoLessons'
        ]
        
        for table_name in expected_tables:
            try:
                response = self.dynamodb.describe_table(TableName=table_name)
                table_status = response['Table']['TableStatus']
                
                if table_status == 'ACTIVE':
                    self._add_result("DynamoDB", f"{table_name} Status", True, "Table is active")
                else:
                    self._add_result("DynamoDB", f"{table_name} Status", False, f"Table status is {table_status}")
                
                # Check billing mode
                billing_mode = response['Table']['BillingModeSummary']['BillingMode']
                if billing_mode == 'PAY_PER_REQUEST':
                    self._add_result("DynamoDB", f"{table_name} Billing", True, "Pay-per-request billing enabled")
                else:
                    self._add_result("DynamoDB", f"{table_name} Billing", False, f"Billing mode is {billing_mode}")
                
            except Exception as e:
                self._add_result("DynamoDB", f"{table_name} Existence", False, str(e))
    
    def _validate_s3_buckets(self):
        """Validate S3 buckets."""
        logger.info("🪣 Validating S3 buckets...")
        
        # Check content bucket
        content_bucket = self.stack_outputs.get('ContentBucketName')
        if content_bucket:
            try:
                self.s3.head_bucket(Bucket=content_bucket)
                self._add_result("S3", "Content Bucket Existence", True, f"Bucket {content_bucket} exists")
                
                # Check bucket encryption
                try:
                    response = self.s3.get_bucket_encryption(Bucket=content_bucket)
                    self._add_result("S3", "Content Bucket Encryption", True, "Bucket encryption is enabled")
                except self.s3.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                        self._add_result("S3", "Content Bucket Encryption", False, "Bucket encryption is not enabled")
                    else:
                        raise
                
            except Exception as e:
                self._add_result("S3", "Content Bucket Existence", False, str(e))
        else:
            self._add_result("S3", "Content Bucket Configuration", False, "Content bucket name not found in outputs")
    
    def _validate_cognito(self):
        """Validate Cognito User Pool."""
        logger.info("🔐 Validating Cognito...")
        
        user_pool_id = self.stack_outputs.get('UserPoolId')
        user_pool_client_id = self.stack_outputs.get('UserPoolClientId')
        
        if user_pool_id:
            try:
                response = self.cognito.describe_user_pool(UserPoolId=user_pool_id)
                pool_status = response['UserPool']['Status']
                
                if pool_status == 'Enabled':
                    self._add_result("Cognito", "User Pool Status", True, "User pool is enabled")
                else:
                    self._add_result("Cognito", "User Pool Status", False, f"User pool status is {pool_status}")
                
            except Exception as e:
                self._add_result("Cognito", "User Pool Existence", False, str(e))
        else:
            self._add_result("Cognito", "User Pool Configuration", False, "User pool ID not found in outputs")
        
        if user_pool_client_id and user_pool_id:
            try:
                response = self.cognito.describe_user_pool_client(
                    UserPoolId=user_pool_id,
                    ClientId=user_pool_client_id
                )
                self._add_result("Cognito", "User Pool Client", True, "User pool client exists")
                
            except Exception as e:
                self._add_result("Cognito", "User Pool Client", False, str(e))
        else:
            self._add_result("Cognito", "User Pool Client Configuration", False, "User pool client ID not found in outputs")
    
    def _validate_api_gateway(self):
        """Validate API Gateway."""
        logger.info("🌐 Validating API Gateway...")
        
        api_url = self.stack_outputs.get('ApiGatewayUrl')
        if api_url:
            try:
                # Test health endpoint
                response = requests.get(f"{api_url}health", timeout=10)
                
                if response.status_code == 200:
                    health_data = response.json()
                    if health_data.get('status') == 'healthy':
                        self._add_result("API Gateway", "Health Endpoint", True, "Health endpoint returns healthy status")
                    else:
                        self._add_result("API Gateway", "Health Endpoint", False, f"Health endpoint returns status: {health_data.get('status')}")
                else:
                    self._add_result("API Gateway", "Health Endpoint", False, f"Health endpoint returned status code {response.status_code}")
                
                # Test CORS headers
                options_response = requests.options(f"{api_url}health", timeout=10)
                if 'Access-Control-Allow-Origin' in options_response.headers:
                    self._add_result("API Gateway", "CORS Configuration", True, "CORS headers are present")
                else:
                    self._add_result("API Gateway", "CORS Configuration", False, "CORS headers are missing")
                
            except Exception as e:
                self._add_result("API Gateway", "API Accessibility", False, str(e))
        else:
            self._add_result("API Gateway", "API Configuration", False, "API Gateway URL not found in outputs")
    
    def _validate_frontend(self):
        """Validate frontend deployment."""
        logger.info("🎨 Validating frontend...")
        
        cloudfront_url = self.stack_outputs.get('CloudFrontUrl')
        if cloudfront_url:
            try:
                # Test CloudFront distribution
                response = requests.get(cloudfront_url, timeout=30)
                
                if response.status_code == 200:
                    if 'SnapStudy' in response.text or 'react' in response.text.lower():
                        self._add_result("Frontend", "CloudFront Distribution", True, "Frontend is accessible via CloudFront")
                    else:
                        self._add_result("Frontend", "CloudFront Distribution", False, "CloudFront returns unexpected content")
                else:
                    self._add_result("Frontend", "CloudFront Distribution", False, f"CloudFront returned status code {response.status_code}")
                
                # Check security headers
                security_headers = [
                    'X-Content-Type-Options',
                    'X-Frame-Options',
                    'Strict-Transport-Security'
                ]
                
                for header in security_headers:
                    if header in response.headers:
                        self._add_result("Frontend", f"Security Header {header}", True, f"Header is present: {response.headers[header]}")
                    else:
                        self._add_result("Frontend", f"Security Header {header}", False, "Header is missing")
                
            except Exception as e:
                self._add_result("Frontend", "Frontend Accessibility", False, str(e))
        else:
            self._add_result("Frontend", "Frontend Configuration", False, "CloudFront URL not found in outputs")
    
    def _validate_end_to_end(self):
        """Validate end-to-end functionality."""
        logger.info("🔄 Validating end-to-end functionality...")
        
        api_url = self.stack_outputs.get('ApiGatewayUrl')
        if not api_url:
            self._add_result("End-to-End", "API Availability", False, "API URL not available")
            return
        
        try:
            # Test API root endpoint
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('message') == 'SnapStudy API':
                    self._add_result("End-to-End", "API Root Endpoint", True, "API root endpoint responds correctly")
                else:
                    self._add_result("End-to-End", "API Root Endpoint", False, "API root endpoint returns unexpected response")
            else:
                self._add_result("End-to-End", "API Root Endpoint", False, f"API root endpoint returned status {response.status_code}")
            
            # Test authentication endpoints (should return 401 or proper error)
            auth_response = requests.post(f"{api_url}api/v1/auth/login", 
                                        json={"email": "test@example.com", "password": "invalid"}, 
                                        timeout=10)
            if auth_response.status_code in [400, 401, 422]:
                self._add_result("End-to-End", "Authentication Endpoint", True, "Authentication endpoint is accessible")
            else:
                self._add_result("End-to-End", "Authentication Endpoint", False, f"Authentication endpoint returned unexpected status {auth_response.status_code}")
            
        except Exception as e:
            self._add_result("End-to-End", "End-to-End Test", False, str(e))
    
    def _add_result(self, category: str, test: str, passed: bool, message: str):
        """Add validation result."""
        self.validation_results.append({
            'category': category,
            'test': test,
            'passed': passed,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        status = "✅" if passed else "❌"
        logger.info(f"{status} {category} - {test}: {message}")
    
    def _generate_report(self):
        """Generate validation report."""
        logger.info("📊 Generating validation report...")
        
        # Count results
        total_tests = len(self.validation_results)
        passed_tests = len([r for r in self.validation_results if r['passed']])
        failed_tests = total_tests - passed_tests
        
        # Group by category
        categories = {}
        for result in self.validation_results:
            category = result['category']
            if category not in categories:
                categories[category] = {'passed': 0, 'failed': 0, 'tests': []}
            
            if result['passed']:
                categories[category]['passed'] += 1
            else:
                categories[category]['failed'] += 1
            
            categories[category]['tests'].append(result)
        
        # Generate report
        report = {
            'validation_summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': f"{(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%",
                'validation_date': datetime.now().isoformat()
            },
            'stack_outputs': self.stack_outputs,
            'categories': categories,
            'detailed_results': self.validation_results
        }
        
        # Save report to file
        with open('deployment-validation-report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Validation report saved to deployment-validation-report.json")
        
        # Print summary
        print("\n" + "="*60)
        print("🔍 SNAPSTUDY DEPLOYMENT VALIDATION REPORT")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print("\nCategory Breakdown:")
        
        for category, stats in categories.items():
            total_cat = stats['passed'] + stats['failed']
            success_rate = (stats['passed']/total_cat)*100 if total_cat > 0 else 0
            status = "✅" if stats['failed'] == 0 else "❌"
            print(f"{status} {category}: {stats['passed']}/{total_cat} ({success_rate:.1f}%)")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.validation_results:
                if not result['passed']:
                    print(f"   • {result['category']} - {result['test']}: {result['message']}")
        
        print("="*60)

def main():
    """Main validation function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate SnapStudy deployment')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--stack-name', default='SnapStudy-production', help='CloudFormation stack name')
    
    args = parser.parse_args()
    
    validator = DeploymentValidator(region=args.region, stack_name=args.stack_name)
    success = validator.validate_deployment()
    
    if success:
        print("\n🎉 All validation tests passed! SnapStudy is ready for use.")
        sys.exit(0)
    else:
        print("\n❌ Some validation tests failed. Please check the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()