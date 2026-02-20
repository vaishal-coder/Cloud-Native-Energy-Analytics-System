"""Diagnose Lambda function issues"""
import boto3
import json
import time

def load_deployment_info():
    """Load deployment information"""
    with open('deployment_info.json', 'r') as f:
        return json.load(f)

def check_lambda_logs():
    """Check Lambda CloudWatch logs"""
    deployment_info = load_deployment_info()
    lambda_name = deployment_info['lambda_function_name']
    
    logs_client = boto3.client('logs', region_name='us-east-1')
    
    log_group = f'/aws/lambda/{lambda_name}'
    
    print("="*70)
    print("LAMBDA DIAGNOSTICS")
    print("="*70)
    print(f"Function: {lambda_name}")
    print()
    
    try:
        # Get log streams
        response = logs_client.describe_log_streams(
            logGroupName=log_group,
            orderBy='LastEventTime',
            descending=True,
            limit=5
        )
        
        if not response.get('logStreams'):
            print("⚠️  No log streams found")
            print("   Lambda may not have been invoked yet")
            print()
            print("Possible reasons:")
            print("1. S3 trigger not configured properly")
            print("2. Lambda hasn't been invoked yet")
            print("3. File uploaded to wrong S3 location")
            return
        
        print(f"✓ Found {len(response['logStreams'])} recent log streams")
        print()
        
        # Get latest logs
        latest_stream = response['logStreams'][0]
        stream_name = latest_stream['logStreamName']
        
        print(f"Latest execution: {stream_name}")
        print("-"*70)
        
        log_response = logs_client.get_log_events(
            logGroupName=log_group,
            logStreamName=stream_name,
            limit=100
        )
        
        if not log_response.get('events'):
            print("No log events found")
            return
        
        # Print logs
        for event in log_response['events']:
            message = event['message'].strip()
            if message:
                print(message)
        
        print()
        print("-"*70)
        
        # Check for common errors
        all_logs = '\n'.join([e['message'] for e in log_response['events']])
        
        if 'ModuleNotFoundError' in all_logs or 'ImportError' in all_logs:
            print()
            print("❌ ERROR DETECTED: Missing Python packages")
            print()
            print("The Lambda function is missing required dependencies.")
            print("Lambda needs: pandas, numpy, prophet, etc.")
            print()
            print("SOLUTION:")
            print("1. Create a Lambda layer with dependencies")
            print("2. Or use a simplified version without Prophet")
            print()
            print("Quick fix - Run:")
            print("  python scripts/fix_lambda_dependencies.py")
            
        elif 'Task timed out' in all_logs:
            print()
            print("❌ ERROR: Lambda timeout")
            print("Increase timeout or optimize code")
            
        elif 'errorMessage' in all_logs or 'ERROR' in all_logs:
            print()
            print("❌ ERROR detected in logs (see above)")
            
        else:
            print()
            print("✓ No obvious errors detected")
        
    except Exception as e:
        print(f"Error checking logs: {str(e)}")
        print()
        print("This might mean:")
        print("1. Log group doesn't exist yet (Lambda never invoked)")
        print("2. Insufficient permissions to read logs")

def check_s3_trigger():
    """Check if S3 trigger is configured"""
    deployment_info = load_deployment_info()
    bucket_name = deployment_info['bucket_name']
    
    s3_client = boto3.client('s3', region_name='us-east-1')
    
    print()
    print("="*70)
    print("S3 TRIGGER CHECK")
    print("="*70)
    
    try:
        response = s3_client.get_bucket_notification_configuration(
            Bucket=bucket_name
        )
        
        if 'LambdaFunctionConfigurations' in response:
            configs = response['LambdaFunctionConfigurations']
            print(f"✓ Found {len(configs)} Lambda trigger(s)")
            for config in configs:
                print(f"  • Events: {config.get('Events', [])}")
                print(f"  • Function: {config.get('LambdaFunctionArn', 'N/A')}")
                if 'Filter' in config:
                    rules = config['Filter']['Key']['FilterRules']
                    for rule in rules:
                        print(f"  • {rule['Name']}: {rule['Value']}")
        else:
            print("⚠️  No Lambda triggers configured")
            print()
            print("SOLUTION: Manually configure S3 trigger:")
            print("1. Go to S3 Console")
            print(f"2. Open bucket: {bucket_name}")
            print("3. Go to Properties → Event notifications")
            print("4. Create notification:")
            print("   - Event: All object create events")
            print("   - Prefix: raw/")
            print("   - Suffix: .csv")
            print(f"   - Destination: Lambda function 'energy-pipeline'")
    
    except Exception as e:
        print(f"Error checking S3 trigger: {str(e)}")

def check_lambda_config():
    """Check Lambda function configuration"""
    deployment_info = load_deployment_info()
    lambda_name = deployment_info['lambda_function_name']
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    print()
    print("="*70)
    print("LAMBDA CONFIGURATION")
    print("="*70)
    
    try:
        response = lambda_client.get_function(FunctionName=lambda_name)
        config = response['Configuration']
        
        print(f"Runtime: {config['Runtime']}")
        print(f"Memory: {config['MemorySize']} MB")
        print(f"Timeout: {config['Timeout']} seconds")
        print(f"Code Size: {config['CodeSize']} bytes")
        print(f"Layers: {len(config.get('Layers', []))}")
        
        if not config.get('Layers'):
            print()
            print("⚠️  No Lambda layers attached")
            print("   Dependencies (pandas, prophet) are missing")
            print()
            print("SOLUTION:")
            print("  python scripts/fix_lambda_dependencies.py")
        
    except Exception as e:
        print(f"Error checking Lambda config: {str(e)}")

if __name__ == '__main__':
    check_lambda_config()
    check_s3_trigger()
    check_lambda_logs()
    
    print()
    print("="*70)
    print("NEXT STEPS")
    print("="*70)
    print()
    print("If Lambda is missing dependencies:")
    print("  python scripts/fix_lambda_dependencies.py")
    print()
    print("To manually trigger Lambda for testing:")
    print("  python scripts/test_lambda_manually.py")
    print()
    print("="*70)
