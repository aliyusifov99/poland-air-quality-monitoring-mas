"""
Data Processor Agent

This agent cleans and structures the raw data from the Collector Agent.
It's the SECOND agent in our pipeline.

Job: Receive raw data → Clean it → Convert to DataFrame → Pass to next agent
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import pandas as pd
from agents.base_agent import BaseAgent

class DataProcessorAgent(BaseAgent):
    """
    Agent responsible for cleaning and processing raw air quality data.
    """
    
    def __init__(self):
        super().__init__()
    
    def get_name(self):
        return "DataProcessorAgent"
    
    def extract_latest_value(self, measurements):
        """
        Get the most recent non-null measurement value.
        
        Args:
            measurements: Dictionary with 'values' list
            
        Returns:
            Latest value as float, or None if no valid values
        """
        values = measurements.get("values", [])
        
        for entry in values:
            value = entry.get("value")
            if value is not None:
                return float(value)
        
        return None
    
    def raw_to_dataframe(self, raw_data):
        """
        Convert raw API data into a clean pandas DataFrame.
        
        Args:
            raw_data: Raw data from DataCollectorAgent
            
        Returns:
            DataFrame with columns:
            - city, station_id, station_name
            - parameter_code, value, unit
        """
        rows = []
        
        cities_data = raw_data.get("cities", {})
        collection_time = raw_data.get("collection_timestamp")
        
        for city_name, city_data in cities_data.items():
            for station in city_data.get("stations", []):
                station_id = station.get("station_id")
                station_name = station.get("station_name")
                
                for sensor in station.get("sensors", []):
                    param_info = sensor.get("parameter", {})
                    param_code = param_info.get("paramCode", "Unknown")
                    
                    measurements = sensor.get("measurements", {})
                    latest_value = self.extract_latest_value(measurements)
                    
                    # Only add row if we have a valid value
                    if latest_value is not None:
                        rows.append({
                            "city": city_name,
                            "station_id": station_id,
                            "station_name": station_name,
                            "parameter_code": param_code,
                            "value": latest_value,
                            "unit": "µg/m³",
                            "timestamp": collection_time,
                        })
        
        df = pd.DataFrame(rows)
        return df
    
    def extract_aqi_data(self, raw_data):
        """
        Extract AQI information into a separate DataFrame.
        
        Args:
            raw_data: Raw data from DataCollectorAgent
            
        Returns:
            DataFrame with AQI info per station
        """
        rows = []
        
        cities_data = raw_data.get("cities", {})
        
        for city_name, city_data in cities_data.items():
            for station in city_data.get("stations", []):
                aqi = station.get("aqi", {})
                
                if aqi:
                    rows.append({
                        "city": city_name,
                        "station_id": station.get("station_id"),
                        "station_name": station.get("station_name"),
                        "aqi_level": aqi.get("stIndexLevel", {}).get("indexLevelName", "Unknown"),
                        "aqi_level_id": aqi.get("stIndexLevel", {}).get("id", -1),
                    })
        
        df = pd.DataFrame(rows)
        return df
    
    def process(self, input_message=None):
        """
        Main processing method.
        
        Args:
            input_message: Message from DataCollectorAgent
            
        Returns:
            Message containing cleaned DataFrames
        """
        # Check if we received valid input
        if input_message is None:
            self.log("ERROR: No input message received")
            return self.create_message(data=None, status="error")
        
        if input_message.status != "success":
            self.log("ERROR: Previous agent failed")
            return self.create_message(data=None, status="error")
        
        raw_data = input_message.data
        self.log(f"Processing data from {input_message.sender}")
        
        # Convert to DataFrame
        self.log("Converting to DataFrame...")
        measurements_df = self.raw_to_dataframe(raw_data)
        
        # Extract AQI data
        self.log("Extracting AQI data...")
        aqi_df = self.extract_aqi_data(raw_data)
        
        self.log(f"Processed {len(measurements_df)} measurements, {len(aqi_df)} stations")
        
        # Package the results
        processed_data = {
            "measurements": measurements_df,
            "aqi": aqi_df,
            "raw_data": raw_data,  # Keep raw data for reference
        }
        
        return self.create_message(data=processed_data, status="success")


# Test the agent
if __name__ == "__main__":
    print("Testing Data Processor Agent...")
    print("=" * 50)
    
    # First, get data from collector
    from collector_agent import DataCollectorAgent
    
    collector = DataCollectorAgent()
    raw_message = collector.run()
    
    print()  # Empty line
    
    # Now process the data
    processor = DataProcessorAgent()
    processed_message = processor.run(raw_message)
    
    print(f"\nStatus: {processed_message.status}")
    
    if processed_message.status == "success":
        data = processed_message.data
        
        print("\n--- Measurements DataFrame ---")
        print(data["measurements"].to_string(index=False))
        
        print("\n--- AQI DataFrame ---")
        print(data["aqi"].to_string(index=False))