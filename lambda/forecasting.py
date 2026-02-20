"""Time-series forecasting using Prophet"""
import pandas as pd
import json
from io import StringIO

class EnergyForecaster:
    def __init__(self, forecast_days=7):
        self.forecast_days = forecast_days
    
    def forecast(self, daily_df):
        """Generate forecast using Prophet"""
        try:
            from prophet import Prophet
            
            # Initialize Prophet model
            model = Prophet(
                daily_seasonality=False,
                weekly_seasonality=True,
                yearly_seasonality=False,
                changepoint_prior_scale=0.05
            )
            
            # Fit model
            model.fit(daily_df)
            
            # Create future dataframe
            future = model.make_future_dataframe(periods=self.forecast_days)
            
            # Generate forecast
            forecast = model.predict(future)
            
            # Extract relevant columns
            forecast_result = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(self.forecast_days)
            
            return forecast_result
            
        except ImportError:
            # Fallback: Simple moving average forecast
            return self._simple_forecast(daily_df)
    
    def _simple_forecast(self, daily_df):
        """Simple moving average forecast as fallback"""
        # Calculate 7-day moving average
        window = min(7, len(daily_df))
        avg = daily_df['y'].tail(window).mean()
        std = daily_df['y'].tail(window).std()
        
        # Generate future dates
        last_date = daily_df['ds'].max()
        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=self.forecast_days,
            freq='D'
        )
        
        # Create forecast
        forecast_df = pd.DataFrame({
            'ds': future_dates,
            'yhat': [avg] * self.forecast_days,
            'yhat_lower': [avg - 2*std] * self.forecast_days,
            'yhat_upper': [avg + 2*std] * self.forecast_days
        })
        
        return forecast_df
    
    def format_forecast_summary(self, forecast_df):
        """Format forecast summary for reporting"""
        summary = {
            'forecast_period': f"{self.forecast_days} days",
            'start_date': forecast_df['ds'].min().strftime('%Y-%m-%d'),
            'end_date': forecast_df['ds'].max().strftime('%Y-%m-%d'),
            'avg_predicted_kwh': float(forecast_df['yhat'].mean()),
            'total_predicted_kwh': float(forecast_df['yhat'].sum()),
            'daily_predictions': []
        }
        
        for _, row in forecast_df.iterrows():
            summary['daily_predictions'].append({
                'date': row['ds'].strftime('%Y-%m-%d'),
                'predicted_kwh': float(row['yhat']),
                'lower_bound': float(row['yhat_lower']),
                'upper_bound': float(row['yhat_upper'])
            })
        
        return summary
