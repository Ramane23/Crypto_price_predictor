from typing import Dict, List

from config import config
from kraken_api import KrakenWebsoceketTradeAPI
from loguru import logger
from quixstreams import Application


def produce_trades(
    kafka_broker_address: str,
    kafka_topic_name: str,
    product_id: str = config.product_id,
) -> None:
    """Reads trades from the Kraken websocket API and produces them to a Kafka topic

    Args:
        kafka_broker_address (str): the address of the Kafka broker
        kafka_topic (str): the name of the Kafka topic
    Returns:
        None
    """
    # Create a new application
    app = Application(broker_address=kafka_broker_address)
    # The topic where we will save the trades
    topic = app.topic(name=kafka_topic_name, value_serializer='json')
    # Create an instance of the KrakenWebsocketTradeAPI
    kraken_api = KrakenWebsoceketTradeAPI(product_id=product_id)
    logger.info('Starting to produce trades to redpanda...')
    # Create a Producer instance
    with app.get_producer() as producer:  # application that writes to the Kafka topics are called producers
        while True:
            # Get trades from the Kraken API
            trades: List[Dict] = kraken_api.get_trades()
            for trade in trades:
                # Serialize an event using the defined Topic
                message = topic.serialize(key=trade['product_id'], value=trade)
                # Produce a message into the Kafka topic
                producer.produce(topic=topic.name, value=message.value, key=message.key)
                logger.info(f'Trade sent: {trade}')
                import time

                # Wait for 1 second
                time.sleep(1)


if __name__ == '__main__':
       produce_trades(
            kafka_broker_address=config.kafka_broker_address,
            kafka_topic_name=config.kafka_topic_name,
            product_id=config.product_id,
       )