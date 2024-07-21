import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# This will load the environment variables from the .env file.
load_dotenv()
class Config(BaseSettings):
    kafka_broker_address: Optional[str] = os.environ.get('KAFKA_BROKER_ADDRESS')
    kafka_input_topic_name: str = 'trades'
    kafka_output_topic_name: str = 'ohlc'
    ohlc_window_secs: int = os.environ.get('OHLC_WINDOW_SECS')
    


config = Config()
