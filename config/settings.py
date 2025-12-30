"""
Configuration settings for the Air Quality Monitoring System
"""

# Set to False when you want to use the real GIOŚ API
USE_MOCK_DATA = False

# GIOŚ API Base URL
API_BASE_URL = "https://api.gios.gov.pl/pjp-api/v1/rest"

# API Endpoints (these are the URLs we'll call)
ENDPOINTS = {
    "all_stations": f"{API_BASE_URL}/station/findAll",
    "station_sensors": f"{API_BASE_URL}/station/sensors/{{station_id}}",
    "sensor_data": f"{API_BASE_URL}/data/getData/{{sensor_id}}",
    "station_aqi": f"{API_BASE_URL}/aqindex/getIndex/{{station_id}}",
}

# The 3 Polish cities we want to monitor
TARGET_CITIES = [
    "Warszawa",
    "Kraków",
    "Gdańsk",
]

# Pollutants we're tracking
POLLUTANTS = ["PM2.5", "PM10", "NO2", "SO2", "O3", "CO"]

# How often to refresh data (in seconds)
REFRESH_INTERVAL = 3600  # 1 hour

# API request timeout
REQUEST_TIMEOUT = 30