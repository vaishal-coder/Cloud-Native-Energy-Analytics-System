"""Script to upload data to S3 and trigger pipeline"""
import sys
import os
import json
import boto3
import time

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
        print("Error: deployment_info.json not found. Please run deploy.py first.")
        sys.exit(1)
    
    with open(deployment_file, 'r') as f:
        return json.load(f)

def upload_to_s3(file_path):
    """Upload data file to S3 raw folder"""
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    deployment_info = load_deployment_info()
    bucket_name = deployment_info['bucket_name']
    
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    
    # Generate S3 key with timestamp
    filename = os.path.basename(file_path)
    s3_key = f"raw/{filename.replace('.csv', '')}_{int(time.time())}.csv"
    
    print(f"Uploading {file_path} to s3://{bucket_name}/{s3_key}")
    
    with open(file_path, 'rb') as f:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=f
        )
    
    print(f"✓ Upload successful!")
    print(f"✓ Lambda function will be triggered automatically")
    print()
    print("Monitor execution:")
    print(f"  aws logs tail /aws/lambda/{deployment_info['lambda_function_name']} --follow")
    print()
    print("Check results:")
    print(f"  aws s3 ls s3://{bucket_name}/reports/")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python upload_data.py <path_to_csv_file>")
        print()
        print("Example:")
        print("  python upload_data.py data/output/energy_data.csv")
        sys.exit(1)
    
    file_path = sys.argv[1]
    upload_to_s3(file_path)
