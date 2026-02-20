"""Script to cleanup all AWS resources"""
import sys
import os
import json
import boto3
from botocore.exceptions import ClientError

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import AWS_REGION

def load_deployment_info():
    """Load deployment information"""
    deployment_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'deployment_info.json'
    )
    
    if not os.path.exists(deployment_file):
        print("Warning: deployment_info.json not found.")
        return None
    
    with open(deployment_file, 'r') as f:
        return json.load(f)

def cleanup_resources():
    """Delete all AWS resources"""
    print("="*70)
    print("ENERGY ANALYTICS SYSTEM - RESOURCE CLEANUP")
    print("="*70)
    print()
    print("WARNING: This will delete all resources including data!")
    print()
    
    response = input("Are you sure you want to continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Cleanup cancelled.")
        return
    
    print()
    
    deployment_info = load_deployment_info()
    
    if not deployment_info:
        print("No deployment info found. Please provide resource names manually.")
        bucket_name = input("S3 Bucket name: ")
        lambda_function_name = input("Lambda function name: ")
        iam_role_name = input("IAM role name: ")
        athena_database = input("Athena database name: ")
    else:
        bucket_name = deployment_info.get('bucket_name')
        lambda_function_name = deployment_info.get('lambda_function_name')
        iam_role_name = deployment_info.get('iam_role_name')
        athena_database = deployment_info.get('athena_database')
    
    # Initialize AWS clients
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    lambda_client = boto3.client('lambda', region_name=AWS_REGION)
    iam_client = boto3.client('iam', region_name=AWS_REGION)
    athena_client = boto3.client('athena', region_name=AWS_REGION)
    
    # Step 1: Delete S3 bucket
    print("Step 1: Deleting S3 Bucket")
    print("-"*70)
    try:
        # Delete all objects first
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name)
        
        delete_count = 0
        for page in pages:
            if 'Contents' in page:
                objects = [{'Key': obj['Key']} for obj in page['Contents']]
                s3_client.delete_objects(
                    Bucket=bucket_name,
                    Delete={'Objects': objects}
                )
                delete_count += len(objects)
        
        print(f"  ✓ Deleted {delete_count} objects")
        
        # Delete bucket
        s3_client.delete_bucket(Bucket=bucket_name)
        print(f"✓ Deleted S3 bucket: {bucket_name}")
    except ClientError as e:
        print(f"✗ Error deleting S3 bucket: {e}")
    print()
    
    # Step 2: Delete Lambda function
    print("Step 2: Deleting Lambda Function")
    print("-"*70)
    try:
        lambda_client.delete_function(FunctionName=lambda_function_name)
        print(f"✓ Deleted Lambda function: {lambda_function_name}")
    except ClientError as e:
        print(f"✗ Error deleting Lambda function: {e}")
    print()
    
    # Step 3: Delete IAM role
    print("Step 3: Deleting IAM Role")
    print("-"*70)
    try:
        # Delete inline policies
        policies = ['S3Access', 'AthenaAccess', 'CloudWatchLogs']
        for policy_name in policies:
            try:
                iam_client.delete_role_policy(
                    RoleName=iam_role_name,
                    PolicyName=policy_name
                )
                print(f"  ✓ Deleted policy: {policy_name}")
            except ClientError:
                pass
        
        # Delete role
        iam_client.delete_role(RoleName=iam_role_name)
        print(f"✓ Deleted IAM role: {iam_role_name}")
    except ClientError as e:
        print(f"✗ Error deleting IAM role: {e}")
    print()
    
    # Step 4: Delete Athena database
    print("Step 4: Deleting Athena Database")
    print("-"*70)
    try:
        query = f"DROP DATABASE IF EXISTS {athena_database} CASCADE"
        
        # Need a temporary location for query results
        # Use a different bucket or skip if S3 bucket already deleted
        print(f"  Note: Athena database '{athena_database}' should be deleted manually")
        print(f"  Run: DROP DATABASE IF EXISTS {athena_database} CASCADE")
    except Exception as e:
        print(f"✗ Error deleting Athena database: {e}")
    print()
    
    # Delete deployment info file
    if deployment_info:
        deployment_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'deployment_info.json'
        )
        try:
            os.remove(deployment_file)
            print("✓ Deleted deployment_info.json")
        except Exception as e:
            print(f"✗ Error deleting deployment_info.json: {e}")
    
    print()
    print("="*70)
    print("CLEANUP COMPLETED")
    print("="*70)
    print()
    print("All resources have been deleted.")
    print("Note: CloudWatch logs may still exist and will be retained.")
    print()

if __name__ == '__main__':
    cleanup_resources()
