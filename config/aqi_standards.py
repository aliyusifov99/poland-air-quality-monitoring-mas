"""
Polish Air Quality Index (AQI) Standards and Thresholds

Based on official Polish Air Quality Index from GIOŚ
"""

# AQI Categories with color codes for the UI
AQI_CATEGORIES = {
    "very_good": {
        "name": "Bardzo dobry",
        "name_en": "Very Good",
        "color": "#00FF00",  # Bright Green
        "level": 0,
    },
    "good": {
        "name": "Dobry",
        "name_en": "Good",
        "color": "#00CC00",  # Green
        "level": 1,
    },
    "moderate": {
        "name": "Umiarkowany",
        "name_en": "Moderate",
        "color": "#FFFF00",  # Yellow
        "level": 2,
    },
    "sufficient": {
        "name": "Dostateczny",
        "name_en": "Sufficient",
        "color": "#FF9900",  # Orange
        "level": 3,
    },
    "bad": {
        "name": "Zły",
        "name_en": "Bad",
        "color": "#FF0000",  # Red
        "level": 4,
    },
    "very_bad": {
        "name": "Bardzo zły",
        "name_en": "Very Bad",
        "color": "#990000",  # Dark Red
        "level": 5,
    },
}

# Pollutant thresholds (µg/m³) for each AQI category
# Format: (min_value, max_value)
AQI_THRESHOLDS = {
    "PM2.5": {
        "very_good": (0, 13),
        "good": (13.1, 35),
        "moderate": (35.1, 55),
        "sufficient": (55.1, 75),
        "bad": (75.1, 110),
        "very_bad": (110.1, float('inf')),
    },
    "PM10": {
        "very_good": (0, 20),
        "good": (20.1, 50),
        "moderate": (50.1, 80),
        "sufficient": (80.1, 110),
        "bad": (110.1, 150),
        "very_bad": (150.1, float('inf')),
    },
    "NO2": {
        "very_good": (0, 40),
        "good": (40.1, 100),
        "moderate": (100.1, 150),
        "sufficient": (150.1, 200),
        "bad": (200.1, 400),
        "very_bad": (400.1, float('inf')),
    },
    "SO2": {
        "very_good": (0, 50),
        "good": (50.1, 100),
        "moderate": (100.1, 200),
        "sufficient": (200.1, 350),
        "bad": (350.1, 500),
        "very_bad": (500.1, float('inf')),
    },
    "O3": {
        "very_good": (0, 70),
        "good": (70.1, 120),
        "moderate": (120.1, 150),
        "sufficient": (150.1, 180),
        "bad": (180.1, 240),
        "very_bad": (240.1, float('inf')),
    },
    "CO": {
        "very_good": (0, 3000),
        "good": (3000.1, 7000),
        "moderate": (7000.1, 11000),
        "sufficient": (11000.1, 15000),
        "bad": (15000.1, 21000),
        "very_bad": (21000.1, float('inf')),
    },
}

# Health recommendations for each AQI category
HEALTH_RECOMMENDATIONS = {
    "very_good": {
        "general_en": "Air quality is excellent. Perfect for outdoor activities!",
        "sensitive_en": "No restrictions for any group.",
    },
    "good": {
        "general_en": "Air quality is good. Enjoy outdoor activities.",
        "sensitive_en": "No restrictions for any group.",
    },
    "moderate": {
        "general_en": "Air quality is acceptable. Consider reducing intense outdoor exercise.",
        "sensitive_en": "Sensitive groups should limit prolonged outdoor exertion.",
    },
    "sufficient": {
        "general_en": "Air quality is sufficient. Reduce outdoor activities.",
        "sensitive_en": "Sensitive groups should avoid outdoor exertion.",
    },
    "bad": {
        "general_en": "Air quality is bad. Avoid outdoor activities. Keep windows closed.",
        "sensitive_en": "Sensitive groups should stay indoors.",
    },
    "very_bad": {
        "general_en": "Air quality is very bad. Stay indoors. Use air purifier if available.",
        "sensitive_en": "Everyone should stay indoors and avoid exertion.",
    },
}

