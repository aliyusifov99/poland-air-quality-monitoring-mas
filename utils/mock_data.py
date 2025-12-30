"""
Mock Data for Air Quality Monitoring System

This provides sample data that mimics GIOŚ API responses.
Used for development and testing when the real API is not accessible.
"""

import random
from datetime import datetime, timedelta


# Sample stations (based on real GIOŚ data structure)
MOCK_STATIONS = [
    # Warsaw stations
    {
        "id": 114,
        "stationName": "Warszawa-Marszałkowska",
        "gegrLat": "52.219568",
        "gegrLon": "21.012568",
        "city": {"id": 1, "name": "Warszawa"},
        "addressStreet": "ul. Marszałkowska"
    },
    {
        "id": 115,
        "stationName": "Warszawa-Komunikacyjna",
        "gegrLat": "52.219300",
        "gegrLon": "21.005200",
        "city": {"id": 1, "name": "Warszawa"},
        "addressStreet": "Al. Niepodległości"
    },
    # Kraków stations
    {
        "id": 400,
        "stationName": "Kraków, Aleja Krasińskiego",
        "gegrLat": "50.057678",
        "gegrLon": "19.926189",
        "city": {"id": 2, "name": "Kraków"},
        "addressStreet": "Aleja Krasińskiego"
    },
    {
        "id": 401,
        "stationName": "Kraków, ul. Bujaka",
        "gegrLat": "50.010575",
        "gegrLon": "19.949189",
        "city": {"id": 2, "name": "Kraków"},
        "addressStreet": "ul. Bujaka"
    },
    # Wrocław stations
    {
        "id": 117,
        "stationName": "Wrocław, ul. Bartnicza",
        "gegrLat": "51.115356",
        "gegrLon": "17.074114",
        "city": {"id": 3, "name": "Wrocław"},
        "addressStreet": "ul. Bartnicza"
    },
    {
        "id": 118,
        "stationName": "Wrocław, ul. Korzeniowskiego",
        "gegrLat": "51.129378",
        "gegrLon": "17.029250",
        "city": {"id": 3, "name": "Wrocław"},
        "addressStreet": "ul. Korzeniowskiego"
    },
]

# Sensors for each station
MOCK_SENSORS = {
    114: [
        {"id": 672, "stationId": 114, "param": {"paramName": "pył zawieszony PM2.5", "paramFormula": "PM2.5", "paramCode": "PM2.5"}},
        {"id": 673, "stationId": 114, "param": {"paramName": "pył zawieszony PM10", "paramFormula": "PM10", "paramCode": "PM10"}},
        {"id": 674, "stationId": 114, "param": {"paramName": "dwutlenek azotu", "paramFormula": "NO2", "paramCode": "NO2"}},
    ],
    115: [
        {"id": 680, "stationId": 115, "param": {"paramName": "pył zawieszony PM2.5", "paramFormula": "PM2.5", "paramCode": "PM2.5"}},
        {"id": 681, "stationId": 115, "param": {"paramName": "pył zawieszony PM10", "paramFormula": "PM10", "paramCode": "PM10"}},
    ],
    400: [
        {"id": 690, "stationId": 400, "param": {"paramName": "pył zawieszony PM2.5", "paramFormula": "PM2.5", "paramCode": "PM2.5"}},
        {"id": 691, "stationId": 400, "param": {"paramName": "pył zawieszony PM10", "paramFormula": "PM10", "paramCode": "PM10"}},
        {"id": 692, "stationId": 400, "param": {"paramName": "dwutlenek azotu", "paramFormula": "NO2", "paramCode": "NO2"}},
    ],
    401: [
        {"id": 700, "stationId": 401, "param": {"paramName": "pył zawieszony PM2.5", "paramFormula": "PM2.5", "paramCode": "PM2.5"}},
        {"id": 701, "stationId": 401, "param": {"paramName": "pył zawieszony PM10", "paramFormula": "PM10", "paramCode": "PM10"}},
    ],
    117: [
        {"id": 710, "stationId": 117, "param": {"paramName": "pył zawieszony PM2.5", "paramFormula": "PM2.5", "paramCode": "PM2.5"}},
        {"id": 711, "stationId": 117, "param": {"paramName": "pył zawieszony PM10", "paramFormula": "PM10", "paramCode": "PM10"}},
    ],
    118: [
        {"id": 720, "stationId": 118, "param": {"paramName": "pył zawieszony PM2.5", "paramFormula": "PM2.5", "paramCode": "PM2.5"}},
        {"id": 721, "stationId": 118, "param": {"paramName": "pył zawieszony PM10", "paramFormula": "PM10", "paramCode": "PM10"}},
    ],
}

