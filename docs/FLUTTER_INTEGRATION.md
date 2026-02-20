# Flutter Mobile App Integration

## Overview

This document outlines the plan to build a Flutter mobile application for the Energy Analytics System, providing real-time monitoring and insights on mobile devices.

## Proposed Features

### 1. Dashboard
- Real-time energy consumption metrics
- Daily/weekly/monthly trends
- Cost analysis
- Anomaly alerts

### 2. Data Upload
- Camera-based CSV upload
- File picker integration
- Drag-and-drop support
- Upload progress tracking

### 3. Analytics
- Interactive charts (consumption over time)
- Appliance breakdown (pie charts)
- Forecast visualization
- Anomaly timeline

### 4. Notifications
- Push notifications for anomalies
- Daily/weekly reports
- Cost threshold alerts
- Forecast updates

### 5. Settings
- AWS credentials configuration
- Notification preferences
- Data refresh intervals
- Theme customization

## Architecture

```
┌─────────────────┐
│  Flutter App    │
│  (Mobile/Web)   │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  API Gateway    │
│  (REST API)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Lambda         │
│  (API Handler)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  S3 + Athena    │
│  (Data Layer)   │
└─────────────────┘
```

## Tech Stack

### Frontend
- **Framework**: Flutter 3.x
- **State Management**: Provider / Riverpod
- **Charts**: fl_chart
- **HTTP**: dio
- **Storage**: shared_preferences / hive
- **Auth**: AWS Amplify Flutter

### Backend (New Components)
- **API Gateway**: REST API endpoints
- **Lambda**: API request handlers
- **Cognito**: User authentication
- **DynamoDB**: User preferences (optional)

## Project Structure

```
energy_analytics_app/
├── lib/
│   ├── main.dart
│   ├── models/
│   │   ├── energy_data.dart
│   │   ├── forecast.dart
│   │   └── anomaly.dart
│   ├── services/
│   │   ├── api_service.dart
│   │   ├── auth_service.dart
│   │   └── storage_service.dart
│   ├── providers/
│   │   ├── energy_provider.dart
│   │   └── auth_provider.dart
│   ├── screens/
│   │   ├── dashboard_screen.dart
│   │   ├── upload_screen.dart
│   │   ├── analytics_screen.dart
│   │   ├── settings_screen.dart
│   │   └── login_screen.dart
│   └── widgets/
│       ├── energy_chart.dart
│       ├── anomaly_card.dart
│       └── forecast_widget.dart
├── assets/
│   └── images/
├── pubspec.yaml
└── README.md
```

## Implementation Plan

### Phase 1: Backend API (Week 1-2)

1. **Create API Gateway**
   ```bash
   # Create REST API
   aws apigateway create-rest-api --name energy-analytics-api
   ```

2. **Lambda API Handlers**
   - `GET /api/v1/data` - Fetch energy data
   - `POST /api/v1/upload` - Upload CSV
   - `GET /api/v1/forecast` - Get predictions
   - `GET /api/v1/anomalies` - Get anomalies

3. **Authentication**
   - Set up AWS Cognito user pool
   - Configure API Gateway authorizer
   - Implement JWT token validation

### Phase 2: Flutter App Setup (Week 3)

1. **Initialize Flutter Project**
   ```bash
   flutter create energy_analytics_app
   cd energy_analytics_app
   ```

2. **Add Dependencies**
   ```yaml
   dependencies:
     flutter:
       sdk: flutter
     dio: ^5.0.0
     provider: ^6.0.0
     fl_chart: ^0.60.0
     shared_preferences: ^2.0.0
     file_picker: ^5.0.0
     image_picker: ^0.8.0
     amplify_flutter: ^1.0.0
     amplify_auth_cognito: ^1.0.0
   ```

3. **Configure AWS Amplify**
   ```dart
   await Amplify.addPlugins([
     AmplifyAuthCognito(),
   ]);
   await Amplify.configure(amplifyconfig);
   ```

### Phase 3: Core Features (Week 4-5)

1. **Authentication Screen**
   ```dart
   class LoginScreen extends StatelessWidget {
     Future<void> signIn(String username, String password) async {
       try {
         await Amplify.Auth.signIn(
           username: username,
           password: password,
         );
       } catch (e) {
         print('Sign in failed: $e');
       }
     }
   }
   ```

2. **Dashboard Screen**
   ```dart
   class DashboardScreen extends StatelessWidget {
     @override
     Widget build(BuildContext context) {
       return Scaffold(
         appBar: AppBar(title: Text('Energy Analytics')),
         body: Column(
           children: [
             EnergyMetricsCard(),
             ConsumptionChart(),
             AnomalyList(),
           ],
         ),
       );
     }
   }
   ```

3. **API Service**
   ```dart
   class ApiService {
     final Dio _dio = Dio();
     final String baseUrl = 'https://api.example.com/api/v1';
     
     Future<EnergyData> fetchEnergyData() async {
       final response = await _dio.get('$baseUrl/data');
       return EnergyData.fromJson(response.data);
     }
     
     Future<void> uploadFile(File file) async {
       FormData formData = FormData.fromMap({
         'file': await MultipartFile.fromFile(file.path),
       });
       await _dio.post('$baseUrl/upload', data: formData);
     }
   }
   ```

