from config import config
from loguru import logger
from datetime import timedelta

def trade_to_ohlc(
    kafka_input_topic: str,
    kafka_output_topic: str,
    kafka_broker_address: str,
    ohlc_window_secs: int,
) -> None:
    """Reads trades from a Kafka topic and produces OHLC data to another Kafka topic

    Args:
        kafka_input_topic (str): the name of the Kafka topic where the trades are stored
        kafka_output_topic (str): the name of the Kafka topic where the OHLC data will be stored
        kafka_broker_address (str): the address of the Kafka broker
        ohlc_window_secs (int): the window size in seconds for the OHLC data
    Returns:
        None
    """
    from quixstreams import Application
    app = Application(
        broker_address=kafka_broker_address,
        consumer_group="trade_to_ohlc",#when we are reading from a topic, we need to specify the consumer group
        auto_offset_reset="earliest",#read from the beginning of the topic, meaning all the messages
        #auto_create_reset= "latest" #forget passed messages
    )

    #specify input and output topics
    input_topic = app.topic(name=kafka_input_topic, value_serializer="json")
    output_topic = app.topic(name=kafka_output_topic, value_serializer="json")

    #creating a streaming dataframe from the input topic
    sdf = app.dataframe(input_topic)

    #applying transformations to the incoming data
    def init_ohlc_candle(value: dict) -> dict:
        """
        Initialize the OHLC candle with the first trade
        """
        return {
            'open': value['price'],
            'high': value['price'],
            'low': value['price'],
            'close': value['price'],
            'product_id': value['product_id'],

            # Uncomment this line if you plan to use `volume` in your feature engineering
            # For you Olanrewaju!
            # 'volume': value['volume']
        }
    def update_ohlc_candle(ohlc_candle: dict, trade: dict) -> dict:
        """
        Update the OHLC candle with the new trade and return the updated candle

        Args:
            ohlc_candle : dict : The current OHLC candle
            trade : dict : The incoming trade

        Returns:
            dict : The updated OHLC candle
        """
        return {
            'open': ohlc_candle['open'],
            'high': max(ohlc_candle['high'], trade['price']),
            'low': min(ohlc_candle['low'], trade['price']),
            'close': trade['price'],
            'product_id': trade['product_id'],

            # Uncomment this line if you plan to use `volume` in your feature engineering
            # For you Olanrewaju!
            # 'volume': ohlc_candle['volume'] + trade['volume']
        }
    
    #creating a tumbling window 
    sdf=sdf.tumbling_window(duration_ms=timedelta(seconds = ohlc_window_secs))
    #applying reduce function to the window
    # Create a "reduce" aggregation with "reducer" and "initializer" functions
    sdf=sdf.reduce(reducer=update_ohlc_candle, initializer=init_ohlc_candle).final()

    # extract the open, high, low, close prices from the value key
    # The current format is the following:
    # {
    #     'start': 1717667940000,
    #     'end': 1717668000000,
    #     'value':
    #         {'open': 3535.98, 'high': 3537.11, 'low': 3535.98, 'close': 3537.11, 'product_id': 'ETH/USD'}
    # }
    # But the message format we want is the following:
    # {
    #     'timestamp': 1717667940000, # end of the window
    #     'open': 3535.98,
    #     'high': 3537.11,
    #     'low': 3535.98,
    #     'close': 3537.11,
    #     'product_id': 'ETH/USD',
    # }

    # unpacking the values we want
    sdf['open'] = sdf['value']['open']
    sdf['high'] = sdf['value']['high']
    sdf['low'] = sdf['value']['low']
    sdf['close'] = sdf['value']['close']
    sdf['product_id'] = sdf['value']['product_id']

    # adding the volume key if you plan to use it generate features that depend on it
    # For you Olanrewaju!
    # sdf['volume'] = sdf['value']['volume']

    # adding a timestamp key
    sdf['timestamp'] = sdf['end']

    # let's keep only the keys we want in our final message
    # don't forget to add the volume key if you plan to use it
    sdf = sdf[['timestamp', 'open', 'high', 'low', 'close', 'product_id']]

    #print the transformed data
    sdf = sdf.update(logger.info)
    
    #Publishing the transformed data to the output topic
    sdf = sdf.to_topic(output_topic)

    #quickoff the streaming job
    app.run(sdf)


if __name__ == "__main__":
    #read configuration parameters from config file
    kafka_input_topic = config.kafka_input_topic_name
    kafka_output_topic = config.kafka_output_topic_name
    kafka_broker_address = config.kafka_broker_address
    ohlc_window_secs = config.ohlc_window_secs

trade_to_ohlc(kafka_input_topic, kafka_output_topic, kafka_broker_address, ohlc_window_secs)