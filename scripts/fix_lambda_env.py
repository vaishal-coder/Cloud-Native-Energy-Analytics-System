"""Fix Lambda environment variable with correct bucket name"""
import boto3
import json

def load_deployment_info():
    """Load deployment information"""
    with open('deployment_info.json', 'r') as f:
        return json.load(f)

def fix_lambda_environment():
    """Update Lambda environment variable with correct bucket"""
    deployment_info = load_deployment_info()
    lambda_name = deployment_info['lambda_function_name']
    bucket_name = deployment_info['bucket_name']
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    print("="*70)
    print("FIXING LAMBDA ENVIRONMENT VARIABLE")
    print("="*70)
    print()
    print(f"Lambda function: {lambda_name}")
    print(f"Correct bucket: {bucket_name}")
    print()
    
    try:
        # Update environment variable
        response = lambda_client.update_function_configuration(
            FunctionName=lambda_name,
            Environment={
                'Variables': {
                    'BUCKET_NAME': bucket_name
                }
            }
        )
        
        print("✓ Updated Lambda environment variable")
        print(f"  BUCKET_NAME = {bucket_name}")
        print()
        print("Waiting for update to complete (10 seconds)...")
        
        import time
        time.sleep(10)
        
        print()
        print("="*70)
        print("SUCCESS! Lambda environment fixed")
        print("="*70)
        print()
        print("Now test the pipeline:")
        print("  python scripts/invoke_lambda_manually.py")
        print()
        print("Or upload a new file:")
        print(f"  aws s3 cp data/output/energy_data.csv s3://{bucket_name}/raw/test_fixed.csv")
        print()
        
    except Exception as e:
        print(f"✗ Error updating Lambda: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    fix_lambda_environment()
