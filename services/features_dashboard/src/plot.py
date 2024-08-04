import pandas as pd  # Importing the pandas library for data manipulation and analysis
from bokeh.plotting import figure  # Importing the figure function from Bokeh for creating plots 

from datetime import timedelta  # Importing timedelta for time-based calculations
from typing import Optional  # Importing Optional for type hinting optional parameters

def plot_candles(
    df: pd.DataFrame,
    window_seconds: Optional[int] = 60,
    title: Optional[str] = '',
) -> figure:
    """Generates a candlestick plot using the provided data in `df` and the
    Bokeh library

    Args:
        df (pd.DataFrame): DataFrame containing the candlestick data with columns
            - open: Opening price
            - high: Highest price
            - low: Lowest price
            - close: Closing price

        window_seconds (Optional[int]): Time window in seconds for each candlestick
        title (Optional[str]): Title of the plot

    Returns:
        figure.Figure: Bokeh figure with candlestick and Bollinger bands
    """
    # Convert the 'timestamp' column in unix milliseconds to a datetime object
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')

    # Boolean arrays for increasing and decreasing candlesticks
    inc = df.close > df.open
    dec = df.open > df.close

    # Band width in milliseconds
    w = 1000 * window_seconds / 2

    # Tools for the Bokeh plot
    TOOLS = 'pan,wheel_zoom,box_zoom,reset,save'

    # Set the x-axis range to include some padding before and after the data range
    x_max = df['date'].max() + timedelta(minutes=5)
    x_min = df['date'].min() - timedelta(minutes=5)

    # Create a new figure with datetime x-axis, specified tools, and given title
    p = figure(
        x_axis_type='datetime',
        tools=TOOLS,
        width=1000,
        title=title,
        x_range=(x_min, x_max),
    )
    p.grid.grid_line_alpha = 0.3  # Set grid line transparency

    # Add vertical line segments for high and low prices
    p.segment(df.date, df.high, df.date, df.low, color='black')

    # Add vertical bars for increasing candlesticks
    p.vbar(
        df.date[inc],  # x-coordinates for increasing candlesticks
        w,  # Width of the bars
        df.open[inc],  # Bottom y-coordinates (opening prices)
        df.close[inc],  # Top y-coordinates (closing prices)
        fill_color='#70bd40',  # Fill color for increasing bars
        line_color='black',  # Border color for bars
    )

    # Add vertical bars for decreasing candlesticks
    p.vbar(
        df.date[dec],  # x-coordinates for decreasing candlesticks
        w,  # Width of the bars
        df.open[dec],  # Top y-coordinates (opening prices)
        df.close[dec],  # Bottom y-coordinates (closing prices)
        fill_color='#F2583E',  # Fill color for decreasing bars
        line_color='black',  # Border color for bars
    )

    return p  # Return the Bokeh figure
