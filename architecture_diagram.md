# Multi-Agent Air Quality Monitoring System - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL DATA SOURCE                                   │
│                                                                                  │
│                         ┌─────────────────────┐                                  │
│                         │      GIOŚ API       │                                  │
│                         │  (Polish Gov API)   │                                  │
│                         └──────────┬──────────┘                                  │
│                                    │                                             │
└────────────────────────────────────┼─────────────────────────────────────────────┘
                                     │ HTTP Requests
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              AGENT LAYER                                         │
│                                                                                  │
│  ┌──────────────────────┐                                                        │
│  │  DATA COLLECTOR      │                                                        │
│  │      AGENT           │                                                        │
│  │                      │                                                        │
│  │ • Fetches stations   │                                                        │
│  │ • Fetches sensors    │                                                        │
│  │ • Fetches raw data   │                                                        │
│  └──────────┬───────────┘                                                        │
│             │                                                                    │
│             │ Raw JSON Data                                                      │
│             ▼                                                                    │
│  ┌──────────────────────┐                                                        │
│  │  DATA PROCESSOR      │                                                        │
│  │      AGENT           │                                                        │
│  │                      │                                                        │
│  │ • Cleans data        │                                                        │
│  │ • Handles nulls      │                                                        │
│  │ • Standardizes       │                                                        │
│  └──────────┬───────────┘                                                        │
│             │                                                                    │
│             │ Clean DataFrame                                                    │
│             ▼                                                                    │
│  ┌──────────────────────┐                                                        │
│  │  QUALITY CLASSIFIER  │                                                        │
│  │      AGENT           │                                                        │
│  │                      │                                                        │
│  │ • Calculates AQI     │                                                        │
│  │ • Assigns category   │                                                        │
│  │ • Color coding       │                                                        │
│  └──────────┬───────────┘                                                        │
│             │                                                                    │
│             │ Classified Data                                                    │
│             ▼                                                                    │
│  ┌──────────────────────┐                                                        │
│  │  HEALTH ADVISOR      │                                                        │
│  │      AGENT           │                                                        │
│  │                      │                                                        │
│  │ • Health warnings    │                                                        │
│  │ • Recommendations    │                                                        │
│  │ • Risk assessment    │                                                        │
│  └──────────┬───────────┘                                                        │
│             │                                                                    │
│             │ Final Enriched Data                                                │
│             ▼                                                                    │
│  ┌──────────────────────┐                                                        │
│  │  COORDINATOR         │◄─────── Orchestrates all agents                        │
│  │      AGENT           │                                                        │
│  │                      │                                                        │
│  │ • Manages flow       │                                                        │
│  │ • Error handling     │                                                        │
│  │ • Agent scheduling   │                                                        │
│  └──────────┬───────────┘                                                        │
│             │                                                                    │
└─────────────┼───────────────────────────────────────────────────────────────────┘
              │
              │ Processed Results
              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                                     │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                        STREAMLIT DASHBOARD                                │   │
│  │                                                                           │   │
│  │   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                  │   │
│  │   │   Warsaw    │    │   Kraków    │    │  Wrocław    │                  │   │
│  │   │   AQI: 45   │    │   AQI: 78   │    │   AQI: 52   │                  │   │
│  │   │   Good ●    │    │  Moderate ● │    │   Good ●    │                  │   │
│  │   └─────────────┘    └─────────────┘    └─────────────┘                  │   │
│  │                                                                           │   │
│  │   ┌────────────────────────────────────────────────────────────────┐     │   │
│  │   │                    POLLUTANT CHARTS                            │     │   │
│  │   │         PM2.5 | PM10 | NO2 | SO2 | O3                          │     │   │
│  │   └────────────────────────────────────────────────────────────────┘     │   │
│  │                                                                           │   │
│  │   ┌────────────────────────────────────────────────────────────────┐     │   │
│  │   │                 HEALTH RECOMMENDATIONS                         │     │   │
│  │   │    "Air quality is moderate. Sensitive groups should..."       │     │   │
│  │   └────────────────────────────────────────────────────────────────┘     │   │
│  │                                                                           │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Summary

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    GIOŚ     │────▶│  Collector  │────▶│  Processor  │────▶│ Classifier  │────▶│   Advisor   │
│    API      │     │   Agent     │     │   Agent     │     │   Agent     │     │   Agent     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                                       │
                           ┌───────────────────────────────────────────────────────────┘
                           │
                           ▼
                    ┌─────────────┐     ┌─────────────────────────────────────────────┐
                    │ Coordinator │────▶│              Streamlit UI                   │
                    │   Agent     │     │  (Dashboard with charts & recommendations) │
                    └─────────────┘     └─────────────────────────────────────────────┘
```

## Agent Communication Protocol

```
┌────────────────────────────────────────────────────────────────────┐
│                    MESSAGE PASSING STRUCTURE                        │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Agent A                              Agent B                      │
│   ┌─────┐                              ┌─────┐                      │
│   │     │──── message = {              │     │                      │
│   │     │       "sender": "AgentA",    │     │                      │
│   │     │       "data": {...},    ────▶│     │                      │
│   │     │       "timestamp": "...",    │     │                      │
│   │     │       "status": "success"    │     │                      │
│   │     │     }                        │     │                      │
│   └─────┘                              └─────┘                      │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

## Project File Structure

```
air_quality_mas/
│
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # Base class for all agents
│   ├── collector_agent.py     # Data Collector Agent
│   ├── processor_agent.py     # Data Processor Agent
│   ├── classifier_agent.py    # Quality Classifier Agent
│   ├── advisor_agent.py       # Health Advisor Agent
│   └── coordinator_agent.py   # Coordinator Agent
│
├── config/
│   ├── __init__.py
│   ├── settings.py            # Configuration (cities, API URLs)
│   └── aqi_standards.py       # AQI thresholds and categories
│
├── utils/
│   ├── __init__.py
│   └── api_client.py          # HTTP client for GIOŚ API
│
├── app.py                     # Streamlit application
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
└── README.md                  # Project documentation
```