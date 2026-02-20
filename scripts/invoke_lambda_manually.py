"""Manually invoke Lambda function for testing"""
import boto3
import json

def load_deployment_info():
    """Load deployment information"""
    with open('deployment_info.json', 'r') as f:
        return json.load(f)

def invoke_lambda():
    """Manually invoke Lambda function"""
    deployment_info = load_deployment_info()
    lambda_name = deployment_info['lambda_function_name']
    bucket_name = deployment_info['bucket_name']
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    print("="*70)
    print("MANUALLY INVOKING LAMBDA FUNCTION")
    print("="*70)
    print()
    
    # Create test event
    test_event = {
        "Records": [
            {
                "s3": {
                    "bucket": {
                        "name": bucket_name
                    },
                    "object": {
                        "key": "raw/test_20260221_010504.csv"
                    }
                }
            }
        ]
    }
    
    print(f"Function: {lambda_name}")
    print(f"Test file: s3://{bucket_name}/raw/test_20260221_010504.csv")
    print()
    print("Invoking Lambda...")
    
    try:
        response = lambda_client.invoke(
            FunctionName=lambda_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(test_event)
        )
        
        # Read response
        payload = json.loads(response['Payload'].read())
        
        print()
        print("="*70)
        print("LAMBDA RESPONSE")
        print("="*70)
        print()
        
        if response['StatusCode'] == 200:
            print("✓ Lambda invoked successfully")
            print()
            print("Response:")
            print(json.dumps(payload, indent=2))
            
            if 'errorMessage' in payload:
                print()
                print("❌ Lambda execution failed:")
                print(payload['errorMessage'])
                if 'errorType' in payload:
                    print(f"Error type: {payload['errorType']}")
                if 'stackTrace' in payload:
                    print("\nStack trace:")
                    for line in payload['stackTrace']:
                        print(f"  {line}")
            else:
                print()
                print("✓ Lambda executed successfully!")
                print()
                print("Now check results:")
                print("  python scripts/check_results.py")
        else:
            print(f"✗ Lambda invocation failed with status: {response['StatusCode']}")
        
        print()
        print("="*70)
        
    except Exception as e:
        print(f"✗ Error invoking Lambda: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    invoke_lambda()
