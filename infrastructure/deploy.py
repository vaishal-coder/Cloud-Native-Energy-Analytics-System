"""Main deployment script for Energy Analytics System"""
import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.aws_setup import AWSInfrastructure
from config.config import *

def main():
    """Deploy complete energy analytics system"""
    print("="*70)
    print("ENERGY ANALYTICS SYSTEM - AUTOMATED DEPLOYMENT")
    print("="*70)
    print()
    
    try:
        # Initialize AWS infrastructure manager
        aws = AWSInfrastructure()
        
        print("Step 1: Creating S3 Bucket and Folder Structure")
        print("-"*70)
        bucket_name = aws.create_s3_bucket()
        print()
        
        print("Step 2: Creating IAM Role and Policies")
        print("-"*70)
        role_arn = aws.create_iam_role()
        print(f"Role ARN: {role_arn}")
        print()
        
        # Wait for IAM role propagation
        print("Waiting for IAM role propagation (10 seconds)...")
        time.sleep(10)
        
        print("Step 3: Creating Lambda Function")
        print("-"*70)
        lambda_code_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'lambda',
            'lambda_function.py'
        )
        lambda_arn = aws.create_lambda_function(role_arn, lambda_code_path)
        print(f"Lambda ARN: {lambda_arn}")
        print()
        
        print("Step 4: Configuring S3 Trigger")
        print("-"*70)
        aws.configure_s3_trigger(lambda_arn)
        print()
        
        print("Step 5: Setting up Athena Database and Tables")
        print("-"*70)
        aws.setup_athena()
        print()
        
        # Print deployment summary
        print("="*70)
        print("DEPLOYMENT COMPLETED SUCCESSFULLY")
        print("="*70)
        print()
        print("RESOURCE DETAILS:")
        print("-"*70)
        print(f"S3 Bucket:        {bucket_name}")
        print(f"Lambda Function:  {LAMBDA_FUNCTION_NAME}")
        print(f"Lambda ARN:       {lambda_arn}")
        print(f"IAM Role:         {IAM_ROLE_NAME}")
        print(f"Athena Database:  {ATHENA_DATABASE}")
        print(f"AWS Region:       {AWS_REGION}")
        print()
        
        print("S3 FOLDER STRUCTURE:")
        print("-"*70)
        for folder_name, folder_path in S3_FOLDERS.items():
            print(f"  s3://{bucket_name}/{folder_path}")
        print()
        
        print("ATHENA TABLES:")
        print("-"*70)
        print(f"  {ATHENA_DATABASE}.raw_energy_data")
        print(f"  {ATHENA_DATABASE}.processed_energy_data")
        print(f"  {ATHENA_DATABASE}.forecast_data")
        print()
        
        print("NEXT STEPS:")
        print("-"*70)
        print("1. Generate synthetic data:")
        print("   python data/generate_data.py")
        print()
        print("2. Upload data to S3 to trigger pipeline:")
        print(f"   aws s3 cp data/output/energy_data.csv s3://{bucket_name}/raw/")
        print()
        print("3. Monitor Lambda execution:")
        print(f"   aws logs tail /aws/lambda/{LAMBDA_FUNCTION_NAME} --follow")
        print()
        print("4. Check results in S3:")
        print(f"   aws s3 ls s3://{bucket_name}/reports/")
        print()
        
        # Save deployment info
        deployment_info = {
            'bucket_name': bucket_name,
            'lambda_arn': lambda_arn,
            'lambda_function_name': LAMBDA_FUNCTION_NAME,
            'iam_role_name': IAM_ROLE_NAME,
            'athena_database': ATHENA_DATABASE,
            'region': AWS_REGION,
            'deployment_time': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        import json
        deployment_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'deployment_info.json'
        )
        with open(deployment_file, 'w') as f:
            json.dump(deployment_info, f, indent=2)
        
        print(f"Deployment info saved to: {deployment_file}")
        print()
        print("="*70)
        
        return deployment_info
        
    except Exception as e:
        print()
        print("="*70)
        print("DEPLOYMENT FAILED")
        print("="*70)
        print(f"Error: {str(e)}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
