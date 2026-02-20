# Energy Analytics System - Quick Reference

## 🚀 Quick Start (3 Commands)

```bash
python infrastructure/deploy.py          # Deploy infrastructure
python data/generate_data.py             # Generate test data
python scripts/upload_data.py data/output/energy_data.csv  # Trigger pipeline
```

## 📋 Common Commands

### Deployment
```bash
# Full deployment
python infrastructure/deploy.py

# Check deployment status
cat deployment_info.json
```

### Data Operations
```bash
# Generate synthetic data
python data/generate_data.py

# Upload to S3 (triggers pipeline)
python scripts/upload_data.py <csv_file>
aws s3 cp <file> s3://<bucket>/raw/

# Check results
python scripts/check_results.py
```

### Monitoring
```bash
# Tail Lambda logs
aws logs tail /aws/lambda/energy-pipeline --follow

# Filter errors
aws logs filter-pattern /aws/lambda/energy-pipeline --pattern "ERROR"

# Last hour logs
aws logs tail /aws/lambda/energy-pipeline --since 1h
```

### Athena Queries
```bash
# Interactive query tool
python scripts/query_athena.py

# Direct query
aws athena start-query-execution \
  --query-string "SELECT * FROM energy_db.processed_energy_data" \
  --result-configuration "OutputLocation=s3://<bucket>/athena-results/"
```

### S3 Operations
```bash
# List files
aws s3 ls s3://<bucket>/reports/

# Download latest report
aws s3 cp s3://<bucket>/reports/ . --recursive

# Check bucket size
aws s3 ls s3://<bucket> --recursive --summarize
```

### Cleanup
```bash
# Remove all resources
python scripts/cleanup.py

# Manual S3 cleanup
aws s3 rb s3://<bucket> --force
```

## 🏗️ Resource Names

| Resource | Name Pattern |
|----------|--------------|
| S3 Bucket | energy-analytics-<random> |
| Lambda Function | energy-pipeline |
| IAM Role | energy-lambda-role |
| Athena Database | energy_db |
| Log Group | /aws/lambda/energy-pipeline |

## 📁 S3 Folder Structure

```
s3://energy-analytics-xxxxx/
├── raw/              # Upload CSV here (triggers pipeline)
├── processed/        # Aggregated statistics
├── forecast/         # 7-day predictions
├── anomalies/        # Detected anomalies
├── reports/          # GenAI reports
└── athena-results/   # Query outputs
```

## 🔧 Configuration

### Environment Variables (Lambda)
```bash
BUCKET_NAME=energy-analytics-xxxxx
ATHENA_DATABASE=energy_db
AWS_REGION=us-east-1
OPENAI_API_KEY=sk-...  # Optional
USE_BEDROCK=false      # Optional
```

### config/config.py
```python
LAMBDA_TIMEOUT = 900        # seconds
LAMBDA_MEMORY = 3008        # MB
FORECAST_DAYS = 7           # days
ANOMALY_THRESHOLD_SIGMA = 2 # std deviations
DATA_DAYS = 30              # days of synthetic data
```

## 📊 Data Format

### Input CSV
```csv
timestamp,appliance,kwh
2026-02-20 00:00:00,AC,2.345
2026-02-20 00:00:00,Refrigerator,0.156
```

### Appliances
- AC
- Refrigerator
- Heater
- Washing Machine

## 🔍 Troubleshooting

### Lambda Not Triggered
```bash
# Check trigger configuration
aws lambda get-function --function-name energy-pipeline

# Verify S3 notification
aws s3api get-bucket-notification-configuration --bucket <bucket>

# Check file location (must be in raw/)
aws s3 ls s3://<bucket>/raw/
```

### Permission Errors
```bash
# Check IAM role
aws iam get-role --role-name energy-lambda-role

# List attached policies
aws iam list-role-policies --role-name energy-lambda-role

# Wait for IAM propagation (10-15 seconds after creation)
```

### No Outputs
```bash
# Check Lambda logs for errors
aws logs tail /aws/lambda/energy-pipeline --follow

# Verify Lambda execution
aws lambda list-functions | grep energy-pipeline

# Check S3 permissions
aws s3 ls s3://<bucket>/
```

## 📈 Sample Athena Queries

### Total by Appliance
```sql
SELECT appliance, SUM(kwh) as total
FROM energy_db.raw_energy_data
GROUP BY appliance
ORDER BY total DESC;
```

