export KAFKA_TOPIC="ohlc_historical"
export KAFKA_CONSUMER_GROUP="ohlc_historical_consumer_group"
export FEATURE_GROUP_NAME="ohlc_feature_group"
export FEATURE_GROUP_VERSION=1

# number of elements we save at once to the Hopsworks feature store
# This value of 10080 corresponds to saving batches of 1 week of data at once
export BUFFER_SIZE=5000

# this way we tell  our `kafka_to_feature_store` service to save features to the
# offline store, because we are basically generating historical data we will use for
# training our models
export LIVE_OR_HISTORICAL="historical"

export SAVE_EVERY_N_SEC=600

export CREATE_NEW_CONSUMER_GROUP=true