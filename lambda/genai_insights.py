"""GenAI modules for energy insights and recommendations"""
import json
import os

class EnergyInsightsAssistant:
    def __init__(self, use_bedrock=False):
        self.use_bedrock = use_bedrock
        self.openai_api_key = os.environ.get('OPENAI_API_KEY', '')
    
    def generate_insights(self, analytics_data):
        """Generate professional energy insights summary"""
        total_usage = analytics_data.get('total_usage', 0)
        peak_hours = analytics_data.get('peak_hours', [])
        anomaly_count = analytics_data.get('anomaly_count', 0)
        appliance_stats = analytics_data.get('appliance_stats', [])
        forecast_summary = analytics_data.get('forecast_summary', {})
        
        # Build context for AI
        context = self._build_context(
            total_usage, peak_hours, anomaly_count, 
            appliance_stats, forecast_summary
        )
        
        # Generate insights using available AI service
        if self.openai_api_key:
            insights = self._generate_with_openai(context)
        elif self.use_bedrock:
            insights = self._generate_with_bedrock(context)
        else:
            insights = self._generate_rule_based(context)
        
        return insights
    
    def _build_context(self, total_usage, peak_hours, anomaly_count, appliance_stats, forecast_summary):
        """Build context string for AI"""
        context = f"""
Energy Usage Analysis Summary:

Total Consumption: {total_usage:.2f} kWh over 30 days
Daily Average: {total_usage/30:.2f} kWh
Anomalies Detected: {anomaly_count}

Peak Consumption Hours:
"""
        for i, hour_data in enumerate(peak_hours[:3], 1):
            context += f"{i}. Hour {hour_data.get('hour', 'N/A')}: {hour_data.get('total_kwh', 0):.2f} kWh\n"
        
        context += "\nAppliance Breakdown:\n"
        for stat in appliance_stats:
            context += f"- {stat.get('appliance', 'Unknown')}: {stat.get('total_kwh', 0):.2f} kWh (Avg: {stat.get('avg_kwh', 0):.3f} kWh/hour)\n"
        
        if forecast_summary:
            context += f"\n7-Day Forecast:\n"
            context += f"Predicted Total: {forecast_summary.get('total_predicted_kwh', 0):.2f} kWh\n"
            context += f"Daily Average: {forecast_summary.get('avg_predicted_kwh', 0):.2f} kWh\n"
        
        return context
    
    def _generate_with_openai(self, context):
        """Generate insights using OpenAI API"""
        try:
            import openai
            openai.api_key = self.openai_api_key
            
            prompt = f"""Based on the following energy usage data, provide a professional summary with behavioral recommendations:

{context}

Provide:
1. Key insights about consumption patterns
2. Behavioral recommendations to reduce energy usage
3. Cost-saving opportunities
"""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an energy efficiency expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return self._generate_rule_based(context)
    
    def _generate_with_bedrock(self, context):
        """Generate insights using AWS Bedrock"""
        try:
            import boto3
            
            bedrock = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
            
            prompt = f"""Based on the following energy usage data, provide a professional summary with behavioral recommendations:

{context}

Provide:
1. Key insights about consumption patterns
2. Behavioral recommendations to reduce energy usage
3. Cost-saving opportunities
"""
            
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
            
            response = bedrock.invoke_model(
                modelId='anthropic.claude-3-sonnet-20240229-v1:0',
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            return self._generate_rule_based(context)
    
    def _generate_rule_based(self, context):
        """Generate insights using rule-based approach"""
        insights = f"""
ENERGY USAGE INSIGHTS REPORT
{'='*50}

{context}

KEY INSIGHTS:
• Your energy consumption shows typical residential patterns with peak usage during evening hours
• Anomalies detected suggest occasional high-consumption events that warrant investigation
• Consistent monitoring can help identify opportunities for optimization

BEHAVIORAL RECOMMENDATIONS:
1. Shift high-energy activities away from peak hours (6 PM - 9 PM) when possible
2. Review anomalous consumption events to identify and eliminate energy waste
3. Consider implementing smart scheduling for major appliances
4. Maintain regular appliance maintenance to ensure optimal efficiency
5. Monitor standby power consumption and use power strips to eliminate phantom loads

COST-SAVING OPPORTUNITIES:
• Optimize thermostat settings during peak and off-peak hours
• Utilize natural lighting and ventilation when weather permits
• Consider time-of-use electricity plans if available in your area
• Implement energy-efficient practices during high-consumption periods
"""
        return insights


class VirtualEnergyAuditor:
    def __init__(self):
        pass
    
    def generate_audit_report(self, appliance_stats):
        """Generate appliance upgrade recommendations"""
        if not appliance_stats:
            return "No appliance data available for audit."
        
        # Find highest consuming appliance
        highest = max(appliance_stats, key=lambda x: x.get('total_kwh', 0))
        
        total_consumption = sum(stat.get('total_kwh', 0) for stat in appliance_stats)
        
        report = f"""
VIRTUAL ENERGY AUDITOR REPORT
{'='*50}

CONSUMPTION ANALYSIS:
Total Energy Consumption: {total_consumption:.2f} kWh (30 days)

Appliance Breakdown:
"""
        
        for stat in sorted(appliance_stats, key=lambda x: x.get('total_kwh', 0), reverse=True):
            appliance = stat.get('appliance', 'Unknown')
            total = stat.get('total_kwh', 0)
            percentage = (total / total_consumption * 100) if total_consumption > 0 else 0
            peak_hour = stat.get('peak_hour', 'N/A')
            
            report += f"\n{appliance}:\n"
            report += f"  • Consumption: {total:.2f} kWh ({percentage:.1f}% of total)\n"
            report += f"  • Peak Usage: Hour {peak_hour}\n"
        
        report += f"\n\nHIGHEST CONSUMER: {highest.get('appliance', 'Unknown')}\n"
        report += f"Accounts for {(highest.get('total_kwh', 0)/total_consumption*100):.1f}% of total consumption\n"
        
        report += "\n\nUPGRADE RECOMMENDATIONS:\n"
        report += self._get_recommendations(highest.get('appliance', ''))
        
        report += "\n\nESTIMATED SAVINGS:\n"
        report += "• Upgrading to energy-efficient appliances: 20-40% reduction\n"
        report += "• Smart thermostat installation: 10-15% reduction on HVAC\n"
        report += "• LED lighting conversion: 75% reduction on lighting costs\n"
        report += f"• Potential annual savings: ${(total_consumption * 0.12 * 0.25 * 12):.2f} (estimated)\n"
        
        return report
    
    def _get_recommendations(self, appliance):
        """Get specific recommendations for appliance"""
        recommendations = {
            'AC': """
1. Inverter AC Upgrade (5-Star Rated)
   • Energy savings: 30-40% compared to conventional AC
   • Features: Variable speed compressor, smart temperature control
   • ROI: 2-3 years

2. Smart Thermostat Integration
   • Automated temperature scheduling
   • Remote control and monitoring
   • Learning algorithms for optimal efficiency

3. Maintenance Tips
   • Clean filters monthly
   • Annual professional servicing
   • Seal room properly to prevent cool air loss
""",
            'Refrigerator': """
1. Energy Star Certified Refrigerator
   • 15-20% more efficient than standard models
   • Features: Improved insulation, efficient compressors
   • ROI: 5-7 years

2. Optimization Tips
   • Set temperature to 37-40°F (3-4°C)
   • Keep coils clean
   • Ensure door seals are tight
   • Avoid placing near heat sources
""",
            'Heater': """
1. Energy-Efficient Space Heater
   • Ceramic or infrared heaters with thermostats
   • 25-30% more efficient than traditional heaters
   • Features: Auto shut-off, programmable timers

2. Insulation Improvements
   • Seal windows and doors
   • Add weatherstripping
   • Consider smart heating zones

3. Alternative Solutions
   • Heat pump systems (3x more efficient)
   • Radiant floor heating for specific areas
""",
            'Washing Machine': """
1. Front-Load Energy Star Washer
   • Uses 25% less energy and 33% less water
   • Features: High-efficiency motors, advanced wash cycles
   • ROI: 3-5 years

2. Usage Optimization
   • Use cold water when possible (90% energy savings per load)
   • Run full loads only
   • Use high-speed spin to reduce dryer time
   • Consider air-drying when feasible
"""
        }
        
        return recommendations.get(appliance, """
General Recommendations:
• Look for Energy Star certified replacements
• Consider smart appliances with energy monitoring
• Implement usage scheduling during off-peak hours
• Regular maintenance to ensure optimal performance
""")
