"""
Data Collector Agent

This agent fetches raw air quality data from the GIOŚ API.
It's the FIRST agent in our pipeline.

Job: Call the API → Get raw data → Pass to next agent
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from agents.base_agent import BaseAgent
from config.settings import TARGET_CITIES, USE_MOCK_DATA

# Choose API client based on settings
if USE_MOCK_DATA:
    from utils.mock_data import MockGIOSApiClient as ApiClient
else:
    from utils.api_client import GIOSApiClient as ApiClient


class DataCollectorAgent(BaseAgent):
    """
    Agent responsible for collecting air quality data from GIOŚ API.
    """
    
    def __init__(self, target_cities=None):
        """
        Initialize the agent.
        
        Args:
            target_cities: List of cities to monitor (default: from settings)
        """
        self.target_cities = target_cities or TARGET_CITIES
        self.api_client = ApiClient()  # Using mock data for now
        super().__init__()
    
    def get_name(self):
        return "DataCollectorAgent"
    
    def get_stations_for_cities(self):
        """
        Get all stations that are in our target cities.
        
        Returns:
            List of station dictionaries
        """
        self.log(f"Fetching stations for: {self.target_cities}")
        
        # Get all stations from API
        all_stations = self.api_client.get_all_stations()
        
        # Filter only stations in our target cities
        filtered = []
        for station in all_stations:
            city_name = station.get("city", {}).get("name", "")
            if city_name in self.target_cities:
                filtered.append(station)
        
        self.log(f"Found {len(filtered)} stations")
        return filtered
    
    def collect_all_data(self):
        """
        Main collection method - gathers all data for target cities.
        
        Returns:
            Dictionary with all collected data organized by city
        """
        from datetime import datetime
        
        collected_data = {
            "cities": {},
            "collection_timestamp": datetime.now().isoformat(),
        }
        
        # Get stations
        stations = self.get_stations_for_cities()
        
        # Process each station
        for station in stations:
            city_name = station.get("city", {}).get("name", "Unknown")
            station_id = station["id"]
            
            # Initialize city if first time seeing it
            if city_name not in collected_data["cities"]:
                collected_data["cities"][city_name] = {"stations": []}
            
            # Get sensors for this station
            sensors = self.api_client.get_station_sensors(station_id)
            
            # Get measurements for each sensor
            sensor_data = []
            for sensor in sensors:
                sensor_id = sensor["id"]
                measurements = self.api_client.get_sensor_data(sensor_id)
                sensor_data.append({
                    "sensor_id": sensor_id,
                    "parameter": sensor.get("param", {}),
                    "measurements": measurements
                })
            
            # Get AQI for station
            aqi_data = self.api_client.get_station_aqi(station_id)
            
            # Add station to city
            station_entry = {
                "station_id": station_id,
                "station_name": station.get("stationName", "Unknown"),
                "latitude": station.get("gegrLat"),
                "longitude": station.get("gegrLon"),
                "sensors": sensor_data,
                "aqi": aqi_data
            }
            collected_data["cities"][city_name]["stations"].append(station_entry)
        
        return collected_data
    
    def process(self, input_message=None):
        """
        Main processing method.
        
        Returns:
            Message containing all collected raw data
        """
        self.log("Collecting data from GIOŚ API...")
        
        raw_data = self.collect_all_data()
        
        # Count what we collected
        city_count = len(raw_data["cities"])
        station_count = sum(
            len(city["stations"]) 
            for city in raw_data["cities"].values()
        )
        
        self.log(f"Collected data from {city_count} cities, {station_count} stations")
        
        return self.create_message(data=raw_data, status="success")


# Test the agent
if __name__ == "__main__":
    print("Testing Data Collector Agent...")
    print("=" * 50)
    
    agent = DataCollectorAgent()
    result = agent.run()
    
    print(f"\nStatus: {result.status}")
    print(f"Cities collected: {list(result.data['cities'].keys())}")
    
    # Show details for each city
    for city, city_data in result.data['cities'].items():
        print(f"\n{city}:")
        for station in city_data['stations']:
            print(f"  - {station['station_name']}")
            print(f"    Sensors: {len(station['sensors'])}")
            aqi_level = station['aqi']['stIndexLevel']['indexLevelName']
            print(f"    AQI: {aqi_level}")
