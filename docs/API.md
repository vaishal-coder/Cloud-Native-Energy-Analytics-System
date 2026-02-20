# API Documentation

## Overview

The Energy Analytics System can be extended with an API layer using AWS API Gateway. This document describes the potential API endpoints and integration patterns.

## Future API Endpoints

### 1. Upload Data

```http
POST /api/v1/upload
Content-Type: multipart/form-data

{
  "file": <CSV file>
}
```

**Response**:
```json
{
  "status": "success",
  "upload_id": "uuid",
  "s3_key": "raw/energy_data_timestamp.csv",
  "message": "File uploaded successfully"
}
```

### 2. Get Processing Status

```http
GET /api/v1/status/{upload_id}
```

**Response**:
```json
{
  "upload_id": "uuid",
  "status": "completed",
  "processing_time_ms": 225,
  "records_processed": 2880,
  "anomalies_detected": 49
}
```

### 3. Get Results

```http
GET /api/v1/results/{upload_id}
```

**Response**:
```json
{
  "upload_id": "uuid",
  "summary": {
    "total_consumption": 3344.43,
    "daily_average": 111.48,
    "anomalies_count": 49
  },
  "forecast": [
    {"date": "2026-02-21", "predicted_kwh": 111.48},
    {"date": "2026-02-22", "predicted_kwh": 111.48}
  ],
  "anomalies": [
    {"timestamp": "2026-01-15 14:30", "appliance": "AC", "value": 13.44}
  ]
}
```

### 4. Query Historical Data

```http
GET /api/v1/analytics?start_date=2026-01-01&end_date=2026-01-31
```

**Response**:
```json
{
  "period": {
    "start": "2026-01-01",
    "end": "2026-01-31"
  },
  "total_consumption": 3344.43,
  "by_appliance": {
    "AC": 1655.36,
    "Heater": 1237.47,
    "Refrigerator": 112.75,
    "Washing Machine": 338.85
  }
}
```

### 5. Get Forecast

```http
GET /api/v1/forecast?days=7
```

**Response**:
```json
{
  "forecast_days": 7,
  "predictions": [
    {
      "date": "2026-02-21",
      "predicted_kwh": 111.48,
      "confidence_lower": 89.18,
      "confidence_upper": 133.78
    }
  ]
}
```

## Integration with Flutter App

### Authentication

```dart
// Using AWS Cognito
final cognitoUser = await Amplify.Auth.signIn(
  username: username,
  password: password,
);
```

### Upload Data

```dart
import 'package:http/http.dart' as http;

Future<void> uploadEnergyData(File csvFile) async {
  var request = http.MultipartRequest(
    'POST',
    Uri.parse('https://api.example.com/api/v1/upload'),
  );
  
  request.files.add(
    await http.MultipartFile.fromPath('file', csvFile.path),
  );
  
  var response = await request.send();
  var responseData = await response.stream.bytesToString();
  
  print('Upload response: $responseData');
}
```

### Fetch Results

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

Future<Map<String, dynamic>> getResults(String uploadId) async {
  final response = await http.get(
    Uri.parse('https://api.example.com/api/v1/results/$uploadId'),
  );
  
  if (response.statusCode == 200) {
    return json.decode(response.body);
  } else {
    throw Exception('Failed to load results');
  }
}
```

## Implementation with API Gateway

### Lambda Integration

```python
# API Gateway Lambda handler
def api_handler(event, context):
    http_method = event['httpMethod']
    path = event['path']
    
    if http_method == 'POST' and path == '/upload':
        return handle_upload(event)
    elif http_method == 'GET' and path.startswith('/results'):
        return handle_get_results(event)
    
    return {
        'statusCode': 404,
        'body': json.dumps({'error': 'Not found'})
    }
```

### CORS Configuration

```python
def add_cors_headers(response):
    response['headers'] = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
    }
    return response
```

## WebSocket Support (Real-time Updates)

```dart
import 'package:web_socket_channel/web_socket_channel.dart';

final channel = WebSocketChannel.connect(
  Uri.parse('wss://api.example.com/ws'),
);

channel.stream.listen((message) {
  print('Processing update: $message');
});
```

## Rate Limiting

- 100 requests per minute per user
- 1000 requests per hour per user
- Burst capacity: 200 requests

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

## SDK Examples

### Python SDK

```python
import requests

class EnergyAnalyticsClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.example.com/api/v1"
    
    def upload_data(self, file_path):
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{self.base_url}/upload",
                files=files,
                headers={'Authorization': f'Bearer {self.api_key}'}
            )
        return response.json()
    
    def get_results(self, upload_id):
        response = requests.get(
            f"{self.base_url}/results/{upload_id}",
            headers={'Authorization': f'Bearer {self.api_key}'}
        )
        return response.json()
```

### JavaScript SDK

```javascript
class EnergyAnalyticsClient {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseUrl = 'https://api.example.com/api/v1';
  }
  
  async uploadData(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${this.baseUrl}/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: formData
    });
    
    return await response.json();
  }
  
  async getResults(uploadId) {
    const response = await fetch(`${this.baseUrl}/results/${uploadId}`, {
      headers: {
        'Authorization': `Bearer ${this.apiKey}`
      }
    });
    
    return await response.json();
  }
}
```

## Next Steps

To implement the API layer:

1. Create API Gateway REST API
2. Configure Lambda integration
3. Set up Cognito for authentication
4. Implement rate limiting
5. Add CloudWatch monitoring
6. Create API documentation with Swagger/OpenAPI

