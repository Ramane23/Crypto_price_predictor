from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator
import os
from dotenv import load_dotenv

# This will load the environment variables from the .env file.
load_dotenv()

class Config(BaseSettings):
    kafka_broker_address: Optional[str] = os.environ.get('KAFKA_BROKER_ADDRESS')
    kafka_topic_name: str = 'trades'
    #product_ids: List[str]= ['ETH/USD', "ETH/EUR", "BTC/USD", "BTC/EUR"]
    product_id: str = 'ETH/USD'
    live_or_historical: str = os.environ.get('LIVE_OR_HISTORICAL')
    last_n_days: int = 7
    # Validate the live_or_historical argument using a pydantic field validator
    @field_validator('live_or_historical')
    @classmethod
    def validate_live_or_historical(cls, value):
        assert value in {
            'live',
            'historical',
        }, f'Invalid value for live_or_historical: {value}'
        return value

config = Config()
