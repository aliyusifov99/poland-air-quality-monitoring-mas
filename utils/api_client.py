"""
Real API Client for GIOŚ (Polish Chief Inspectorate of Environmental Protection)

This client makes actual HTTP requests to the GIOŚ air quality API.
API Documentation: https://powietrze.gios.gov.pl/pjp/content/api
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import requests
from config.settings import ENDPOINTS, REQUEST_TIMEOUT


class GIOSApiClient:
    """
    Real API client for GIOŚ Air Quality API.
    Fetches live data from Polish government servers.
    """
    
    def __init__(self, verbose=False):
        """
        Initialize the API client.
        
        Args:
            verbose: If True, print error messages. If False, fail silently.
        """
        self.timeout = REQUEST_TIMEOUT
        self.verbose = verbose
    
    def _make_request(self, url):
        """
        Make HTTP GET request to the API.
        
        Args:
            url: Full URL to request
            
        Returns:
            JSON response as dictionary/list, or None if request fails
        """
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            if self.verbose:
                print(f"ERROR: Request timeout for {url}")
            return None
        except requests.exceptions.HTTPError as e:
            if self.verbose:
                print(f"ERROR: HTTP error for {url}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            if self.verbose:
                print(f"ERROR: Request failed for {url}: {e}")
            return None
        except ValueError as e:
            if self.verbose:
                print(f"ERROR: Failed to parse JSON from {url}: {e}")
            return None
    
    def get_all_stations(self):
        """
        Fetch all air quality monitoring stations in Poland.
        Handles pagination to get ALL stations.
        
        Returns:
            List of station dictionaries (transformed to English keys)
        """
        url = ENDPOINTS["all_stations"]
        all_stations = []
        page = 1
        
        while True:
            page_url = f"{url}?page={page}"
            response = self._make_request(page_url)
            
            if not response:
                break
            
            if isinstance(response, dict):
                raw_stations = response.get('Lista stacji pomiarowych', [])
                total_pages = response.get('totalPages', 1)
            else:
                raw_stations = response if response else []
                total_pages = 1
            
            # Transform Polish keys to English keys
            for station in raw_stations:
                all_stations.append({
                    "id": station.get("Identyfikator stacji"),
                    "stationName": station.get("Nazwa stacji"),
                    "gegrLat": station.get("WGS84 φ N"),
                    "gegrLon": station.get("WGS84 λ E"),
                    "city": {
                        "id": station.get("Identyfikator miasta"),
                        "name": station.get("Nazwa miasta"),
                    },
                    "addressStreet": station.get("Ulica"),
                })
            
            if page >= total_pages:
                break
            
            page += 1
        
        return all_stations

    def get_station_sensors(self, station_id):
        """
        Fetch all sensors for a specific station.
        
        Args:
            station_id: ID of the station
            
        Returns:
            List of sensor dictionaries (transformed to English keys)
        """
        url = ENDPOINTS["station_sensors"].format(station_id=station_id)
        response = self._make_request(url)
        
        if not response:
            return []
        
        if isinstance(response, dict):
            raw_sensors = response.get('Lista stanowisk pomiarowych dla podanej stacji', [])
        else:
            raw_sensors = response if response else []
        
        # Transform Polish keys to English keys
        sensors = []
        for sensor in raw_sensors:
            sensors.append({
                "id": sensor.get("Identyfikator stanowiska"),
                "stationId": sensor.get("Identyfikator stacji"),
                "param": {
                    "paramName": sensor.get("Wskaźnik"),
                    "paramFormula": sensor.get("Wskaźnik - wzór"),
                    "paramCode": sensor.get("Wskaźnik - kod"),
                }
            })
        
        return sensors

    def get_sensor_data(self, sensor_id):
        """
        Fetch measurement data from a specific sensor.
        
        Args:
            sensor_id: ID of the sensor
            
        Returns:
            Dictionary with 'key' (parameter code) and 'values' (measurements)
        """
        url = ENDPOINTS["sensor_data"].format(sensor_id=sensor_id)
        response = self._make_request(url)
        
        if not response:
            return {"key": "", "values": []}
        
        if isinstance(response, dict):
            raw_data = response.get('Lista danych pomiarowych', [])
        else:
            raw_data = []
        
        # Transform Polish keys to English keys
        values = []
        for item in raw_data:
            values.append({
                "date": item.get("Data"),
                "value": item.get("Wartość"),
            })
        
        # Extract parameter code from station code
        key = ""
        if raw_data and raw_data[0].get("Kod stanowiska"):
            parts = raw_data[0].get("Kod stanowiska", "").split("-")
            if len(parts) >= 2:
                key = parts[1]
        
        return {
            "key": key,
            "values": values
        }
    
    def get_station_aqi(self, station_id):
        """
        Fetch Air Quality Index for a specific station.
        
        Args:
            station_id: ID of the station
            
        Returns:
            Dictionary with AQI data (transformed to English keys)
        """
        url = ENDPOINTS["station_aqi"].format(station_id=station_id)
        response = self._make_request(url)
        
        if not response:
            return {}
        
        if isinstance(response, dict):
            raw_aqi = response.get('AqIndex', {})
        else:
            return {}
        
        # Transform Polish keys to English keys
        aqi = {
            "id": raw_aqi.get("Identyfikator stacji pomiarowej"),
            "stCalcDate": raw_aqi.get("Data wykonania obliczeń indeksu"),
            "stIndexLevel": {
                "id": raw_aqi.get("Wartość indeksu"),
                "indexLevelName": raw_aqi.get("Nazwa kategorii indeksu"),
            },
        }
        
        return aqi
    
    def close(self):
        """Cleanup (nothing to do for requests library)."""
        pass


# Test the API client
if __name__ == "__main__":
    print("Testing Real GIOŚ API Client...")
    print("-" * 40)
    
    client = GIOSApiClient(verbose=True)
    
    # Test stations
    stations = client.get_all_stations()
    print(f"✅ Found {len(stations)} stations")
    
    # Test target cities
    print("\n--- Target cities ---")
    from config.settings import TARGET_CITIES
    
    for city_name in TARGET_CITIES:
        city_stations = [s for s in stations if s['city']['name'] == city_name]
        print(f"{city_name}: {len(city_stations)} stations")
    
    client.close()