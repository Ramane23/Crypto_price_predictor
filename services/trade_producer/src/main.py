import time
from typing import List

from config import config
#from kraken_api.rest import KrakenRestAPIMultipleProducts
from kraken_api.pau_rest import KrakenRestAPIMultipleProducts
from kraken_api.trade import Trade
from kraken_api.pau_websocket import KrakenWebsocketTradeAPI
#from kraken_api.websocket import KrakenWebsocketTradeAPI
from loguru import logger
from quixstreams import Application


def produce_trades(
    kafka_broker_address: str,
    kafka_topic_name: str,
    product_ids: List[str], 
    #product_id: str,
    live_or_historical: str, 
    last_n_days: int 
) -> None:
    """Reads trades from the Kraken websocket API and produces them to a Kafka topic

    Args:
        kafka_broker_address (str): the address of the Kafka broker
        kafka_topic (str): the name of the Kafka topic
        product_ids (List[str]): the list of product ids
        live_or_historical (str): the type of data to fetch from the Kraken API
        last_n_days (int): the number of days to fetch data from the Kraken API
    Returns:
        None
    """
    # Create a new application
    app = Application(broker_address=kafka_broker_address)
    # The topic where we will save the trades
    topic = app.topic(name=kafka_topic_name, value_serializer='json')
    # Create an instance of the KrakenWebsocketTradeAPI
    if live_or_historical == 'live':
        kraken_api = KrakenWebsocketTradeAPI(product_ids=product_ids)
    else:
        kraken_api = KrakenRestAPIMultipleProducts(
            product_ids=product_ids, 
            #from_ms=from_ms, 
            #to_ms=to_ms
            last_n_days=last_n_days
        )
        #breakpoint()
    logger.info('Starting to produce trades to redpanda...')
    # Create a Producer instance
    with app.get_producer() as producer:  # application that writes to the Kafka topics are called producers
        while True:
            #check if we are done fetching historical data
            if kraken_api.done():
                logger.info('Done fetching historical data')
                break

            # Get trades from the Kraken API
            trades: List[Trade] = kraken_api.get_trades()
            for trade in trades:
                # Serialize an event using the defined Topic
                message = topic.serialize(
                    key=trade.product_id,
                    value=trade.model_dump(), #transforming a pydantic BaseModel object (as the trade class inherit from it) to a dictionary
                    #timestamp_ms=trade.timestamp_ms
                    #key=trade['product_id'], 
                    #value=trade,
                    #timestamp_ms=trade["time"] #considering the timestamp of the trade as the timestamp of the messaage in the Kafka topic
                )
                #breakpoint()
                # Produce a message into the Kafka topic
                producer.produce(
                    topic=topic.name, 
                    value=message.value, 
                    key=message.key,
                    #timestamp=message.timestamp #considering the timestamp of the trade as the timestamp of the messaage in the Kafka topic
                )
                #breakpoint()
                logger.info(f'Trade sent: {trade}')
        
                # Wait for 1 second
                time.sleep(1)


if __name__ == '__main__':
    try: 
        produce_trades(
            kafka_broker_address=config.kafka_broker_address,
            kafka_topic_name=config.kafka_topic_name,
            product_ids=config.product_ids,
            #extra argument needed for fetching trades from the Kraken REST API
            live_or_historical=config.live_or_historical,
            last_n_days=config.last_n_days
        )
    except KeyboardInterrupt:
        logger.info("Exiting...")
