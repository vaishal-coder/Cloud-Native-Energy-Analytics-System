"""Main Lambda function handler for energy analytics pipeline"""
import json
import boto3
import os
import logging
from datetime import datetime
from io import StringIO
import pandas as pd

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Import local modules
from processing import EnergyDataProcessor
from forecasting import EnergyForecaster
from genai_insights import EnergyInsightsAssistant, VirtualEnergyAuditor

# AWS clients
s3_client = boto3.client('s3')

# Configuration from environment
BUCKET_NAME = os.environ.get('BUCKET_NAME')
ATHENA_DATABASE = os.environ.get('ATHENA_DATABASE')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
USE_BEDROCK = os.environ.get('USE_BEDROCK', 'false').lower() == 'true'

def lambda_handler(event, context):
    """Main Lambda handler triggered by S3 upload"""
    try:
        logger.info("Energy analytics pipeline started")
        logger.info(f"Event: {json.dumps(event)}")
        
        # Extract S3 event details
        s3_event = event['Records'][0]['s3']
        bucket = s3_event['bucket']['name']
        key = s3_event['object']['key']
        
        logger.info(f"Processing file: s3://{bucket}/{key}")
        
        # Step 1: Read raw data from S3
        raw_data = read_s3_file(bucket, key)
        logger.info(f"Read {len(raw_data)} bytes from S3")
        
        # Step 2: Process data
        processor = EnergyDataProcessor(anomaly_threshold_sigma=2)
        processed_results = processor.process_data(raw_data)
        logger.info("Data processing completed")
        
        # Step 3: Save processed data
        save_processed_data(processed_results)
        logger.info("Processed data saved to S3")
        
        # Step 4: Generate forecast
        daily_df = processor.prepare_for_forecast(processed_results['processed_df'])
        forecaster = EnergyForecaster(forecast_days=7)
        forecast_df = forecaster.forecast(daily_df)
        forecast_summary = forecaster.format_forecast_summary(forecast_df)
        
        # Save forecast
        save_forecast(forecast_df)
        logger.info("Forecast generated and saved")
        
        # Step 5: Save anomalies
        save_anomalies(processed_results['anomalies'])
        logger.info(f"Saved {len(processed_results['anomalies'])} anomalies")
        
        # Step 6: Generate GenAI insights
        analytics_data = prepare_analytics_data(processed_results, forecast_summary)
        
        insights_assistant = EnergyInsightsAssistant(use_bedrock=USE_BEDROCK)
        insights = insights_assistant.generate_insights(analytics_data)
        
        auditor = VirtualEnergyAuditor()
        audit_report = auditor.generate_audit_report(
            processed_results['appliance_stats'].to_dict('records')
        )
        
        # Step 7: Generate and save final report
        final_report = generate_final_report(insights, audit_report, analytics_data)
        save_report(final_report)
        logger.info("GenAI reports generated and saved")
        
        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Energy analytics pipeline completed successfully',
                'processed_file': key,
                'anomalies_detected': len(processed_results['anomalies']),
                'forecast_days': 7,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Pipeline execution failed',
                'error': str(e)
            })
        }

def read_s3_file(bucket, key):
    """Read file content from S3"""
    response = s3_client.get_object(Bucket=bucket, Key=key)
    return response['Body'].read().decode('utf-8')

def save_processed_data(processed_results):
    """Save processed data to S3"""
    appliance_stats = processed_results['appliance_stats']
    
    # Convert to CSV
    csv_buffer = StringIO()
    appliance_stats.to_csv(csv_buffer, index=False)
    
    # Upload to S3
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    key = f"processed/aggregated_{timestamp}.csv"
    
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=csv_buffer.getvalue(),
        ContentType='text/csv'
    )
    
    logger.info(f"Saved processed data: {key}")

def save_forecast(forecast_df):
    """Save forecast to S3"""
    csv_buffer = StringIO()
    forecast_df.to_csv(csv_buffer, index=False)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    key = f"forecast/forecast_{timestamp}.csv"
    
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=csv_buffer.getvalue(),
        ContentType='text/csv'
    )
    
    logger.info(f"Saved forecast: {key}")

def save_anomalies(anomalies_df):
    """Save anomalies to S3"""
    if len(anomalies_df) == 0:
        logger.info("No anomalies detected")
        return
    
    csv_buffer = StringIO()
    anomalies_df.to_csv(csv_buffer, index=False)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    key = f"anomalies/anomalies_{timestamp}.csv"
    
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=csv_buffer.getvalue(),
        ContentType='text/csv'
    )
    
    logger.info(f"Saved anomalies: {key}")

def save_report(report_content):
    """Save final report to S3"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    key = f"reports/final_report_{timestamp}.txt"
    
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=report_content,
        ContentType='text/plain'
    )
    
    logger.info(f"Saved report: {key}")

def prepare_analytics_data(processed_results, forecast_summary):
    """Prepare analytics data for GenAI"""
    appliance_stats = processed_results['appliance_stats'].to_dict('records')
    peak_hours = processed_results['peak_hours'].to_dict('records')
    
    total_usage = sum(stat['total_kwh'] for stat in appliance_stats)
    
    return {
        'total_usage': total_usage,
        'peak_hours': peak_hours,
        'anomaly_count': len(processed_results['anomalies']),
        'appliance_stats': appliance_stats,
        'forecast_summary': forecast_summary
    }

def generate_final_report(insights, audit_report, analytics_data):
    """Generate comprehensive final report"""
    report = f"""
{'='*70}
ENERGY USAGE ANALYSIS & FORECASTING SYSTEM
COMPREHENSIVE REPORT
{'='*70}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'='*70}
EXECUTIVE SUMMARY
{'='*70}

Total Energy Consumption: {analytics_data['total_usage']:.2f} kWh (30 days)
Daily Average: {analytics_data['total_usage']/30:.2f} kWh
Anomalies Detected: {analytics_data['anomaly_count']}
Forecast Period: 7 days

{'='*70}
AI-GENERATED INSIGHTS
{'='*70}

{insights}

{'='*70}
{audit_report}

{'='*70}
FORECAST SUMMARY
{'='*70}

7-Day Energy Consumption Forecast:
"""
    
    if 'forecast_summary' in analytics_data and analytics_data['forecast_summary']:
        fs = analytics_data['forecast_summary']
        report += f"\nTotal Predicted: {fs.get('total_predicted_kwh', 0):.2f} kWh\n"
        report += f"Daily Average: {fs.get('avg_predicted_kwh', 0):.2f} kWh\n"
        report += f"Period: {fs.get('start_date', 'N/A')} to {fs.get('end_date', 'N/A')}\n"
        
        report += "\nDaily Breakdown:\n"
        for pred in fs.get('daily_predictions', []):
            report += f"  {pred['date']}: {pred['predicted_kwh']:.2f} kWh "
            report += f"(Range: {pred['lower_bound']:.2f} - {pred['upper_bound']:.2f})\n"
    
    report += f"\n{'='*70}\n"
    report += "END OF REPORT\n"
    report += f"{'='*70}\n"
    
    return report
