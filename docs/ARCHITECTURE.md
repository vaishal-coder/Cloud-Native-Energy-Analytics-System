# Energy Analytics System - Architecture Documentation

## System Overview

Production-ready serverless energy analytics platform on AWS with ML forecasting and GenAI insights.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         DATA INGESTION                          │
│  Raw Energy Data (CSV) → S3 Bucket (raw/)                      │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ S3 Event Trigger
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AWS LAMBDA PIPELINE                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 1. Data Processing (PySpark-style with Pandas)          │  │
│  │    • Parse timestamps                                     │  │
│  │    • Aggregate by appliance                              │  │
│  │    • Peak hour analysis                                   │  │
│  │    • Z-score anomaly detection                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 2. ML Forecasting (Prophet)                              │  │
│  │    • Daily aggregation                                    │  │
│  │    • 7-day forecast generation                           │  │
│  │    • Confidence intervals                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 3. GenAI Insights                                        │  │
│  │    • Energy Insights Assistant                           │  │
│  │    • Virtual Energy Auditor                              │  │
│  │    • Behavioral recommendations                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ Write Results
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      S3 DATA LAKE                               │
│  • processed/    → Aggregated statistics                       │
│  • forecast/     → 7-day predictions                           │
│  • anomalies/    → Detected anomalies                          │
│  • reports/      → GenAI comprehensive reports                 │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ Query
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AWS ATHENA                                 │
│  • energy_db.raw_energy_data                                   │
│  • energy_db.processed_energy_data                             │
│  • energy_db.forecast_data                                     │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Data Layer (S3)

**Bucket Structure:**
```
energy-analytics-<unique-id>/
├── raw/              # Raw CSV uploads (trigger point)
├── processed/        # Aggregated statistics
├── forecast/         # ML predictions
├── anomalies/        # Detected anomalies
├── reports/          # GenAI reports
└── athena-results/   # Athena query outputs
```

**Data Flow:**
- Raw data uploaded to `raw/` folder
- S3 event notification triggers Lambda
- Processed outputs stored in respective folders

### 2. Processing Layer (Lambda)

**Function Configuration:**
- Runtime: Python 3.9
- Memory: 3008 MB
- Timeout: 900 seconds (15 minutes)
- Trigger: S3 ObjectCreated events on `raw/*.csv`

**Processing Pipeline:**

1. **Data Ingestion**
   - Read CSV from S3
   - Parse timestamps
   - Validate data structure

2. **Data Processing**
   - Appliance-wise aggregation (sum, mean, std)
   - Hourly consumption analysis
   - Peak hour identification
   - Z-score anomaly detection (threshold: mean + 2σ)

3. **ML Forecasting**
   - Daily consumption aggregation
   - Prophet model training
   - 7-day forecast with confidence intervals
   - Fallback to moving average if Prophet unavailable

4. **GenAI Analysis**
   - Energy Insights Assistant: Behavioral recommendations
   - Virtual Energy Auditor: Appliance upgrade suggestions
   - Supports OpenAI API or AWS Bedrock
   - Rule-based fallback for offline operation

5. **Output Generation**
   - Save processed data to S3
   - Save forecast results
   - Save anomaly records
   - Generate comprehensive report

### 3. Analytics Layer (Athena)

**Database:** `energy_db`

**Tables:**

1. **raw_energy_data**
   - Schema: timestamp, appliance, kwh
   - Location: s3://bucket/raw/
   - Format: CSV with header

2. **processed_energy_data**
   - Schema: appliance, total_kwh, avg_kwh, peak_hour
   - Location: s3://bucket/processed/
   - Format: CSV with header

3. **forecast_data**
   - Schema: ds, yhat, yhat_lower, yhat_upper
   - Location: s3://bucket/forecast/
   - Format: CSV with header

**Query Examples:**
```sql
-- Total consumption by appliance
SELECT appliance, SUM(kwh) as total
FROM energy_db.raw_energy_data
GROUP BY appliance
ORDER BY total DESC;

-- Peak hours analysis
SELECT HOUR(timestamp) as hour, SUM(kwh) as total
FROM energy_db.raw_energy_data
GROUP BY HOUR(timestamp)
ORDER BY total DESC;

-- Forecast summary
SELECT * FROM energy_db.forecast_data
ORDER BY ds DESC
LIMIT 7;
```

### 4. Security & IAM

**IAM Role:** `energy-lambda-role`

**Policies:**

1. **S3 Access** (Least Privilege)
   - GetObject, PutObject, DeleteObject on specific bucket
   - ListBucket on specific bucket

2. **Athena Access**
   - Query execution permissions
   - Glue catalog access for table management
   - S3 access for query results

3. **CloudWatch Logs**
   - CreateLogGroup, CreateLogStream, PutLogEvents
   - Automatic log retention

**Trust Policy:**
- Lambda service can assume the role

