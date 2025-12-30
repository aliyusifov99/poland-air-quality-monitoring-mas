# 🌬️ Multi-Agent Air Quality Monitoring System

A Multi-Agent System (MAS) for monitoring real-time air quality in Polish cities. This project demonstrates how multiple AI agents collaborate to collect, process, classify, and visualize air quality data.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Agents Description](#agents-description)
- [Data Source](#data-source)
- [Screenshots](#screenshots)
- [Future Improvements](#future-improvements)
- [License](#license)

## 🎯 Overview

This project implements a Multi-Agent System that monitors air quality across three major Polish cities:
- **Warszawa** (Warsaw)
- **Kraków** (Krakow)
- **Gdańsk** (Gdansk)

The system fetches real-time data from the GIOŚ (Polish Chief Inspectorate of Environmental Protection) API, processes it through a pipeline of specialized agents, and presents the results in an interactive Streamlit dashboard.

## ✨ Features

- **Real-time Data**: Fetches live air quality data from official Polish government API
- **Multi-Agent Architecture**: 5 specialized agents working together
- **Air Quality Classification**: Categorizes air quality (Very Good → Very Bad)
- **Health Recommendations**: Provides health advice based on air quality
- **Interactive Dashboard**: Beautiful Streamlit UI with charts and gauges
- **Caching**: 5-minute cache to optimize performance
- **Dual Mode**: Supports both real API and mock data for testing

## 🏗️ Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                        GIOŚ API                                  │
│              (Polish Government Air Quality API)                 │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AGENT LAYER                                 │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Collector  │───▶│  Processor   │───▶│  Classifier  │       │
│  │    Agent     │    │    Agent     │    │    Agent     │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                   │              │
│                                                   ▼              │
│                      ┌──────────────┐    ┌──────────────┐       │
│                      │ Coordinator  │◀───│   Advisor    │       │
│                      │    Agent     │    │    Agent     │       │
│                      └──────────────┘    └──────────────┘       │
│                             │                                    │
└─────────────────────────────┼────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   STREAMLIT DASHBOARD                            │
│                                                                  │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐                     │
│   │ Warsaw  │    │ Kraków  │    │ Gdańsk  │                     │
│   │  Card   │    │  Card   │    │  Card   │                     │
│   └─────────┘    └─────────┘    └─────────┘                     │
│                                                                  │
│   ┌─────────────────────┐    ┌─────────────────────┐            │
│   │  Pollutant Charts   │    │    AQI Gauges       │            │
│   └─────────────────────┘    └─────────────────────┘            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Clone or download the project**
```bash
   cd air_quality_mas
```

2. **Install dependencies**
```bash
   pip install -r requirements.txt
```

3. **Configure data source** (optional)
   
   Edit `config/settings.py`:
```python
   # Use real API data
   USE_MOCK_DATA = False
   
   # Or use mock data for testing
   USE_MOCK_DATA = True
```

## 💻 Usage

### Run the Dashboard
```bash
streamlit run app.py
```

This will open the dashboard in your browser at `http://localhost:8501`

### Run Individual Agents (for testing)
```bash
# Test the full pipeline
python agents/coordinator_agent.py

# Test individual agents
python agents/collector_agent.py
python agents/processor_agent.py
python agents/classifier_agent.py
python agents/advisor_agent.py

# Test API client
python utils/api_client.py
```

## 📁 Project Structure
```
air_quality_mas/
│
├── agents/                     # Agent modules
│   ├── __init__.py
│   ├── base_agent.py          # Base class for all agents
│   ├── collector_agent.py     # Fetches data from API
│   ├── processor_agent.py     # Cleans and structures data
│   ├── classifier_agent.py    # Classifies air quality
│   ├── advisor_agent.py       # Generates health advice
│   └── coordinator_agent.py   # Orchestrates all agents
│
├── config/                     # Configuration files
│   ├── __init__.py
│   ├── settings.py            # API URLs, target cities
│   └── aqi_standards.py       # AQI thresholds, health advice
│
├── utils/                      # Utility modules
│   ├── __init__.py
│   ├── api_client.py          # Real GIOŚ API client
│   └── mock_data.py           # Mock data for testing
│
├── app.py                      # Streamlit dashboard
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🤖 Agents Description

### 1. Data Collector Agent
- **Purpose**: Fetches raw data from GIOŚ API
- **Input**: Target city names
- **Output**: Raw JSON data (stations, sensors, measurements, AQI)

### 2. Data Processor Agent
- **Purpose**: Cleans and structures raw data
- **Input**: Raw JSON from Collector
- **Output**: Clean pandas DataFrames

### 3. Quality Classifier Agent
- **Purpose**: Classifies air quality using Polish AQI standards
- **Input**: Clean DataFrames from Processor
- **Output**: Data with AQI categories and colors

### 4. Health Advisor Agent
- **Purpose**: Generates health recommendations
- **Input**: Classified data from Classifier
- **Output**: Data with health advice and activity suggestions

### 5. Coordinator Agent
- **Purpose**: Orchestrates the entire pipeline
- **Input**: User configuration
- **Output**: Final processed results for UI

## 📊 Data Source

This project uses the **GIOŚ API** (Główny Inspektorat Ochrony Środowiska - Polish Chief Inspectorate of Environmental Protection).

- **API Documentation**: https://powietrze.gios.gov.pl/pjp/content/api
- **Data includes**: PM2.5, PM10, NO2, SO2, O3, CO, and more
- **Update frequency**: Hourly

### Polish Air Quality Index (AQI) Categories

| Category | Polish Name | Color | Health Advice |
|----------|-------------|-------|---------------|
| Very Good | Bardzo dobry | 🟢 Green | Perfect for outdoor activities |
| Good | Dobry | 🟢 Green | Enjoy outdoor activities |
| Moderate | Umiarkowany | 🟡 Yellow | Consider reducing intense exercise |
| Sufficient | Dostateczny | 🟠 Orange | Reduce outdoor activities |
| Bad | Zły | 🔴 Red | Avoid outdoor activities |
| Very Bad | Bardzo zły | 🟤 Maroon | Stay indoors |

## 🖼️ Screenshots

### Dashboard Overview
The dashboard displays:
- City cards with current air quality status
- Color-coded AQI indicators
- Health recommendations
- Pollutant comparison charts
- AQI gauge visualizations
- Detailed measurement tables

## 🔮 Future Improvements

- [ ] Add more Polish cities
- [ ] Historical data analysis and trends
- [ ] Air quality predictions using ML
- [ ] Email/SMS alerts for poor air quality
- [ ] Mobile-responsive design
- [ ] Data export functionality (CSV, PDF)
- [ ] Comparison with WHO guidelines

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **GIOŚ** - For providing free access to air quality data
- **Streamlit** - For the amazing dashboard framework
- **Plotly** - For interactive visualizations

---

**Built with ❤️ for cleaner air in Poland**