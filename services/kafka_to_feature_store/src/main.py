from quixstreams import Application
from config import config
import json
from loguru import logger
from datetime import datetime
from hopsworks_api import push_data_to_feature_store

def kafka_to_feature_store(
    kafka_topic: str,
    kafka_broker_address: str,
    feature_group_name: str,
    feature_group_version: int,
    buffer_size: int = 1 #contains the trades that we want to write to the feature store at once
)-> None:
    """
    Stream data from the ohlc Kafka topic to the hopsworks feature store in the specified feature group
    Args:
        kafka_topic (str): the name of the Kafka topic where the OHLC data is stored
        kafka_broker_address (str): the address of the Kafka broker
        feature_group_name (str): the name of the feature group
        feature_group_version (int): the version of the feature group
        buffer_size (int): the number of messages to buffer before writing to the feature store
    Returns:
        None
    """
    # Create a new application
    app = Application(
        broker_address=kafka_broker_address,
        consumer_group="kafka_to_feature_store",
        auto_offset_reset="earliest"
    )
    logger.info("Application created")
    #initialize the buffer
    buffer = []
    #TODO: handle the case where the buffer is not full and there is nor more expected data to come in 
    # as with the current implementation we may miss the last few messages if the buffer is not full (up to buffer_size-1 messages)
    # Create a consumer and start a polling loop
    with app.get_consumer() as consumer: #creating a consumer with the predifined quixstreams get_consumer() method
        consumer.subscribe(topics=[kafka_topic]) #subscribing to the topic
        logger.info(f"Subscribed to topic {kafka_topic}")
        while True:
            msg = consumer.poll(1) #how much time to wait for a message before skipping to the next iteration
            if msg is None:
                logger.info("No new messages comes in!")
                continue
            elif msg.error():
                logger.info('Kafka error:', msg.error())
                continue
            else:
                # step 1 -> parse the data from the topic into a dictionary
                try:
                    ohlc = json.loads(msg.value().decode('utf-8'))
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode JSON: {e}")
                    continue
                #append the data to the buffer
                buffer.append(ohlc)
                logger.info(f"current buffer length: {len(buffer)}")
                #breakpoint()
                #check if the buffer is full
                if len(buffer) >= buffer_size:
                    # step 2 -> store the data in the feature store
                    push_data_to_feature_store(
                        data=buffer, 
                        feature_group_name=feature_group_name, 
                        feature_group_version=feature_group_version,
                        online_or_offline = "offline"
                    )
                    #clear the buffer
                    buffer = []

                # step 2 -> store the data in the feature store
                # push_data_to_feature_store(
                #     data=ohlc, 
                #     feature_group_name=feature_group_name, 
                #     feature_group_version=feature_group_version,
                #     online_or_offline = "online"
                # )

            value = msg.value()
            # Do some work with the value here ...

            # Store the offset of the processed message on the Consumer 
            # for the auto-commit mechanism.
            # It will send it to Kafka in the background.
            # Storing offset only after the message is processed enables at-least-once delivery
            # guarantees.
            consumer.store_offsets(message=msg)# telling kafka that this consumer group has red up until this message

if __name__ == "__main__":
    try: 
        kafka_to_feature_store(
            kafka_topic = config.kafka_topic,
            kafka_broker_address = config.kafka_broker_address,
            feature_group_name = config.feature_group_name,
            feature_group_version = config.feature_group_version,
            buffer_size = config.buffer_size
        )
    except KeyboardInterrupt:
        logger.info("Stopping the application...")
    # kafka_to_feature_store(
    #     kafka_topic = config.kafka_topic,
    #     kafka_broker_address = config.kafka_broker_address,
    #     feature_group_name = config.feature_group_name,
    #     feature_group_version = config.feature_group_version,
    #     buffer_size = config.buffer_size
    # )
