"""Test script for energy analytics pipeline"""
import sys
import os
import json
import time
import boto3

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import *

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

def test_pipeline():
    """Test the complete energy analytics pipeline"""
    print("="*70)
    print("ENERGY ANALYTICS PIPELINE - TEST EXECUTION")
    print("="*70)
    print()
    
    # Load deployment info
    deployment_info = load_deployment_info()
    bucket_name = deployment_info['bucket_name']
    lambda_function_name = deployment_info['lambda_function_name']
    
    print(f"Testing bucket: {bucket_name}")
    print(f"Testing Lambda: {lambda_function_name}")
    print()
    
    # Initialize AWS clients
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    lambda_client = boto3.client('lambda', region_name=AWS_REGION)
    
    # Step 1: Generate test data
    print("Step 1: Generating test data")
    print("-"*70)
    from data.generate_data import generate_energy_data, save_to_csv
    
    df = generate_energy_data()
    test_file = save_to_csv(df, 'test_energy_data.csv')
    print()
    
    # Step 2: Upload to S3
    print("Step 2: Uploading test data to S3")
    print("-"*70)
    s3_key = f"raw/test_energy_data_{int(time.time())}.csv"
    
    with open(test_file, 'rb') as f:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=f
        )
    
    print(f"✓ Uploaded: s3://{bucket_name}/{s3_key}")
    print()
    
    # Step 3: Wait for Lambda execution
    print("Step 3: Waiting for Lambda execution (30 seconds)")
    print("-"*70)
    time.sleep(30)
    print("✓ Wait completed")
    print()
    
    # Step 4: Check results
    print("Step 4: Verifying pipeline outputs")
    print("-"*70)
    
    folders_to_check = ['processed/', 'forecast/', 'anomalies/', 'reports/']
    results = {}
    
    for folder in folders_to_check:
        try:
            response = s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=folder,
                MaxKeys=10
            )
            
            if 'Contents' in response:
                files = [obj['Key'] for obj in response['Contents'] if not obj['Key'].endswith('/')]
                results[folder] = files
                print(f"✓ {folder}: {len(files)} file(s) found")
                for file in files[-3:]:  # Show last 3 files
                    print(f"    - {file}")
            else:
                results[folder] = []
                print(f"✗ {folder}: No files found")
        except Exception as e:
            print(f"✗ {folder}: Error - {str(e)}")
            results[folder] = []
    
    print()
    
    # Step 5: Download and display report
    if results.get('reports/'):
        print("Step 5: Displaying Generated Report")
        print("-"*70)
        
        latest_report = sorted(results['reports/'])[-1]
        
        try:
            response = s3_client.get_object(Bucket=bucket_name, Key=latest_report)
            report_content = response['Body'].read().decode('utf-8')
            
            print(report_content)
            print()
        except Exception as e:
            print(f"Error reading report: {str(e)}")
            print()
    
    # Summary
    print("="*70)
    print("TEST EXECUTION SUMMARY")
    print("="*70)
    
    total_outputs = sum(len(files) for files in results.values())
    
    if total_outputs >= 4:  # At least one file in each folder
        print("✓ Pipeline test PASSED")
        print(f"  Total output files: {total_outputs}")
    else:
        print("✗ Pipeline test INCOMPLETE")
        print(f"  Total output files: {total_outputs}")
        print("  Some outputs may be missing. Check Lambda logs for errors.")
    
    print()
    print("To view Lambda logs:")
    print(f"  aws logs tail /aws/lambda/{lambda_function_name} --follow")
    print()
    print("="*70)

if __name__ == '__main__':
    test_pipeline()
