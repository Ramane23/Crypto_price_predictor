# In this file I define the UI and the logic of the dashboard
import streamlit as st  # Importing the Streamlit library for building the web application
import pandas as pd  # Importing the pandas library for data manipulation
from loguru import logger  # Importing the loguru library for logging
from time import sleep  # Importing the sleep function to add delays

# Importing custom functions and configurations from other modules
from backend import get_features_from_the_store  # Function to fetch data from the store
from plot import plot_candles  # Function to generate candlestick plots
from config import config  # Configuration settings

# Writing the title of the dashboard
st.write("""
# OHLC features dashboard
""")

# Adding a selectbox to the sidebar to switch between the online store and the offline store
online_or_offline = st.sidebar.selectbox(
    'Select the store',  # Label for the selectbox
    ('online', 'offline')  # Options available in the selectbox
)

# Challenge: add a time range slider to the sidebar to select the time range for which
# we want to display the data
# Pass this parameter to the get_features_from_the_store function to get the data
with st.container():  # Creating a container for the chart placeholder
    placeholder_chart = st.empty()  # Creating an empty placeholder for the chart

# Infinite loop to keep updating the chart
while True:
    # Load the data from the selected store
    data = get_features_from_the_store(online_or_offline)
    logger.debug(f'Received {len(data)} rows of data from the Feature Store')  # Logging the number of rows received

    # Refresh the chart
    with placeholder_chart:  # Using the placeholder to update the chart
        st.bokeh_chart(plot_candles(data))  # Generating and displaying the candlestick chart using Bokeh
    # Sleep for 15 seconds
    sleep(15)  # Adding a delay of 15 seconds before updating the chart again
