"""
Air Quality Monitoring System - Streamlit Dashboard

This is the main UI for our Multi-Agent System.
Run with: streamlit run app.py
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from agents.coordinator_agent import CoordinatorAgent


# Page configuration
st.set_page_config(
    page_title="Air Quality Monitor - Poland",
    page_icon="🌬️",
    layout="wide"
)


@st.cache_data(ttl=300)  # Cache for 5 minutes (300 seconds)
def get_air_quality_data():
    """
    Run the multi-agent pipeline and get results.
    Cached for 5 minutes to avoid slow reloads.
    
    Returns:
        Dictionary with air quality data
    """
    coordinator = CoordinatorAgent()
    result = coordinator.run()
    
    if result.status == "success":
        return result.data["data"]
    else:
        return None


def display_city_card(city_data):
    """
    Display a card for one city with its air quality info.
    """
    color = city_data['overall_color']
    category = city_data['overall_category']
    emoji = city_data['emoji']
    
    st.markdown(f"""
    <div style="
        background-color: {color}20;
        border-left: 5px solid {color};
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
    ">
        <h3 style="margin:0;">{emoji} {city_data['city']}</h3>
        <p style="font-size: 24px; font-weight: bold; color: {color}; margin: 10px 0;">
            {category}
        </p>
        <p style="margin: 5px 0;">
            <strong>Main pollutant:</strong> {city_data['dominant_pollutant']} 
            ({city_data['dominant_value']:.1f} µg/m³)
        </p>
        <p style="margin: 5px 0;">
            <strong>Stations:</strong> {city_data['stations_count']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("💡 Health Advice"):
        st.write(f"**General:** {city_data['health_advice']}")
        st.write(f"**Sensitive groups:** {city_data['sensitive_advice']}")


def create_pollutant_chart(measurements_df):
    """
    Create a bar chart showing pollutant levels by city.
    """
    # Filter to main pollutants only
    main_pollutants = ['PM2.5', 'PM10', 'NO2', 'SO2', 'O3']
    filtered_df = measurements_df[measurements_df['parameter_code'].isin(main_pollutants)]
    
    if filtered_df.empty:
        return None
    
    chart_data = filtered_df.groupby(['city', 'parameter_code'])['value'].mean().reset_index()
    
    fig = px.bar(
        chart_data,
        x='city',
        y='value',
        color='parameter_code',
        barmode='group',
        title='Pollutant Levels by City (Main Pollutants)',
        labels={
            'value': 'Concentration (µg/m³)',
            'city': 'City',
            'parameter_code': 'Pollutant'
        }
    )
    
    fig.update_layout(
        legend_title_text='Pollutant',
        height=400
    )
    
    return fig


def create_aqi_gauge(city_data):
    """
    Create a gauge chart for AQI level.
    """
    level = city_data['overall_level']
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=level,
        title={'text': city_data['city']},
        gauge={
            'axis': {'range': [0, 5], 'tickvals': [0, 1, 2, 3, 4, 5]},
            'bar': {'color': city_data['overall_color']},
            'steps': [
                {'range': [0, 1], 'color': '#00FF00'},
                {'range': [1, 2], 'color': '#00CC00'},
                {'range': [2, 3], 'color': '#FFFF00'},
                {'range': [3, 4], 'color': '#FF9900'},
                {'range': [4, 5], 'color': '#FF0000'},
            ],
        }
    ))
    
    fig.update_layout(height=250)
    
    return fig


def main():
    """Main function to run the Streamlit app."""
    
    # Header
    st.title("🌬️ Air Quality Monitoring System")
    st.markdown("**Real-time Multi-Agent System for Polish Cities**")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.header("⚙️ Settings")
    
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**About**")
    st.sidebar.info(
        "This dashboard monitors air quality in Warsaw, Kraków, and Gdańsk "
        "using a Multi-Agent System with real-time data from GIOŚ API."
    )
    st.sidebar.markdown("*Data refreshes every 5 minutes*")
    
    # Get data with loading indicator
    with st.spinner("🔄 Fetching real-time air quality data... (this may take up to 1 minute)"):
        data = get_air_quality_data()
    
    if data is None:
        st.error("❌ Failed to fetch air quality data. Please try again.")
        return
    
    # Extract DataFrames
    city_summary = data['city_summary']
    measurements = data['measurements']
    
    # Section 1: City Overview Cards
    st.header("📊 Current Air Quality")
    
    cols = st.columns(3)
    
    for idx, (_, city_data) in enumerate(city_summary.iterrows()):
        with cols[idx]:
            display_city_card(city_data)
    
    st.markdown("---")
    
    # Section 2: Charts
    st.header("📈 Detailed Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = create_pollutant_chart(measurements)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No pollutant data available for chart")
    
    with col2:
        st.subheader("AQI Levels")
        gauge_cols = st.columns(3)
        for idx, (_, city_data) in enumerate(city_summary.iterrows()):
            with gauge_cols[idx]:
                fig = create_aqi_gauge(city_data)
                st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Section 3: Detailed Data Table
    st.header("📋 Measurement Details")
    
    display_cols = ['city', 'station_name', 'parameter_code', 'value', 'aqi_category']
    available_cols = [col for col in display_cols if col in measurements.columns]
    
    st.dataframe(
        measurements[available_cols].sort_values(['city', 'parameter_code']),
        use_container_width=True,
        hide_index=True
    )
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}* | "
        f"*Data source: GIOŚ (Polish Chief Inspectorate of Environmental Protection)*"
    )


if __name__ == "__main__":
    main()