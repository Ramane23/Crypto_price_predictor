import pandas as pd


def interpolate_missing_candles(
    ohlc_data: pd.DataFrame,
    ohlc_window_sec: int,
) -> pd.DataFrame:
    """
    Interpolates missing candles in the OHLC data.

    Args:
        ohlc_data (pd.DataFrame): The OHLC data.
        ohlc_window_sec (int): The size of the window in seconds.

    Returns:
        pd.DataFrame: The OHLC data with the missing candles interpolated.
    """
    # Python trick!
    # We use inplace to avoid copying the data, which should be more efficient
    ohlc_data.set_index('timestamp', inplace=True)
    # otherwise you can do a copy. This is less efficient.
    # ohlc_data = ohlc_data.set_index('timestamp')
    
    # complete list of timestamps for which we need to have rows in our dataframe
    from_ms = ohlc_data.index.min()
    to_ms = ohlc_data.index.max()
    labels = range(from_ms, to_ms, ohlc_window_sec*1000)
    # reindex the dataframe to add missing rows
    ohlc_data = ohlc_data.reindex(labels)

    # interpolate missing values using forward fill for close prices
    ohlc_data['close'].ffill(inplace=True)

    # if ohlc_data['open] is null use the ohlc_data['close'] value
    ohlc_data['open'].fillna(ohlc_data['close'], inplace=True)
    # do the same for high and low
    ohlc_data['high'].fillna(ohlc_data['close'], inplace=True)
    ohlc_data['low'].fillna(ohlc_data['close'], inplace=True)
    
    # we have to forward fill the product_id as well
    ohlc_data['product_id'].ffill(inplace=True)

    # reset the index
    ohlc_data.reset_index(inplace=True)

    # let's make sure we have no missing datetimes
    ohlc_data['datetime'] = pd.to_datetime(ohlc_data['timestamp'], unit='ms')
    
    return ohlc_data


def create_target_metric(
    ohlc_data: pd.DataFrame,
    ohlc_window_sec: int,
    prediction_window_sec: int,
) -> pd.DataFrame:
    """
    Creates the target metric by 
    - discretizing the close price in the next prediction_window_sec
    - using the discretization_thresholds
    - and adds the final column in the output dataframe

    Args:
        ohlc_data (pd.DataFrame): The OHLC data.
        ohlc_window_sec (int): The size of the window in seconds.
        discretization_thresholds (list): The thresholds to discretize the close price.
        prediction_window_sec (int): The size of the prediction window in seconds.

    Returns:
        pd.DataFrame: The OHLC data with the target metric.
    """
    # check that prediction_window_sec is a multiple of ohlc_window_sec
    assert prediction_window_sec % ohlc_window_sec == 0, \
        'prediction_window_sec must be a multiple of ohlc_window_sec'

    n_candles_into_future = prediction_window_sec // ohlc_window_sec

    # create a new column with the percentage change in the close price n_candles_into_future
    ohlc_data['close_pct_change'] = ohlc_data['close'].pct_change(n_candles_into_future)
    
    # shift the target column by n_candles_into_future to have the target for the current candle
    ohlc_data['target'] = ohlc_data['close_pct_change'].shift(-n_candles_into_future)

    # drop the close_pct_change column
    ohlc_data.drop(columns=['close_pct_change'], inplace=True)

    # Anton Javelosa asked:
    # "Won't n rows at the end have blank targets? After the shift up?"
    # Yes, you are right. Let's drop them before returning the dataframe
    # Thanks Anton!
    ohlc_data.dropna(subset=['target'], inplace=True)

    return ohlc_data