### Phase 4: Charts & Visualization (Week 6)

1. **Consumption Chart**
   ```dart
   class ConsumptionChart extends StatelessWidget {
     @override
     Widget build(BuildContext context) {
       return LineChart(
         LineChartData(
           lineBarsData: [
             LineChartBarData(
               spots: energyData.map((e) => 
                 FlSpot(e.timestamp, e.consumption)
               ).toList(),
             ),
           ],
         ),
       );
     }
   }
   ```

2. **Appliance Breakdown**
   ```dart
   class AppliancePieChart extends StatelessWidget {
     @override
     Widget build(BuildContext context) {
       return PieChart(
         PieChartData(
           sections: [
             PieChartSectionData(
               value: acConsumption,
               title: 'AC',
               color: Colors.blue,
             ),
             // More sections...
           ],
         ),
       );
     }
   }
   ```

### Phase 5: Notifications (Week 7)

1. **Push Notifications**
   ```dart
   import 'package:firebase_messaging/firebase_messaging.dart';
   
   class NotificationService {
     final FirebaseMessaging _fcm = FirebaseMessaging.instance;
     
     Future<void> initialize() async {
       await _fcm.requestPermission();
       String? token = await _fcm.getToken();
       print('FCM Token: $token');
     }
   }
   ```

2. **SNS Integration**
   - Configure SNS topic for anomalies
   - Lambda function to send notifications
   - Mobile app subscribes to topics

### Phase 6: Testing & Deployment (Week 8)

1. **Unit Tests**
   ```dart
   test('API service fetches data', () async {
     final service = ApiService();
     final data = await service.fetchEnergyData();
     expect(data, isNotNull);
   });
   ```

2. **Build & Deploy**
   ```bash
   # Android
   flutter build apk --release
   
   # iOS
   flutter build ios --release
   
   # Web
   flutter build web
   ```

## Sample Code Snippets

### Energy Data Model

```dart
class EnergyData {
  final String timestamp;
  final double consumption;
  final String appliance;
  
  EnergyData({
    required this.timestamp,
    required this.consumption,
    required this.appliance,
  });
  
  factory EnergyData.fromJson(Map<String, dynamic> json) {
    return EnergyData(
      timestamp: json['timestamp'],
      consumption: json['consumption'].toDouble(),
      appliance: json['appliance'],
    );
  }
}
```

### Energy Provider

```dart
class EnergyProvider extends ChangeNotifier {
  List<EnergyData> _data = [];
  bool _isLoading = false;
  
  List<EnergyData> get data => _data;
  bool get isLoading => _isLoading;
  
  Future<void> fetchData() async {
    _isLoading = true;
    notifyListeners();
    
    try {
      _data = await ApiService().fetchEnergyData();
    } catch (e) {
      print('Error: $e');
    }
    
    _isLoading = false;
    notifyListeners();
  }
}
```

### Dashboard Widget

```dart
class DashboardScreen extends StatefulWidget {
  @override
  _DashboardScreenState createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    Provider.of<EnergyProvider>(context, listen: false).fetchData();
  }
  
  @override
  Widget build(BuildContext context) {
    return Consumer<EnergyProvider>(
      builder: (context, provider, child) {
        if (provider.isLoading) {
          return Center(child: CircularProgressIndicator());
        }
        
        return ListView(
          children: [
            MetricsCard(data: provider.data),
            ConsumptionChart(data: provider.data),
            AnomalyList(data: provider.data),
          ],
        );
      },
    );
  }
}
```

## Cost Estimation

### Additional AWS Costs

| Service | Monthly Cost |
|---------|--------------|
| API Gateway | ~$3.50 (1M requests) |
| Cognito | Free (< 50K users) |
| Lambda (API) | ~$0.20 |
| DynamoDB | ~$1.25 (optional) |
| **Total** | **~$5** |

**Combined System Cost**: ~$9/month

## Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1 | 2 weeks | Backend API ready |
| Phase 2 | 1 week | Flutter app setup |
| Phase 3 | 2 weeks | Core features |
| Phase 4 | 1 week | Charts & visualization |
| Phase 5 | 1 week | Notifications |
| Phase 6 | 1 week | Testing & deployment |
| **Total** | **8 weeks** | **Production app** |

## Next Steps

1. **Confirm Requirements**
   - Review proposed features
   - Prioritize must-have vs nice-to-have
   - Define target platforms (iOS, Android, Web)

2. **Setup Backend API**
   - Create API Gateway
   - Implement Lambda handlers
   - Configure Cognito

3. **Initialize Flutter Project**
   - Create project structure
   - Add dependencies
   - Setup state management

4. **Start Development**
   - Begin with Phase 1
   - Iterate based on feedback
   - Deploy incrementally

## Resources

- [Flutter Documentation](https://flutter.dev/docs)
- [AWS Amplify Flutter](https://docs.amplify.aws/lib/q/platform/flutter/)
- [fl_chart Package](https://pub.dev/packages/fl_chart)
- [Provider Package](https://pub.dev/packages/provider)

---

**Ready to start building the Flutter app?** Let me know and we can begin with Phase 1!
