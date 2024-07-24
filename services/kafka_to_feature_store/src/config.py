import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# This will load the environment variables from the .env file.
load_dotenv()

class Config(BaseSettings):
    kafka_broker_address: Optional[str] = os.environ.get("KAFKA_BROKER_ADDRESS")
    kafka_topic: str = "ohlc"
    kafka_consumer_group: str = "kafka_to_feature_store"
    feature_group_name: str = "ohlc_feature_group_1"
    feature_group_version: int = 1
    hopsworks_project_name: str = os.environ.get("HOPSWORKS_PROJECT_NAME")
    hopsworks_api_key: str = os.environ.get("HOPSWORKS_API_KEY")

config = Config()

print(config.kafka_broker_address)