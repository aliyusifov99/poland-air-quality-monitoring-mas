"""
Quality Classifier Agent

This agent classifies air quality based on Polish AQI standards.
It's the THIRD agent in our pipeline.

Job: Receive clean data → Apply AQI thresholds → Add categories → Pass to next agent
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import pandas as pd
from agents.base_agent import BaseAgent
from config.aqi_standards import AQI_CATEGORIES, AQI_THRESHOLDS


class QualityClassifierAgent(BaseAgent):
    """
    Agent responsible for classifying air quality measurements.
    """
    
    def __init__(self):
        super().__init__()
    
    def get_name(self):
        return "QualityClassifierAgent"
    
    def classify_value(self, parameter, value):
        """
        Classify a single pollutant value.
        
        Args:
            parameter: Pollutant code (PM2.5, PM10, etc.)
            value: Measured value in µg/m³
            
        Returns:
            Tuple of (category_key, category_name, level, color)
        """
        # Get thresholds for this parameter
        thresholds = AQI_THRESHOLDS.get(parameter)
        
        if thresholds is None:
            return ("unknown", "Unknown", -1, "#808080")
        
        # Find which category this value falls into
        for category_key, (min_val, max_val) in thresholds.items():
            if min_val <= value <= max_val:
                category_info = AQI_CATEGORIES.get(category_key, {})
                return (
                    category_key,
                    category_info.get("name_en", category_key),
                    category_info.get("level", -1),
                    category_info.get("color", "#808080")
                )
        
        # If value exceeds all thresholds, it's very bad
        return ("very_bad", "Very Bad", 5, "#990000")
    
    def classify_measurements(self, df):
        """
        Add classification columns to the measurements DataFrame.
        
        Args:
            df: DataFrame with measurements
            
        Returns:
            DataFrame with added columns: aqi_category, aqi_level, aqi_color
        """
        if df.empty:
            return df
        
        df_classified = df.copy()
        
        # Classify each row
        classifications = df_classified.apply(
            lambda row: self.classify_value(row['parameter_code'], row['value']),
            axis=1
        )
        
        # Add new columns
        df_classified['aqi_category_key'] = classifications.apply(lambda x: x[0])
        df_classified['aqi_category'] = classifications.apply(lambda x: x[1])
        df_classified['aqi_level'] = classifications.apply(lambda x: x[2])
        df_classified['aqi_color'] = classifications.apply(lambda x: x[3])
        
        return df_classified
    
    def get_city_summary(self, df):
        """
        Create a summary showing overall AQI for each city.
        
        The overall AQI is determined by the WORST pollutant.
        
        Args:
            df: Classified measurements DataFrame
            
        Returns:
            DataFrame with one row per city
        """
        if df.empty:
            return pd.DataFrame()
        
        # For each city, find the worst (highest level) measurement
        city_summary = []
        
        for city in df['city'].unique():
            city_data = df[df['city'] == city]
            
            # Find the row with highest aqi_level (worst air quality)
            worst_idx = city_data['aqi_level'].idxmax()
            worst_row = city_data.loc[worst_idx]
            
            city_summary.append({
                'city': city,
                'overall_category': worst_row['aqi_category'],
                'overall_level': worst_row['aqi_level'],
                'overall_color': worst_row['aqi_color'],
                'dominant_pollutant': worst_row['parameter_code'],
                'dominant_value': worst_row['value'],
                'stations_count': city_data['station_id'].nunique(),
            })
        
        return pd.DataFrame(city_summary)
    
    def process(self, input_message=None):
        """
        Main processing method.
        
        Args:
            input_message: Message from DataProcessorAgent
            
        Returns:
            Message containing classified data
        """
        # Check input
        if input_message is None:
            self.log("ERROR: No input message received")
            return self.create_message(data=None, status="error")
        
        if input_message.status != "success":
            self.log("ERROR: Previous agent failed")
            return self.create_message(data=None, status="error")
        
        processed_data = input_message.data
        self.log(f"Classifying data from {input_message.sender}")
        
        # Get measurements DataFrame
        measurements_df = processed_data.get("measurements", pd.DataFrame())
        
        # Classify measurements
        self.log("Applying AQI classifications...")
        classified_df = self.classify_measurements(measurements_df)
        
        # Create city summary
        self.log("Creating city summary...")
        city_summary = self.get_city_summary(classified_df)
        
        # Log results
        for _, row in city_summary.iterrows():
            self.log(f"  {row['city']}: {row['overall_category']} (worst: {row['dominant_pollutant']})")
        
        # Package results
        classified_data = {
            "measurements": classified_df,
            "city_summary": city_summary,
            "aqi": processed_data.get("aqi", pd.DataFrame()),
            "raw_data": processed_data.get("raw_data", {}),
        }
        
        return self.create_message(data=classified_data, status="success")


# Test the agent
if __name__ == "__main__":
    print("Testing Quality Classifier Agent...")
    print("=" * 50)
    
    # Get data from previous agents
    from collector_agent import DataCollectorAgent
    from processor_agent import DataProcessorAgent
    
    collector = DataCollectorAgent()
    raw_message = collector.run()
    
    print()
    
    processor = DataProcessorAgent()
    processed_message = processor.run(raw_message)
    
    print()
    
    # Now classify the data
    classifier = QualityClassifierAgent()
    classified_message = classifier.run(processed_message)
    
    print(f"\nStatus: {classified_message.status}")
    
    if classified_message.status == "success":
        data = classified_message.data
        
        print("\n--- Classified Measurements (sample) ---")
        cols = ['city', 'station_name', 'parameter_code', 'value', 'aqi_category', 'aqi_color']
        print(data["measurements"][cols].head(10).to_string(index=False))
        
        print("\n--- City Summary ---")
        print(data["city_summary"].to_string(index=False))
