"""Data processing module for energy analytics"""
import pandas as pd
import numpy as np
from io import StringIO

class EnergyDataProcessor:
    def __init__(self, anomaly_threshold_sigma=2):
        self.anomaly_threshold_sigma = anomaly_threshold_sigma
    
    def process_data(self, csv_content):
        """Process raw energy data"""
        # Read CSV
        df = pd.read_csv(StringIO(csv_content))
        
        # Parse timestamps
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['date'] = df['timestamp'].dt.date
        
        # Aggregate by appliance
        appliance_stats = self._aggregate_by_appliance(df)
        
        # Detect anomalies
        anomalies = self._detect_anomalies(df)
        
        # Peak analysis
        peak_hours = self._analyze_peak_hours(df)
        
        return {
            'appliance_stats': appliance_stats,
            'anomalies': anomalies,
            'peak_hours': peak_hours,
            'processed_df': df
        }
    
    def _aggregate_by_appliance(self, df):
        """Aggregate consumption by appliance"""
        agg_df = df.groupby('appliance').agg({
            'kwh': ['sum', 'mean', 'std', 'count']
        }).reset_index()
        
        agg_df.columns = ['appliance', 'total_kwh', 'avg_kwh', 'std_kwh', 'count']
        
        # Find peak hour for each appliance
        peak_hours = df.groupby('appliance').apply(
            lambda x: x.groupby('hour')['kwh'].mean().idxmax()
        ).reset_index()
        peak_hours.columns = ['appliance', 'peak_hour']
        
        result = agg_df.merge(peak_hours, on='appliance')
        return result
    
    def _detect_anomalies(self, df):
        """Detect anomalies using Z-score method"""
        anomalies = []
        
        for appliance in df['appliance'].unique():
            appliance_data = df[df['appliance'] == appliance].copy()
            
            mean = appliance_data['kwh'].mean()
            std = appliance_data['kwh'].std()
            threshold = mean + (self.anomaly_threshold_sigma * std)
            
            anomaly_records = appliance_data[appliance_data['kwh'] > threshold]
            
            for _, row in anomaly_records.iterrows():
                anomalies.append({
                    'timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'appliance': row['appliance'],
                    'kwh': row['kwh'],
                    'threshold': threshold,
                    'z_score': (row['kwh'] - mean) / std if std > 0 else 0
                })
        
        return pd.DataFrame(anomalies)
    
    def _analyze_peak_hours(self, df):
        """Analyze peak consumption hours"""
        hourly_consumption = df.groupby('hour')['kwh'].sum().reset_index()
        hourly_consumption.columns = ['hour', 'total_kwh']
        hourly_consumption = hourly_consumption.sort_values('total_kwh', ascending=False)
        
        return hourly_consumption
    
    def prepare_for_forecast(self, df):
        """Prepare daily aggregated data for Prophet"""
        daily_df = df.groupby('date')['kwh'].sum().reset_index()
        daily_df.columns = ['ds', 'y']
        daily_df['ds'] = pd.to_datetime(daily_df['ds'])
        
        return daily_df
