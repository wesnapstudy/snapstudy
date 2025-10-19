#!/usr/bin/env python3
"""
Configuration fix script for SnapStudy AI services.
This script helps resolve common configuration issues.
"""

import boto3
import os
import sys

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import settings


def check_aws_account():
    """Check current AWS account and compare with expected."""
    print("🔍 AWS Account Check")
    print("=" * 30)
    
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        current_account = identity.get('Account')
        current_user = identity.get('Arn')
        
        print(f"Current AWS Account: {current_account}")
        print(f"Current AWS User: {current_user}")
        print(f"Expected Account (from infrastructure): 054037102331")
        print()
        
        if current_account != "054037102331":
            print("⚠️  ACCOUNT MISMATCH DETECTED!")
            print("Your current AWS credentials are for a different account than where the infrastructure was deployed.")
            print()
            print("Solutions:")
            print("1. Switch to the correct AWS profile:")
            print("   export AWS_PROFILE=hackathon-user-01")
            print("   # or in PowerShell:")
            print("   $env:AWS_PROFILE='hackathon-user-01'")
            print()
            print("2. Or use the correct AWS credentials for account 054037102331")
            print()
            return False
        else:
            print("✅ AWS account matches infrastructure deployment")
            return True
            
    except Exception as e:
        print(f"❌ Failed to check AWS account: {e}")
        return False


def check_s3_bucket():
    """Check if S3 bucket exists and is accessible."""
    print("📁 S3 Bucket Check")
    print("=" * 30)
    
    try:
        s3 = boto3.client('s3')
        bucket_name = settings.content_bucket
        
        print(f"Checking bucket: {bucket_name}")
        
        # Try to get bucket location
        response = s3.get_bucket_location(Bucket=bucket_name)
        location = response.get('LocationConstraint') or 'us-east-1'
        
        print(f"✅ Bucket exists in region: {location}")
        
        # Try to list objects (just to test permissions)
        s3.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
        print("✅ Bucket is accessible")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ S3 bucket check failed: {error_msg}")
        
        if 'NoSuchBucket' in error_msg:
            print("💡 The S3 bucket doesn't exist in this account")
            print("   This confirms the account mismatch issue")
        elif 'AccessDenied' in error_msg:
            print("💡 S3 bucket exists but you don't have access")
            print("   Check your IAM permissions")
        
        return False


def check_bedrock_access():
    """Check Bedrock access and model availability."""
    print("🤖 Bedrock Access Check")
    print("=" * 30)
    
    try:
        bedrock = boto3.client('bedrock', region_name=settings.aws_region)
        
        print(f"Checking Bedrock in region: {settings.aws_region}")
        
        # Try to list foundation models
        models = bedrock.list_foundation_models()
        print(f"✅ Found {len(models.get('modelSummaries', []))} available models")
        
        # Check if our specific model is available
        target_model = settings.bedrock_model_id
        available_models = [m['modelId'] for m in models.get('modelSummaries', [])]
        
        if target_model in available_models:
            print(f"✅ Target model available: {target_model}")
        else:
            print(f"⚠️  Target model not found: {target_model}")
            print("Available Claude models:")
            claude_models = [m for m in available_models if 'claude' in m.lower()]
            for model in claude_models[:5]:  # Show first 5
                print(f"   - {model}")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Bedrock check failed: {error_msg}")
        
        if 'AccessDeniedException' in error_msg:
            print("💡 No permission to access Bedrock")
            if 'explicit deny' in error_msg:
                print("   Your IAM policy has an EXPLICIT DENY for Bedrock")
                print("   This must be removed by your AWS administrator")
            else:
                print("   Add bedrock:ListFoundationModels and bedrock:InvokeModel permissions")
        elif 'not available' in error_msg.lower():
            print("💡 Bedrock not available in this region")
            print("   Try us-east-1, us-west-2, or eu-west-1")
        
        return False


def suggest_fixes():
    """Provide specific fix suggestions based on the issues found."""
    print("\n🛠️  RECOMMENDED FIXES")
    print("=" * 50)
    
    print("1. **Fix Account Mismatch:**")
    print("   Set the correct AWS profile:")
    print("   ```")
    print("   export AWS_PROFILE=hackathon-user-01")
    print("   # or in PowerShell:")
    print("   $env:AWS_PROFILE='hackathon-user-01'")
    print("   ```")
    print()
    
    print("2. **Fix Bedrock Permissions:**")
    print("   Ask your AWS administrator to:")
    print("   - Remove the explicit deny policy for Bedrock")
    print("   - Add these permissions to your IAM user:")
    print("     * bedrock:ListFoundationModels")
    print("     * bedrock:InvokeModel")
    print("     * bedrock:GetFoundationModel")
    print()
    
    print("3. **Alternative: Use Mock Mode for Testing:**")
    print("   If you can't get Bedrock access immediately, I can create")
    print("   a mock version that simulates AI responses for testing.")
    print()
    
    print("4. **Verify Infrastructure Deployment:**")
    print("   Make sure the infrastructure was deployed to the correct account")
    print("   and that you're using the right AWS credentials.")


def main():
    """Run configuration diagnostics."""
    print("🔧 SnapStudy Configuration Diagnostics")
    print("=" * 50)
    print()
    
    # Run checks
    account_ok = check_aws_account()
    print()
    
    s3_ok = check_s3_bucket()
    print()
    
    bedrock_ok = check_bedrock_access()
    print()
    
    # Summary
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 30)
    print(f"AWS Account: {'✅ OK' if account_ok else '❌ ISSUE'}")
    print(f"S3 Bucket: {'✅ OK' if s3_ok else '❌ ISSUE'}")
    print(f"Bedrock Access: {'✅ OK' if bedrock_ok else '❌ ISSUE'}")
    
    if not (account_ok and s3_ok and bedrock_ok):
        suggest_fixes()
    else:
        print("\n🎉 All checks passed! Your configuration looks good.")


if __name__ == "__main__":
    main()