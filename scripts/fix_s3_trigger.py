"""Fix S3 trigger configuration"""
import boto3
import json
import time

def load_deployment_info():
    """Load deployment information"""
    with open('deployment_info.json', 'r') as f:
        return json.load(f)

def fix_s3_trigger():
    """Fix S3 trigger configuration"""
    deployment_info = load_deployment_info()
    bucket_name = deployment_info['bucket_name']
    lambda_arn = deployment_info['lambda_arn']
    lambda_name = deployment_info['lambda_function_name']
    
    s3_client = boto3.client('s3', region_name='us-east-1')
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    print("="*70)
    print("FIXING S3 TRIGGER CONFIGURATION")
    print("="*70)
    print()
    
    # Step 1: Check and add Lambda permission
    print("Step 1: Checking Lambda permissions...")
    print("-"*70)
    
    try:
        policy = lambda_client.get_policy(FunctionName=lambda_name)
        print("✓ Lambda has existing permissions")
    except:
        print("⚠ No Lambda permissions found")
    
    # Add S3 invoke permission
    try:
        lambda_client.add_permission(
            FunctionName=lambda_name,
            StatementId='S3InvokePermission',
            Action='lambda:InvokeFunction',
            Principal='s3.amazonaws.com',
            SourceArn=f'arn:aws:s3:::{bucket_name}',
            SourceAccount='085470048041'
        )
        print("✓ Added S3 invoke permission")
    except Exception as e:
        if 'ResourceConflictException' in str(e):
            print("✓ S3 invoke permission already exists")
        else:
            print(f"⚠ Error adding permission: {str(e)}")
    
    print()
    
    # Step 2: Configure S3 trigger
    print("Step 2: Configuring S3 trigger...")
    print("-"*70)
    
    notification_config = {
        'LambdaFunctionConfigurations': [
            {
                'Id': 'energy-pipeline-trigger',
                'LambdaFunctionArn': lambda_arn,
                'Events': ['s3:ObjectCreated:*'],
                'Filter': {
                    'Key': {
                        'FilterRules': [
                            {'Name': 'prefix', 'Value': 'raw/'},
                            {'Name': 'suffix', 'Value': '.csv'}
                        ]
                    }
                }
            }
        ]
    }
    
    try:
        s3_client.put_bucket_notification_configuration(
            Bucket=bucket_name,
            NotificationConfiguration=notification_config
        )
        print("✓ S3 trigger configured successfully")
    except Exception as e:
        print(f"✗ Error configuring S3 trigger: {str(e)}")
        print()
        print("Manual fix required:")
        print("1. Go to AWS Console → S3")
        print(f"2. Open bucket: {bucket_name}")
        print("3. Properties → Event notifications → Create")
        print("4. Configure:")
        print("   - Event: All object create events")
        print("   - Prefix: raw/")
        print("   - Suffix: .csv")
        print(f"   - Destination: Lambda function '{lambda_name}'")
        return False
    
    print()
    
    # Step 3: Verify configuration
    print("Step 3: Verifying configuration...")
    print("-"*70)
    
    try:
        response = s3_client.get_bucket_notification_configuration(
            Bucket=bucket_name
        )
        
        if 'LambdaFunctionConfigurations' in response:
            configs = response['LambdaFunctionConfigurations']
            print(f"✓ Found {len(configs)} Lambda trigger(s)")
            for config in configs:
                print(f"  • Function: {config.get('LambdaFunctionArn', 'N/A').split(':')[-1]}")
                print(f"  • Events: {', '.join(config.get('Events', []))}")
                if 'Filter' in config:
                    rules = config['Filter']['Key']['FilterRules']
                    for rule in rules:
                        print(f"  • {rule['Name']}: {rule['Value']}")
        else:
            print("⚠ No Lambda triggers found")
            return False
    except Exception as e:
        print(f"✗ Error verifying configuration: {str(e)}")
        return False
    
    print()
    
    # Step 4: Test the trigger
    print("Step 4: Testing the trigger...")
    print("-"*70)
    print()
    print("Uploading test file...")
    
    try:
        # Upload a test file
        test_content = "timestamp,appliance,kwh\n2026-02-21 00:00:00,AC,2.5\n"
        test_key = f'raw/trigger_test_{int(time.time())}.csv'
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content
        )
        
        print(f"✓ Uploaded test file: {test_key}")
        print()
        print("Waiting for Lambda to process (15 seconds)...")
        time.sleep(15)
        
        # Check if Lambda was invoked
        logs_client = boto3.client('logs', region_name='us-east-1')
        log_group = f'/aws/lambda/{lambda_name}'
        
        try:
            response = logs_client.describe_log_streams(
                logGroupName=log_group,
                orderBy='LastEventTime',
                descending=True,
                limit=1
            )
            
            if response.get('logStreams'):
                latest_stream = response['logStreams'][0]
                last_event_time = latest_stream.get('lastEventTime', 0)
                
                # Check if log is recent (within last 30 seconds)
                current_time = int(time.time() * 1000)
                if current_time - last_event_time < 30000:
                    print("✓ Lambda was invoked!")
                    print()
                    print("Checking for outputs...")
                    
                    # Check for outputs
                    folders = ['processed/', 'forecast/', 'reports/']
                    found_outputs = False
                    
                    for folder in folders:
                        response = s3_client.list_objects_v2(
                            Bucket=bucket_name,
                            Prefix=folder,
                            MaxKeys=5
                        )
                        
                        if 'Contents' in response:
                            files = [obj['Key'] for obj in response['Contents'] if not obj['Key'].endswith('/')]
                            if files:
                                print(f"  ✓ {folder}: {len(files)} file(s)")
                                found_outputs = True
                    
                    if found_outputs:
                        print()
                        print("="*70)
                        print("✓ SUCCESS! S3 TRIGGER IS WORKING!")
                        print("="*70)
                        print()
                        print("Your Energy Analytics System is fully operational!")
                        print()
                        print("Next steps:")
                        print("1. Check results: python scripts/check_results.py")
                        print("2. View report: aws s3 ls s3://{}/reports/".format(bucket_name))
                        print("3. Query data: python scripts/query_athena.py")
                        return True
                    else:
                        print()
                        print("⚠ Lambda invoked but no outputs generated")
                        print("Check Lambda logs for errors:")
                        print(f"  aws logs tail /aws/lambda/{lambda_name} --follow")
                else:
                    print("⚠ Lambda not invoked recently")
                    print("S3 trigger may still be propagating (can take a few minutes)")
            else:
                print("⚠ No Lambda executions found")
                print("S3 trigger may not be working")
        
        except Exception as e:
            print(f"⚠ Could not check Lambda logs: {str(e)}")
    
    except Exception as e:
        print(f"✗ Error testing trigger: {str(e)}")
        return False
    
    print()
    print("="*70)
    print("CONFIGURATION COMPLETE")
    print("="*70)
    print()
    print("If outputs weren't generated, try:")
    print("1. Wait a few more minutes (trigger propagation)")
    print("2. Upload another file:")
    print(f"   aws s3 cp data/output/energy_data.csv s3://{bucket_name}/raw/")
    print("3. Check Lambda logs:")
    print(f"   aws logs tail /aws/lambda/{lambda_name} --follow")
    print()
    
    return True

if __name__ == '__main__':
    fix_s3_trigger()
