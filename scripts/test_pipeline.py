"""Test the complete pipeline"""
import boto3
import json
import time
from datetime import datetime

def load_deployment_info():
    """Load deployment information"""
    with open('deployment_info.json', 'r') as f:
        return json.load(f)

def upload_test_file():
    """Upload test file to S3"""
    deployment_info = load_deployment_info()
    bucket_name = deployment_info['bucket_name']
    
    s3_client = boto3.client('s3', region_name='us-east-1')
    
    print("="*70)
    print("TESTING ENERGY ANALYTICS PIPELINE")
    print("="*70)
    print()
    
    # Upload file
    source_file = 'data/output/energy_data.csv'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    s3_key = f'raw/test_{timestamp}.csv'
    
    print(f"Uploading test file...")
    print(f"  Source: {source_file}")
    print(f"  Destination: s3://{bucket_name}/{s3_key}")
    
    try:
        with open(source_file, 'rb') as f:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=f
            )
        
        print("✓ Upload successful!")
        print()
        print("Waiting for Lambda to process (20 seconds)...")
        time.sleep(20)
        
        # Check results
        print()
        print("="*70)
        print("CHECKING RESULTS")
        print("="*70)
        print()
        
        folders = ['processed/', 'forecast/', 'anomalies/', 'reports/']
        results = {}
        
        for folder in folders:
            try:
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=folder,
                    MaxKeys=10
                )
                
                if 'Contents' in response:
                    files = [obj['Key'] for obj in response['Contents'] if not obj['Key'].endswith('/')]
                    results[folder] = files
                    
                    if files:
                        print(f"✓ {folder}: {len(files)} file(s)")
                        # Show latest file
                        latest = sorted(files)[-1]
                        print(f"    Latest: {latest}")
                    else:
                        print(f"⚠ {folder}: No files yet")
                else:
                    results[folder] = []
                    print(f"⚠ {folder}: No files yet")
            except Exception as e:
                print(f"✗ {folder}: Error - {str(e)}")
                results[folder] = []
        
        print()
        
        # Check if report was generated
        if results.get('reports/'):
            print("="*70)
            print("GENERATED REPORT")
            print("="*70)
            print()
            
            latest_report = sorted(results['reports/'])[-1]
            
            try:
                response = s3_client.get_object(Bucket=bucket_name, Key=latest_report)
                report_content = response['Body'].read().decode('utf-8')
                print(report_content)
            except Exception as e:
                print(f"Error reading report: {str(e)}")
        
        # Summary
        print()
        print("="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        total_outputs = sum(len(files) for files in results.values())
        
        if total_outputs >= 3:  # At least processed, forecast, and report
            print("✓ PIPELINE TEST PASSED!")
            print(f"  Generated {total_outputs} output files")
            print()
            print("Your Energy Analytics System is working correctly!")
        else:
            print("⚠ PIPELINE TEST INCOMPLETE")
            print(f"  Only {total_outputs} output files generated")
            print()
            print("Check Lambda logs for errors:")
            print("  aws logs tail /aws/lambda/energy-pipeline --follow")
        
        print()
        print("="*70)
        
    except FileNotFoundError:
        print(f"✗ Error: {source_file} not found")
        print("Run: python data/generate_data.py")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    upload_test_file()
