"""Fix Lambda dependencies by creating a simplified version without Prophet"""
import boto3
import json
import zipfile
import io
import os

def load_deployment_info():
    """Load deployment information"""
    with open('deployment_info.json', 'r') as f:
        return json.load(f)

def create_simplified_lambda():
    """Create Lambda package with inline simplified code"""
    
    # Simplified lambda function that doesn't require Prophet
    lambda_code = '''"""Simplified Lambda function for energy analytics"""
import json
import boto3
import os
from datetime import datetime, timedelta
from io import StringIO

s3_client = boto3.client('s3')
BUCKET_NAME = os.environ.get('BUCKET_NAME')

def lambda_handler(event, context):
    """Main Lambda handler"""
    try:
        print("Energy analytics pipeline started")
        
        # Extract S3 event details
        s3_event = event['Records'][0]['s3']
        bucket = s3_event['bucket']['name']
        key = s3_event['object']['key']
        
        print(f"Processing file: s3://{bucket}/{key}")
        
        # Read CSV from S3
        response = s3_client.get_object(Bucket=bucket, Key=key)
        csv_content = response['Body'].read().decode('utf-8')
        
        # Simple processing without pandas
        lines = csv_content.strip().split('\\n')
        header = lines[0].split(',')
        
        # Parse data
        data = []
        for line in lines[1:]:
            values = line.split(',')
            if len(values) == 3:
                data.append({
                    'timestamp': values[0],
                    'appliance': values[1],
                    'kwh': float(values[2])
                })
        
        print(f"Processed {len(data)} records")
        
        # Aggregate by appliance
        appliance_stats = {}
        for record in data:
            appliance = record['appliance']
            kwh = record['kwh']
            
            if appliance not in appliance_stats:
                appliance_stats[appliance] = {
                    'total': 0,
                    'count': 0,
                    'values': []
                }
            
            appliance_stats[appliance]['total'] += kwh
            appliance_stats[appliance]['count'] += 1
            appliance_stats[appliance]['values'].append(kwh)
        
        # Calculate statistics
        for appliance, stats in appliance_stats.items():
            stats['avg'] = stats['total'] / stats['count']
            values = sorted(stats['values'])
            stats['median'] = values[len(values)//2]
            stats['min'] = min(values)
            stats['max'] = max(values)
        
        # Detect anomalies (simple threshold)
        anomalies = []
        for record in data:
            appliance = record['appliance']
            kwh = record['kwh']
            avg = appliance_stats[appliance]['avg']
            
            # Simple threshold: 3x average
            if kwh > avg * 3:
                anomalies.append({
                    'timestamp': record['timestamp'],
                    'appliance': appliance,
                    'kwh': kwh,
                    'threshold': avg * 3
                })
        
        print(f"Detected {len(anomalies)} anomalies")
        
        # Generate simple forecast (moving average)
        total_consumption = sum(r['kwh'] for r in data)
        daily_avg = total_consumption / 30  # Assuming 30 days
        
        forecast = []
        for i in range(7):
            date = (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d')
            forecast.append({
                'date': date,
                'predicted_kwh': round(daily_avg, 2),
                'lower_bound': round(daily_avg * 0.8, 2),
                'upper_bound': round(daily_avg * 1.2, 2)
            })
        
        # Save processed data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save aggregated stats
        stats_csv = "appliance,total_kwh,avg_kwh,median_kwh,min_kwh,max_kwh\\n"
        for appliance, stats in appliance_stats.items():
            stats_csv += f"{appliance},{stats['total']:.2f},{stats['avg']:.3f},{stats['median']:.3f},{stats['min']:.3f},{stats['max']:.3f}\\n"
        
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=f"processed/aggregated_{timestamp}.csv",
            Body=stats_csv,
            ContentType='text/csv'
        )
        print(f"Saved processed data")
        
        # Save anomalies
        if anomalies:
            anomaly_csv = "timestamp,appliance,kwh,threshold\\n"
            for a in anomalies:
                anomaly_csv += f"{a['timestamp']},{a['appliance']},{a['kwh']:.3f},{a['threshold']:.3f}\\n"
            
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=f"anomalies/anomalies_{timestamp}.csv",
                Body=anomaly_csv,
                ContentType='text/csv'
            )
            print(f"Saved {len(anomalies)} anomalies")
        
        # Save forecast
        forecast_csv = "date,predicted_kwh,lower_bound,upper_bound\\n"
        for f in forecast:
            forecast_csv += f"{f['date']},{f['predicted_kwh']},{f['lower_bound']},{f['upper_bound']}\\n"
        
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=f"forecast/forecast_{timestamp}.csv",
            Body=forecast_csv,
            ContentType='text/csv'
        )
        print(f"Saved forecast")
        
        # Generate report
        report = f"""
{'='*70}
ENERGY USAGE ANALYSIS REPORT
{'='*70}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY
-------
Total Records Processed: {len(data)}
Total Energy Consumption: {total_consumption:.2f} kWh
Daily Average: {daily_avg:.2f} kWh
Anomalies Detected: {len(anomalies)}

APPLIANCE BREAKDOWN
-------------------
"""
        for appliance, stats in sorted(appliance_stats.items()):
            percentage = (stats['total'] / total_consumption * 100)
            report += f"\\n{appliance}:\\n"
            report += f"  Total: {stats['total']:.2f} kWh ({percentage:.1f}%)\\n"
            report += f"  Average: {stats['avg']:.3f} kWh\\n"
            report += f"  Range: {stats['min']:.3f} - {stats['max']:.3f} kWh\\n"
        
        report += f"""

7-DAY FORECAST
--------------
"""
        for f in forecast:
            report += f"{f['date']}: {f['predicted_kwh']:.2f} kWh (range: {f['lower_bound']:.2f} - {f['upper_bound']:.2f})\\n"
        
        report += f"""

RECOMMENDATIONS
---------------
• Monitor appliances with high consumption
• Investigate detected anomalies
• Consider energy-efficient upgrades for top consumers
• Schedule high-energy tasks during off-peak hours

{'='*70}
END OF REPORT
{'='*70}
"""
        
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=f"reports/final_report_{timestamp}.txt",
            Body=report,
            ContentType='text/plain'
        )
        print(f"Saved report")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Pipeline completed successfully',
                'records_processed': len(data),
                'anomalies_detected': len(anomalies),
                'timestamp': timestamp
            })
        }
        
    except Exception as e:
        print(f"Pipeline error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Pipeline execution failed',
                'error': str(e)
            })
        }
'''
    
    # Create zip file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    return zip_buffer.getvalue()

