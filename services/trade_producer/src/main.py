from quixstreams import Application
from typing import List, Dict
from kraken_api import KrakenWebsoceketTradeAPI

def produce_trades(
        kafka_broker_address: str,
        kafka_topic_name: str,
)->  None: 
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
    #Create an instance of the KrakenWebsocketTradeAPI
    kraken_api = KrakenWebsoceketTradeAPI(product_id="BTC/USD")
    
    # Create a Producer instance
    with app.get_producer() as producer: #application that writes to the Kafka topics are called producers
        while True:
            #Get trades from the Kraken API
            trades: List[Dict] = kraken_api.get_trades()
            for trade in trades:
                # Serialize an event using the defined Topic 
                message = topic.serialize(key=trade["product_id"], value=trade)
                # Produce a message into the Kafka topic
                producer.produce(
                    topic=topic.name, 
                    value=message.value,
                    key=message.key
                )
                print("message sent!")
                import time
                # Wait for 1 second
                time.sleep(1)
            

if __name__ == "__main__":
    # Define the Kafka broker address
    kafka_broker_address = "localhost:19092"
    # Define the Kafka topic name
    kafka_topic_name = "trades"
    # Produce trades to the Kafka topic
    produce_trades(kafka_broker_address, kafka_topic_name)


     