### 5. Monitoring & Logging

**CloudWatch Logs:**
- Log Group: `/aws/lambda/energy-pipeline`
- Retention: Default (never expire)
- Log Level: INFO

**Metrics:**
- Lambda invocations
- Duration
- Errors
- Throttles

**Monitoring Commands:**
```bash
# Tail logs
aws logs tail /aws/lambda/energy-pipeline --follow

# Get recent errors
aws logs filter-pattern /aws/lambda/energy-pipeline --pattern "ERROR"
```

## ML & AI Components

### Prophet Forecasting

**Model Configuration:**
- Daily seasonality: Disabled
- Weekly seasonality: Enabled
- Yearly seasonality: Disabled
- Changepoint prior scale: 0.05

**Output:**
- Point forecast (yhat)
- Lower bound (yhat_lower)
- Upper bound (yhat_upper)
- 7-day prediction horizon

### Anomaly Detection

**Method:** Z-Score
- Threshold: μ + 2σ
- Per-appliance calculation
- Captures unusual consumption spikes

**Output:**
- Timestamp of anomaly
- Appliance name
- Actual consumption
- Threshold value
- Z-score

### GenAI Insights

**Energy Insights Assistant:**
- Analyzes consumption patterns
- Identifies peak usage times
- Provides behavioral recommendations
- Estimates cost-saving opportunities

**Virtual Energy Auditor:**
- Identifies highest consumers
- Calculates percentage share
- Recommends energy-efficient upgrades
- Estimates savings potential

**AI Providers:**
1. OpenAI GPT-3.5-turbo (if API key provided)
2. AWS Bedrock Claude 3 Sonnet (if enabled)
3. Rule-based fallback (always available)

## Data Generation

**Synthetic Dataset:**
- Duration: 30 days
- Frequency: Hourly
- Appliances: AC, Refrigerator, Heater, Washing Machine

**Consumption Patterns:**
- Base consumption per appliance
- Peak hours: 6 PM - 9 PM (1.5-2x multiplier)
- Night hours: 10 PM - 6 AM (0.3-0.5x multiplier)
- Random noise: Normal distribution
- Anomalies: 5% probability, 2-3.5x spike

## Deployment

**Prerequisites:**
- AWS CLI configured with credentials
- Python 3.9+
- boto3 installed

**Deployment Steps:**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Deploy infrastructure
python infrastructure/deploy.py

# 3. Generate data
python data/generate_data.py

# 4. Upload data (triggers pipeline)
python scripts/upload_data.py data/output/energy_data.csv

# 5. Check results
python scripts/check_results.py
```

## Scalability Considerations

**Current Limits:**
- Lambda: 15-minute timeout, 3 GB memory
- S3: Unlimited storage
- Athena: Concurrent query limit (default: 20)

**Scaling Options:**
1. **Larger Datasets:**
   - Use AWS Glue for PySpark processing
   - Partition S3 data by date
   - Use Parquet format for better performance

2. **Real-time Processing:**
   - Add Kinesis Data Streams
   - Use Lambda for stream processing
   - Store in DynamoDB for low-latency access

3. **Advanced ML:**
   - SageMaker for model training
   - Batch Transform for large-scale inference
   - Model registry for versioning

## Cost Optimization

**Estimated Monthly Costs (100 uploads/month):**
- S3 Storage: $0.50 (20 GB)
- Lambda: $2.00 (100 invocations × 30s avg)
- Athena: $1.00 (20 GB scanned)
- **Total: ~$3.50/month**

**Optimization Tips:**
- Use S3 Lifecycle policies for old data
- Compress CSV files (gzip)
- Use Parquet for Athena queries
- Set Lambda memory appropriately
- Use S3 Intelligent-Tiering

## Troubleshooting

**Common Issues:**

1. **Lambda Timeout**
   - Increase timeout in config.py
   - Optimize data processing
   - Consider AWS Glue for large files

2. **IAM Permission Errors**
   - Verify role policies
   - Check S3 bucket permissions
   - Wait for IAM propagation (10-15 seconds)

3. **S3 Trigger Not Working**
   - Verify notification configuration
   - Check Lambda permissions
   - Ensure file uploaded to raw/ folder

4. **Athena Query Failures**
   - Verify table schemas
   - Check S3 data format
   - Ensure proper CSV headers

## Future Enhancements

1. **Real-time Dashboard**
   - QuickSight integration
   - Live consumption monitoring
   - Interactive forecasts

2. **Advanced Analytics**
   - Seasonal decomposition
   - Multi-variate forecasting
   - Cost optimization algorithms

3. **Alerting System**
   - SNS notifications for anomalies
   - Email reports
   - Slack integration

4. **API Layer**
   - API Gateway + Lambda
   - RESTful endpoints
   - Authentication with Cognito

5. **Mobile App**
   - React Native app
   - Push notifications
   - Real-time insights