# Typical value ranges for each pollutant (µg/m³)
POLLUTANT_RANGES = {
    "PM2.5": (5, 80),
    "PM10": (10, 120),
    "NO2": (10, 150),
    "SO2": (5, 100),
    "O3": (20, 160),
    "CO": (200, 5000),
}


def generate_sensor_values(param_code, num_values=24):
    """
    Generate realistic sensor measurement values.
    
    Args:
        param_code: Pollutant code (PM2.5, PM10, etc.)
        num_values: Number of hourly values to generate
        
    Returns:
        List of measurement dictionaries with date and value
    """
    values = []
    min_val, max_val = POLLUTANT_RANGES.get(param_code, (10, 100))
    
    now = datetime.now()
    base_value = random.uniform(min_val, (min_val + max_val) / 2)
    
    for i in range(num_values):
        timestamp = now - timedelta(hours=i)
        # Add random variation
        variation = random.uniform(-0.2, 0.2) * base_value
        value = max(0, base_value + variation)
        
        values.append({
            "date": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "value": round(value, 2)
        })
    
    return values


def get_mock_aqi(station_id):
    """
    Generate mock AQI data for a station.
    
    Args:
        station_id: The station ID
        
    Returns:
        Dictionary mimicking GIOŚ API AQI response
    """
    levels = [
        {"id": 0, "indexLevelName": "Bardzo dobry"},
        {"id": 1, "indexLevelName": "Dobry"},
        {"id": 2, "indexLevelName": "Umiarkowany"},
        {"id": 3, "indexLevelName": "Dostateczny"},
        {"id": 4, "indexLevelName": "Zły"},
        {"id": 5, "indexLevelName": "Bardzo zły"},
    ]
    
    # Random AQI level (weighted towards better quality)
    weights = [0.15, 0.30, 0.25, 0.15, 0.10, 0.05]
    level_index = random.choices(range(6), weights=weights)[0]
    
    now = datetime.now()
    
    return {
        "id": station_id,
        "stCalcDate": now.strftime("%Y-%m-%d %H:%M:%S"),
        "stIndexLevel": levels[level_index],
    }


class MockGIOSApiClient:
    """
    Mock API client that returns simulated data.
    Mimics the real GIOŚ API structure.
    """
    
    def get_all_stations(self):
        """Return all mock stations."""
        return MOCK_STATIONS
    
    def get_station_sensors(self, station_id):
        """Return sensors for a specific station."""
        return MOCK_SENSORS.get(station_id, [])
    
    def get_sensor_data(self, sensor_id):
        """Return mock sensor measurement data."""
        # Find which parameter this sensor measures
        param_code = "PM10"  # Default
        for station_sensors in MOCK_SENSORS.values():
            for sensor in station_sensors:
                if sensor["id"] == sensor_id:
                    param_code = sensor["param"]["paramCode"]
                    break
        
        return {
            "key": param_code,
            "values": generate_sensor_values(param_code)
        }
    
    def get_station_aqi(self, station_id):
        """Return mock AQI data for a station."""
        return get_mock_aqi(station_id)
    
    def close(self):
        """No-op for mock client."""
        pass


# Test the mock data
if __name__ == "__main__":
    client = MockGIOSApiClient()
    
    print("Testing Mock API Client...")
    print("-" * 40)
    
    stations = client.get_all_stations()
    print(f"✓ Found {len(stations)} stations")
    
    sensors = client.get_station_sensors(400)
    print(f"✓ Found {len(sensors)} sensors for Kraków station")
    
    data = client.get_sensor_data(690)
    print(f"✓ Got {len(data['values'])} measurements for {data['key']}")
    
    aqi = client.get_station_aqi(400)
    print(f"✓ AQI Level: {aqi['stIndexLevel']['indexLevelName']}")