### Peak Hours
```sql
SELECT CAST(SUBSTR(timestamp, 12, 2) AS INTEGER) as hour,
       SUM(kwh) as total
FROM energy_db.raw_energy_data
GROUP BY CAST(SUBSTR(timestamp, 12, 2) AS INTEGER)
ORDER BY total DESC
LIMIT 10;
```

### Daily Trend
```sql
SELECT SUBSTR(timestamp, 1, 10) as date,
       SUM(kwh) as daily_total
FROM energy_db.raw_energy_data
GROUP BY SUBSTR(timestamp, 1, 10)
ORDER BY date DESC
LIMIT 30;
```

### Latest Forecast
```sql
SELECT * FROM energy_db.forecast_data
ORDER BY ds DESC
LIMIT 7;
```

## 💰 Cost Estimate

| Service | Monthly Cost |
|---------|--------------|
| S3 (20 GB) | $0.50 |
| Lambda (100 runs) | $2.00 |
| Athena (20 GB) | $1.00 |
| CloudWatch | $0.50 |
| **Total** | **~$4.00** |

## 🎯 Success Indicators

- ✓ Lambda completes in < 60 seconds
- ✓ Files in all 4 output folders
- ✓ Report contains insights
- ✓ No errors in logs
- ✓ Athena queries return data

## 📞 Quick Help

### Check System Status
```bash
# Deployment info
cat deployment_info.json

# Lambda status
aws lambda get-function --function-name energy-pipeline

# Recent executions
aws logs tail /aws/lambda/energy-pipeline --since 1h

# S3 contents
aws s3 ls s3://<bucket>/ --recursive --human-readable
```

### Get Latest Report
```bash
# List reports
aws s3 ls s3://<bucket>/reports/

# Download latest
aws s3 cp s3://<bucket>/reports/ . --recursive --exclude "*" --include "final_report_*.txt"

# View in terminal
aws s3 cp s3://<bucket>/reports/<latest-file> - | less
```

### Redeploy Lambda
```bash
# Update function code
python infrastructure/deploy.py

# Or manually
cd lambda
zip -r ../lambda.zip .
aws lambda update-function-code \
  --function-name energy-pipeline \
  --zip-file fileb://../lambda.zip
```

## 🔗 Useful Links

### AWS Console
- S3: https://console.aws.amazon.com/s3/
- Lambda: https://console.aws.amazon.com/lambda/
- Athena: https://console.aws.amazon.com/athena/
- CloudWatch: https://console.aws.amazon.com/cloudwatch/
- IAM: https://console.aws.amazon.com/iam/

### Documentation
- README.md - Quick start
- ARCHITECTURE.md - System design
- DEPLOYMENT_GUIDE.md - Detailed deployment
- EXECUTION_SUMMARY.md - Complete summary

## 🎓 Key Concepts

### Pipeline Flow
```
CSV Upload → S3 Event → Lambda Trigger → Process Data →
Detect Anomalies → Generate Forecast → GenAI Insights →
Save Outputs → Complete
```

### ML Components
- **Forecasting**: Prophet (7-day prediction)
- **Anomaly Detection**: Z-score (μ + 2σ)
- **GenAI**: OpenAI / Bedrock / Rule-based

### Security
- Least privilege IAM
- Bucket-specific access
- No hardcoded credentials
- CloudWatch logging

## 📝 File Naming Patterns

```
processed/aggregated_YYYYMMDD_HHMMSS.csv
forecast/forecast_YYYYMMDD_HHMMSS.csv
anomalies/anomalies_YYYYMMDD_HHMMSS.csv
reports/final_report_YYYYMMDD_HHMMSS.txt
```

## ⚡ Performance Tips

- Use gzip compression for CSV files
- Convert to Parquet for Athena (70% cost reduction)
- Set appropriate Lambda memory
- Use S3 Lifecycle policies
- Partition data by date for large datasets

## 🛠️ Development

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Run data generator
python data/generate_data.py

# Test processing locally
python -c "from lambda.processing import *; ..."
```

### Add New Appliance
Edit `config/config.py`:
```python
APPLIANCES = ['AC', 'Refrigerator', 'Heater', 'Washing Machine', 'Dishwasher']
```

### Adjust Forecast Period
Edit `config/config.py`:
```python
FORECAST_DAYS = 14  # Change from 7 to 14 days
```

### Change Anomaly Sensitivity
Edit `config/config.py`:
```python
ANOMALY_THRESHOLD_SIGMA = 3  # More strict (fewer anomalies)
ANOMALY_THRESHOLD_SIGMA = 1  # Less strict (more anomalies)
```

---

**Quick Reference v1.0** | For detailed info, see full documentation
