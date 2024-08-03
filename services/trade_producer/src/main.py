from typing import List

from loguru import logger
from quixstreams import Application

# from src import config
from config import config
from kraken_api.trade import Trade
from kraken_api.websocket import KrakenWebsocketTradeAPI
from kraken_api.pau_rest import KrakenRestAPIMultipleProducts


def produce_trades(
    kafka_broker_addres: str,
    kafka_topic_name: str,
    product_ids: List[str],
    live_or_historical: str,
    last_n_days: int,
) -> None:
    """
    Reads trades from the Kraken websocket API and saves them into a Kafka topic.

    Args:
        kafka_broker_addres (str): The address of the Kafka broker.
        kafka_topic (str): The name of the Kafka topic.
        product_ids (List[str]): The product IDs for which we want to get the trades.
        live_or_historical (str): Whether we want to get live or historical data.
        last_n_days (int): The number of days from which we want to get historical data.

    Returns:
        None
    """
    # Trick
    # This input parameter validation was first done here, but then moved to the
    # Config class in src.config, using Pydantic Settings.
    # I recommend you validate config parameters in your Config object using Pydantic Settings
    # assert live_or_historical in {
    #     'live',
    #     'historical',
    # }, f'Invalid value for live_or_historical: {live_or_historical}'

    app = Application(broker_address=kafka_broker_addres)

    # the topic where we will save the trades
    topic = app.topic(name=kafka_topic_name, value_serializer='json')

    logger.info(f'Creating the Kraken API to fetch data for {product_ids}')

    # Create an instance of the Kraken API
    if live_or_historical == 'live':
        kraken_api = KrakenWebsocketTradeAPI(product_ids=product_ids)
    else:
        # I need historical data, so

        kraken_api = KrakenRestAPIMultipleProducts(
            product_ids=product_ids,
            last_n_days=last_n_days,
            n_threads=1,  # len(product_ids),
            cache_dir=config.cache_dir_historical_data,
        )

    logger.info('Creating the producer...')

    # Create a Producer instance
    with app.get_producer() as producer:
        while True:
            # check if we are done fetching historical data
            if kraken_api.done():
                logger.info('Done fetching historical data')
                break

            # breakpoint()

            # Get the trades from the Kraken API
            trades: List[Trade] = kraken_api.get_trades()

            # Challenge 1: Send a heartbeat to Prometheus to check the service is alive
            # Challenge 2: Send an event with trade latency to Prometheus, to monitor the trade latency

            for trade in trades:
                # Serialize an event using the defined Topic
                message = topic.serialize(
                    key=trade.product_id,
                    value=trade.model_dump(),
                )

                # Produce a message into the Kafka topic
                producer.produce(
                    topic=topic.name,
                    value=message.value,
                    key=message.key,
                )

                logger.debug(f'{trade.model_dump()}')

            # logger.info(f'Produced {len(trades)} trades to Kafka topic {topic.name}')


if __name__ == '__main__':
    # You can also pass configuration parameters using the command line
    # use argparse to parse the kafka_broker_address
    # and kafka_topic from the command line
    # from argparse import ArgumentParser
    # parser = ArgumentParser()
    # parser.add_argument('--kafka_broker_address', type=str, required=False, default='localhost:9092')
    # parser.add_argument('--kafka_topic', type=str, required=True)
    # args = parser.parse_args()

    logger.debug('Configuration:')
    logger.debug(config.model_dump())

    # import os
    # breakpoint()

    try:
        produce_trades(
            kafka_broker_addres=config.kafka_broker_address,
            kafka_topic_name=config.kafka_topic_name,
            product_ids=config.product_ids,
            # extra parameters I need when running the trade_producer against
            # historical data from the KrakenREST API
            live_or_historical=config.live_or_historical,
            last_n_days=config.last_n_days,
        )
    except KeyboardInterrupt:
        logger.info('Exiting...')