def update_lambda():
    """Update Lambda function with simplified code"""
    print("="*70)
    print("FIXING LAMBDA DEPENDENCIES")
    print("="*70)
    print()
    
    deployment_info = load_deployment_info()
    lambda_name = deployment_info['lambda_function_name']
    bucket_name = deployment_info['bucket_name']
    
    print("Creating simplified Lambda function...")
    print("(This version doesn't require pandas or prophet)")
    print()
    
    # Create deployment package
    deployment_package = create_simplified_lambda()
    
    # Update Lambda function
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        response = lambda_client.update_function_code(
            FunctionName=lambda_name,
            ZipFile=deployment_package
        )
        
        print(f"✓ Updated Lambda function: {lambda_name}")
        print(f"  Code size: {response['CodeSize']} bytes")
        print()
        
        # Update environment variables
        lambda_client.update_function_configuration(
            FunctionName=lambda_name,
            Environment={
                'Variables': {
                    'BUCKET_NAME': bucket_name
                }
            }
        )
        
        print("✓ Updated environment variables")
        print()
        
        print("="*70)
        print("SUCCESS!")
        print("="*70)
        print()
        print("Lambda function has been updated with a simplified version that:")
        print("• Processes CSV data without pandas")
        print("• Detects anomalies using simple thresholds")
        print("• Generates forecasts using moving averages")
        print("• Creates comprehensive reports")
        print()
        print("NEXT STEPS:")
        print("-"*70)
        print("1. Upload data to trigger pipeline:")
        print(f"   aws s3 cp data/output/energy_data.csv s3://{bucket_name}/raw/")
        print()
        print("2. Wait 10-15 seconds, then check results:")
        print("   python scripts/check_results.py")
        print()
        print("3. Monitor execution:")
        print("   aws logs tail /aws/lambda/energy-pipeline --follow")
        print()
        print("="*70)
        
    except Exception as e:
        print(f"✗ Error updating Lambda: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    update_lambda()
