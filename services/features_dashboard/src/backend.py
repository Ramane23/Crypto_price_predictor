from typing import List, Dict

import hopsworks
#from hopsworks.feature_store import FeatureView
from hsfs.client.exceptions import FeatureStoreException
import pandas as pd
from loguru import logger

from config import config

logger.debug('Backend module loaded')
logger.debug(f'Config: {config.model_dump()}')

# Authenticate with Hopsworks API
project = hopsworks.login(
    project=config.hopsworks_project_name,
    api_key_value=config.hopsworks_api_key,
)

# Get the feature store
feature_store = project.get_feature_store()


def get_feature_view():
    """
    Returns the feature view object that reads data from the feature store
    """
    # # Authenticate with Hopsworks API
    # project = hopsworks.login(
    #     project=config.hopsworks_project_name,
    #     api_key_value=config.hopsworks_api_key,
    # )

    # # Get the feature store
    # feature_store = project.get_feature_store()

    # Get the feature group we want to read features from
    feature_group = feature_store.get_feature_group(
        name=config.feature_group_name,
        version=config.feature_group_version,
    )

    # Get (possibly first create) the feature view that will read features from our
    # feature group
    feature_view = feature_store.get_or_create_feature_view(
        name=config.feature_view_name,
        version=config.feature_view_version,
        query=feature_group.select_all() # select all features from the feature group
    )

    return feature_view


def get_features_from_the_store(
    online_or_offline: str,
) -> pd.DataFrame:
    """
    Fetches the features from the store and returns them as a pandas DataFrame.
    All the config parameters are read from the src.config module

    Args:
        None

    Returns:
        pd.DataFrame: The features as a pandas DataFrame sorted by timestamp (ascending)
    """
    logger.debug('Getting the feature view')
    feature_view = get_feature_view()    

    # For the moment, let's get all rows from this feature group
    if online_or_offline == 'offline':
        try:
            features: pd.DataFrame = feature_view.get_batch_data()

        except FeatureStoreException:
            # breakpoint()
            # retry the call with the use_hive option. This is what Hopsworks recommends
            features: pd.DataFrame = feature_view.get_batch_data(read_options={"use_hive": True})
    else:
        # we fetch from the online feature store.
        # we need to build this list of dictionaries with the primary keys
        features = feature_view.get_feature_vectors(
            entry=get_primary_keys(last_n_minutes=20),
            return_type="pandas"
        )

    # sort the features by timestamp (ascending)
    features = features.sort_values(by='timestamp')

    # breakpoint()

    # Python trick: You can also do a sort inplace. I think with this you avoid copying data and it is
    # paster
    # features.sort_values(by='timestamp', inplace=True)

    return features


def get_primary_keys(last_n_minutes: int) -> List[Dict]:
    """
    Returns a list of dictionaries with the primary keys of the rows we want to fetch
    """
    # get current UTC in milliseconds and floor it to the previous minute
    import time
    current_utc = int(time.time() * 1000)
    current_utc = current_utc - (current_utc % 60000)

    # generate a list of timestamps in miliseconds for the last 'last_n_minutes' minutes
    timestamps = [current_utc - i * 60000 for i in range(last_n_minutes)]
    
    # I've just sent the `kafka_to_feature_store` service pushing a candle for
    # this timestamp for BTC/USD. Let's see if we can actually read it from the online store.
    # timestamps = [1719068640000]

    # primary keys are pairs of product_id and timestamp
    primary_keys = [
        {
            'product_id': config.product_id,
            'timestamp': timestamp,
        } for timestamp in timestamps
    ]

    # breakpoint()

    return primary_keys

if __name__ == '__main__':

    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('--online', action='store_true')
    parser.add_argument('--offline', action='store_true')
    args = parser.parse_args()

    if args.online and args.offline:
        raise ValueError('You cannot pass both --online and --offline')    
    online_or_offline = 'offline' if args.offline else 'online'
    
    from loguru import logger
    data = get_features_from_the_store(online_or_offline)
    
    logger.debug(f'Received {len(data)} rows of data from the Feature Store')

    logger.debug(data.head())
    