"""Script to check pipeline results in S3"""
import sys
import os
import json
import boto3

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

def check_results():
    """Check pipeline results in S3"""
    deployment_info = load_deployment_info()
    bucket_name = deployment_info['bucket_name']
    
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    
    print("="*70)
    print("PIPELINE RESULTS CHECK")
    print("="*70)
    print(f"Bucket: {bucket_name}")
    print()
    
    folders = ['raw/', 'processed/', 'forecast/', 'anomalies/', 'reports/']
    
    for folder in folders:
        print(f"{folder}")
        print("-"*70)
        
        try:
            response = s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=folder,
                MaxKeys=100
            )
            
            if 'Contents' in response:
                files = [obj for obj in response['Contents'] if not obj['Key'].endswith('/')]
                
                if files:
                    print(f"Found {len(files)} file(s):")
                    for obj in sorted(files, key=lambda x: x['LastModified'], reverse=True)[:5]:
                        size_kb = obj['Size'] / 1024
                        print(f"  • {obj['Key']}")
                        print(f"    Size: {size_kb:.2f} KB | Modified: {obj['LastModified']}")
                else:
                    print("  No files found")
            else:
                print("  No files found")
        except Exception as e:
            print(f"  Error: {str(e)}")
        
        print()
    
    # Download and display latest report
    print("LATEST REPORT")
    print("-"*70)
    
    try:
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix='reports/',
            MaxKeys=100
        )
        
        if 'Contents' in response:
            files = [obj for obj in response['Contents'] if not obj['Key'].endswith('/')]
            
            if files:
                latest = sorted(files, key=lambda x: x['LastModified'], reverse=True)[0]
                print(f"File: {latest['Key']}")
                print()
                
                response = s3_client.get_object(Bucket=bucket_name, Key=latest['Key'])
                content = response['Body'].read().decode('utf-8')
                print(content)
            else:
                print("No reports found yet")
        else:
            print("No reports found yet")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print()
    print("="*70)

if __name__ == '__main__':
    check_results()
