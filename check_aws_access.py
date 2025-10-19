"""
Quick AWS access verification script.
Run this after switching to hackathon-user-01 to verify permissions.
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import json


def check_aws_identity():
    """Check current AWS identity."""
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        print("✅ AWS Identity Check:")
        print(f"   User ARN: {identity.get('Arn')}")
        print(f"   Account: {identity.get('Account')}")
        print(f"   User ID: {identity.get('UserId')}")
        
        if 'hackathon-user-01' in identity.get('Arn', ''):
            print("🎯 SUCCESS: Using hackathon-user-01!")
            return True
        else:
            print("⚠️  WARNING: Not using hackathon-user-01")
            return False
            
    except NoCredentialsError:
        print("❌ ERROR: No AWS credentials found")
        print("   Please configure AWS credentials first")
        return False
    except ClientError as e:
        print(f"❌ ERROR: AWS access denied - {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: Unexpected error - {e}")
        return False


def check_dynamodb_access():
    """Check DynamoDB access permissions."""
    try:
        dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        
        # Try to list tables
        response = dynamodb.list_tables()
        tables = response.get('TableNames', [])
        
        print("\n✅ DynamoDB Access Check:")
        print(f"   Can list tables: YES")
        print(f"   Available tables: {len(tables)}")
        
        # Check for SnapStudy tables
        snapstudy_tables = [t for t in tables if 'SnapStudy' in t]
        if snapstudy_tables:
            print(f"   SnapStudy tables found: {snapstudy_tables}")
        else:
            print("   ⚠️  No SnapStudy tables found")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"\n❌ DynamoDB Access Error: {error_code}")
        print(f"   Message: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"\n❌ DynamoDB Unexpected Error: {e}")
        return False


def check_bedrock_access():
    """Check Bedrock access permissions."""
    try:
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Try a simple model invocation (this will fail if no access)
        # We'll catch the specific error to determine if it's permissions or model issue
        test_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        try:
            response = bedrock.invoke_model(
                modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
                body=json.dumps(test_body),
                contentType='application/json'
            )
            print("\n✅ Bedrock Access Check:")
            print("   Can invoke models: YES")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDeniedException':
                print(f"\n❌ Bedrock Access Error: {error_code}")
                print("   No permission to invoke Bedrock models")
                return False
            elif error_code in ['ValidationException', 'ModelNotReadyException']:
                print("\n✅ Bedrock Access Check:")
                print("   Can access Bedrock service: YES")
                print(f"   Model issue (not permissions): {error_code}")
                return True
            else:
                print(f"\n❌ Bedrock Error: {error_code}")
                return False
                
    except Exception as e:
        print(f"\n❌ Bedrock Unexpected Error: {e}")
        return False


def main():
    """Run all AWS access checks."""
    print("🔍 AWS Access Verification for SnapStudy")
    print("="*50)
    
    # Check identity
    identity_ok = check_aws_identity()
    
    # Check DynamoDB
    dynamodb_ok = check_dynamodb_access()
    
    # Check Bedrock
    bedrock_ok = check_bedrock_access()
    
    print("\n" + "="*50)
    print("📋 SUMMARY:")
    print(f"   AWS Identity: {'✅' if identity_ok else '❌'}")
    print(f"   DynamoDB Access: {'✅' if dynamodb_ok else '❌'}")
    print(f"   Bedrock Access: {'✅' if bedrock_ok else '❌'}")
    
    if all([identity_ok, dynamodb_ok, bedrock_ok]):
        print("\n🎉 ALL CHECKS PASSED!")
        print("You can now run the quiz module tests:")
        print("   python backend/test_quiz_module.py")
    else:
        print("\n⚠️  SOME CHECKS FAILED")
        print("Please resolve the access issues before running tests.")
        
        if not identity_ok:
            print("\n🔧 To fix identity issues:")
            print("   1. Update switch_aws_user.ps1 with hackathon-user-01 credentials")
            print("   2. Run: ./switch_aws_user.ps1")
            
        if not dynamodb_ok:
            print("\n🔧 To fix DynamoDB issues:")
            print("   1. Ensure hackathon-user-01 has DynamoDB permissions")
            print("   2. Check if SnapStudy tables exist in us-east-1")
            
        if not bedrock_ok:
            print("\n🔧 To fix Bedrock issues:")
            print("   1. Ensure hackathon-user-01 has Bedrock permissions")
            print("   2. Check if Claude model is available in us-east-1")


if __name__ == "__main__":
    main()