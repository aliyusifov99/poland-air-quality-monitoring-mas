"""
Health Advisor Agent

This agent adds health recommendations based on air quality categories.
It's the FOURTH agent in our pipeline.

Job: Receive classified data → Add health advice → Pass to next agent
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import pandas as pd
from agents.base_agent import BaseAgent
from config.aqi_standards import HEALTH_RECOMMENDATIONS


class HealthAdvisorAgent(BaseAgent):
    """
    Agent responsible for generating health recommendations.
    """
    
    def __init__(self):
        super().__init__()
    
    def get_name(self):
        return "HealthAdvisorAgent"
    
    def get_recommendation(self, category_key):
        """
        Get health recommendation for a given AQI category.
        
        Args:
            category_key: AQI category key (e.g., 'good', 'moderate')
            
        Returns:
            Dictionary with 'general' and 'sensitive' advice
        """
        recommendations = HEALTH_RECOMMENDATIONS.get(category_key, {})
        
        return {
            "general": recommendations.get("general_en", "No data available"),
            "sensitive": recommendations.get("sensitive_en", "No data available"),
        }
    
    def get_activity_emoji(self, category_key):
        """
        Get an emoji representing recommended activity level.
        
        Args:
            category_key: AQI category key
            
        Returns:
            Emoji string
        """
        emoji_map = {
            "very_good": "🏃‍♂️",  # Running - all outdoor activities OK
            "good": "🏃‍♂️",       # Running - all outdoor activities OK
            "moderate": "🚶",      # Walking - light activities
            "sufficient": "🏠",    # House - stay inside preferred
            "bad": "⚠️",          # Warning - avoid outdoors
            "very_bad": "🚫",      # No entry - stay indoors
        }
        return emoji_map.get(category_key, "❓")
    
    def category_name_to_key(self, category_name):
        """
        Convert category name to key.
        Handles both English and Polish names.
        
        Args:
            category_name: e.g., "Very Good", "Moderate", "Bardzo dobry"
            
        Returns:
            Category key: e.g., "very_good", "moderate"
        """
        mapping = {
            # English names
            "Very Good": "very_good",
            "Good": "good",
            "Moderate": "moderate",
            "Sufficient": "sufficient",
            "Bad": "bad",
            "Very Bad": "very_bad",
            # Polish names (from GIOŚ API)
            "Bardzo dobry": "very_good",
            "Dobry": "good",
            "Umiarkowany": "moderate",
            "Dostateczny": "sufficient",
            "Zły": "bad",
            "Bardzo zły": "very_bad",
        }
        return mapping.get(category_name, "moderate")
    
    def add_recommendations(self, city_summary):
        """
        Add health recommendations to city summary DataFrame.
        
        Args:
            city_summary: DataFrame with city AQI info
            
        Returns:
            DataFrame with added recommendation columns
        """
        if city_summary.empty:
            return city_summary
        
        df = city_summary.copy()
        
        # Add recommendations for each city
        general_advice = []
        sensitive_advice = []
        emojis = []
        
        for _, row in df.iterrows():
            category_name = row['overall_category']
            category_key = self.category_name_to_key(category_name)
            
            rec = self.get_recommendation(category_key)
            general_advice.append(rec['general'])
            sensitive_advice.append(rec['sensitive'])
            emojis.append(self.get_activity_emoji(category_key))
        
        df['health_advice'] = general_advice
        df['sensitive_advice'] = sensitive_advice
        df['emoji'] = emojis
        
        return df
    
    def generate_report(self, city_summary):
        """
        Generate a text summary report.
        
        Args:
            city_summary: DataFrame with recommendations
            
        Returns:
            Formatted string report
        """
        lines = []
        lines.append("=" * 50)
        lines.append("AIR QUALITY REPORT")
        lines.append("=" * 50)
        lines.append("")
        
        for _, row in city_summary.iterrows():
            lines.append(f"📍 {row['city']}")
            lines.append(f"   Status: {row['overall_category']} {row['emoji']}")
            lines.append(f"   Main concern: {row['dominant_pollutant']} ({row['dominant_value']:.1f} µg/m³)")
            lines.append(f"   💡 {row['health_advice']}")
            lines.append("")
        
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    def process(self, input_message=None):
        """
        Main processing method.
        
        Args:
            input_message: Message from QualityClassifierAgent
            
        Returns:
            Message containing data with health recommendations
        """
        # Check input
        if input_message is None:
            self.log("ERROR: No input message received")
            return self.create_message(data=None, status="error")
        
        if input_message.status != "success":
            self.log("ERROR: Previous agent failed")
            return self.create_message(data=None, status="error")
        
        classified_data = input_message.data
        self.log(f"Adding recommendations to data from {input_message.sender}")
        
        # Get city summary
        city_summary = classified_data.get("city_summary", pd.DataFrame())
        
        # Add recommendations
        self.log("Adding health recommendations...")
        city_with_advice = self.add_recommendations(city_summary)
        
        # Generate report
        self.log("Generating report...")
        report = self.generate_report(city_with_advice)
        
        # Package results
        final_data = {
            "measurements": classified_data.get("measurements", pd.DataFrame()),
            "city_summary": city_with_advice,
            "report": report,
            "raw_data": classified_data.get("raw_data", {}),
        }
        
        return self.create_message(data=final_data, status="success")


# Test the agent
if __name__ == "__main__":
    print("Testing Health Advisor Agent...")
    print("=" * 50)
    
    # Get data from previous agents
    from collector_agent import DataCollectorAgent
    from processor_agent import DataProcessorAgent
    from classifier_agent import QualityClassifierAgent
    
    collector = DataCollectorAgent()
    raw_message = collector.run()
    
    print()
    
    processor = DataProcessorAgent()
    processed_message = processor.run(raw_message)
    
    print()
    
    classifier = QualityClassifierAgent()
    classified_message = classifier.run(processed_message)
    
    print()
    
    # Now add health advice
    advisor = HealthAdvisorAgent()
    advised_message = advisor.run(classified_message)
    
    print(f"\nStatus: {advised_message.status}")
    
    if advised_message.status == "success":
        data = advised_message.data
        
        print("\n--- City Summary with Recommendations ---")
        cols = ['city', 'overall_category', 'emoji', 'health_advice']
        print(data["city_summary"][cols].to_string(index=False))
        
        print("\n" + data["report"])