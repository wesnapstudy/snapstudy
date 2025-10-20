"""
Lambda deployment script for SnapStudy backend.

This script packages and deploys Lambda functions to AWS with proper configuration.
"""

import os
import sys
import json
import zipfile
import shutil
import subprocess
import boto3
from typing import Dict, List, Any
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LambdaDeployer:
    """Handles Lambda function deployment."""
    
    def __init__(self, aws_region: str = 'us-east-1', environment: str = 'production'):
        self.aws_region = aws_region
        self.environment = environment
        self.lambda_client = boto3.client('lambda', region_name=aws_region)
        self.iam_client = boto3.client('iam', region_name=aws_region)
        self.s3_client = boto3.client('s3', region_name=aws_region)
        
        # Deployment configuration
        self.deployment_bucket = f"snapstudy-lambda-deployments-{aws_region}"
        self.function_configs = self._get_function_configs()
    
    def _get_function_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get Lambda function configurations."""
        return {
            'snapstudy-api': {
                'handler': 'lambda_functions.main_handler.lambda_handler',
                'runtime': 'python3.11',
                'timeout': 30,
                'memory_size': 1024,
                'description': 'Main API handler for SnapStudy',
                'environment_variables': {
                    'ENVIRONMENT': self.environment,
                    'AWS_REGION': self.aws_region,
                    'PYTHONPATH': '/var/task/src'
                },
                'layers': [],
                'vpc_config': None,
                'dead_letter_config': None,
                'tracing_config': {'Mode': 'Active'},
                'tags': {
                    'Project': 'SnapStudy',
                    'Environment': self.environment,
                    'Component': 'API'
                }
            },
            'snapstudy-content-processor': {
                'handler': 'lambda_functions.content_processor.lambda_handler',
                'runtime': 'python3.11',
                'timeout': 900,  # 15 minutes
                'memory_size': 2048,
                'description': 'Content processing for SnapStudy',
                'environment_variables': {
                    'ENVIRONMENT': self.environment,
                    'AWS_REGION': self.aws_region,
                    'PYTHONPATH': '/var/task/src'
                },
                'layers': [],
                'vpc_config': None,
                'dead_letter_config': None,
                'tracing_config': {'Mode': 'Active'},
                'tags': {
                    'Project': 'SnapStudy',
                    'Environment': self.environment,
                    'Component': 'ContentProcessor'
                }
            },
            'snapstudy-multimedia-processor': {
                'handler': 'lambda_functions.multimedia_processor.lambda_handler',
                'runtime': 'python3.11',
                'timeout': 900,  # 15 minutes
                'memory_size': 3008,  # Maximum for multimedia processing
                'description': 'Multimedia generation for SnapStudy',
                'environment_variables': {
                    'ENVIRONMENT': self.environment,
                    'AWS_REGION': self.aws_region,
                    'PYTHONPATH': '/var/task/src'
                },
                'layers': [],
                'vpc_config': None,
                'dead_letter_config': None,
                'tracing_config': {'Mode': 'Active'},
                'tags': {
                    'Project': 'SnapStudy',
                    'Environment': self.environment,
                    'Component': 'MultimediaProcessor'
                }
            }
        }
    
    def create_deployment_package(self, function_name: str) -> str:
        """Create deployment package for Lambda function."""
        logger.info(f"Creating deployment package for {function_name}")
        
        # Create temporary directory
        temp_dir = f"/tmp/lambda_package_{function_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # Copy source code
            src_dir = os.path.join(os.path.dirname(__file__), 'src')
            lambda_dir = os.path.join(os.path.dirname(__file__), 'lambda_functions')
            
            # Copy src directory
            if os.path.exists(src_dir):
                shutil.copytree(src_dir, os.path.join(temp_dir, 'src'))
            
            # Copy lambda_functions directory
            if os.path.exists(lambda_dir):
                shutil.copytree(lambda_dir, os.path.join(temp_dir, 'lambda_functions'))
            
            # Install dependencies
            requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
            if os.path.exists(requirements_file):
                logger.info("Installing dependencies...")
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install',
                    '-r', requirements_file,
                    '-t', temp_dir,
                    '--no-deps'  # Avoid conflicts with Lambda runtime
                ], check=True)
            
            # Create ZIP file
            zip_path = f"/tmp/{function_name}_deployment.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arc_name)
            
            logger.info(f"Deployment package created: {zip_path}")
            return zip_path
            
        finally:
            # Cleanup temporary directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    def upload_to_s3(self, zip_path: str, function_name: str) -> str:
        """Upload deployment package to S3."""
        logger.info(f"Uploading {function_name} to S3")
        
        # Ensure deployment bucket exists
        try:
            self.s3_client.head_bucket(Bucket=self.deployment_bucket)
        except:
            logger.info(f"Creating deployment bucket: {self.deployment_bucket}")
            if self.aws_region == 'us-east-1':
                # us-east-1 doesn't need LocationConstraint
                self.s3_client.create_bucket(Bucket=self.deployment_bucket)
            else:
                # Other regions need LocationConstraint
                self.s3_client.create_bucket(
                    Bucket=self.deployment_bucket,
                    CreateBucketConfiguration={'LocationConstraint': self.aws_region}
                )
        
        # Upload ZIP file
        s3_key = f"lambda-deployments/{function_name}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        with open(zip_path, 'rb') as f:
            self.s3_client.upload_fileobj(f, self.deployment_bucket, s3_key)
        
        logger.info(f"Uploaded to s3://{self.deployment_bucket}/{s3_key}")
        return s3_key
    
    def create_or_update_function(self, function_name: str, s3_key: str) -> Dict[str, Any]:
        """Create or update Lambda function."""
        config = self.function_configs[function_name]
        
        try:
            # Check if function exists
            self.lambda_client.get_function(FunctionName=function_name)
            function_exists = True
        except self.lambda_client.exceptions.ResourceNotFoundException:
            function_exists = False
        
        if function_exists:
            logger.info(f"Updating existing function: {function_name}")
            
            # Update function code
            self.lambda_client.update_function_code(
                FunctionName=function_name,
                S3Bucket=self.deployment_bucket,
                S3Key=s3_key
            )
            
            # Update function configuration
            response = self.lambda_client.update_function_configuration(
                FunctionName=function_name,
                Runtime=config['runtime'],
                Role=self._get_execution_role_arn(function_name),
                Handler=config['handler'],
                Description=config['description'],
                Timeout=config['timeout'],
                MemorySize=config['memory_size'],
                Environment={'Variables': config['environment_variables']},
                TracingConfig=config['tracing_config']
            )
            
        else:
            logger.info(f"Creating new function: {function_name}")
            
            response = self.lambda_client.create_function(
                FunctionName=function_name,
                Runtime=config['runtime'],
                Role=self._get_execution_role_arn(function_name),
                Handler=config['handler'],
                Code={
                    'S3Bucket': self.deployment_bucket,
                    'S3Key': s3_key
                },
                Description=config['description'],
                Timeout=config['timeout'],
                MemorySize=config['memory_size'],
                Environment={'Variables': config['environment_variables']},
                TracingConfig=config['tracing_config'],
                Tags=config['tags']
            )
        
        # Wait for function to be ready
        waiter = self.lambda_client.get_waiter('function_updated')
        waiter.wait(FunctionName=function_name)
        
        logger.info(f"Function {function_name} deployed successfully")
        return response
    
    def _get_execution_role_arn(self, function_name: str) -> str:
        """Get or create execution role for Lambda function."""
        role_name = f"{function_name}-execution-role"
        
        try:
            # Check if role exists
            response = self.iam_client.get_role(RoleName=role_name)
            return response['Role']['Arn']
        except self.iam_client.exceptions.NoSuchEntityException:
            pass
        
        # Create execution role
        logger.info(f"Creating execution role: {role_name}")
        
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        response = self.iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description=f"Execution role for {function_name} Lambda function"
        )
        
        role_arn = response['Role']['Arn']
        
        # Attach basic execution policy
        self.iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        
        # Attach additional policies based on function type
        if 'api' in function_name:
            policies = [
                'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess',
                'arn:aws:iam::aws:policy/AmazonS3FullAccess',
                'arn:aws:iam::aws:policy/AmazonBedrockFullAccess'
            ]
        elif 'content-processor' in function_name:
            policies = [
                'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess',
                'arn:aws:iam::aws:policy/AmazonS3FullAccess',
                'arn:aws:iam::aws:policy/AmazonTextractFullAccess',
                'arn:aws:iam::aws:policy/AmazonTranscribeFullAccess',
                'arn:aws:iam::aws:policy/AmazonBedrockFullAccess'
            ]
        elif 'multimedia-processor' in function_name:
            policies = [
                'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess',
                'arn:aws:iam::aws:policy/AmazonS3FullAccess',
                'arn:aws:iam::aws:policy/AmazonPollyFullAccess',
                'arn:aws:iam::aws:policy/AmazonBedrockFullAccess'
            ]
        else:
            policies = []
        
        for policy_arn in policies:
            self.iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
        
        # Wait for role to be ready
        import time
        time.sleep(10)  # IAM eventual consistency
        
        return role_arn
    
    def deploy_all_functions(self) -> Dict[str, Dict[str, Any]]:
        """Deploy all Lambda functions."""
        logger.info("Starting deployment of all Lambda functions")
        
        results = {}
        
        for function_name in self.function_configs.keys():
            try:
                logger.info(f"Deploying {function_name}...")
                
                # Create deployment package
                zip_path = self.create_deployment_package(function_name)
                
                # Upload to S3
                s3_key = self.upload_to_s3(zip_path, function_name)
                
                # Deploy function
                response = self.create_or_update_function(function_name, s3_key)
                
                results[function_name] = {
                    'status': 'success',
                    'function_arn': response['FunctionArn'],
                    'version': response['Version']
                }
                
                # Cleanup ZIP file
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                
            except Exception as e:
                logger.error(f"Failed to deploy {function_name}: {str(e)}")
                results[function_name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        logger.info("Lambda deployment completed")
        return results
    
    def create_api_gateway_integration(self, function_arn: str) -> str:
        """Create API Gateway integration for main API function."""
        # This would typically be handled by CDK/CloudFormation
        # For now, return a placeholder
        return f"https://api.snapstudy.com"

def main():
    """Main deployment function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy SnapStudy Lambda functions')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--environment', default='production', help='Environment')
    parser.add_argument('--function', help='Specific function to deploy')
    
    args = parser.parse_args()
    
    deployer = LambdaDeployer(aws_region=args.region, environment=args.environment)
    
    if args.function:
        if args.function in deployer.function_configs:
            # Deploy specific function
            zip_path = deployer.create_deployment_package(args.function)
            s3_key = deployer.upload_to_s3(zip_path, args.function)
            result = deployer.create_or_update_function(args.function, s3_key)
            print(f"Deployed {args.function}: {result['FunctionArn']}")
        else:
            print(f"Unknown function: {args.function}")
            print(f"Available functions: {list(deployer.function_configs.keys())}")
    else:
        # Deploy all functions
        results = deployer.deploy_all_functions()
        
        print("\nDeployment Results:")
        print("=" * 50)
        for function_name, result in results.items():
            if result['status'] == 'success':
                print(f"✅ {function_name}: {result['function_arn']}")
            else:
                print(f"❌ {function_name}: {result['error']}")

if __name__ == "__main__":
    main()