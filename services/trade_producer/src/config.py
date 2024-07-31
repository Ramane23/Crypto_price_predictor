#import os
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings

# This will load the environment variables from the .env file.
#load_dotenv()

class Config(BaseSettings):
    kafka_broker_address: Optional[str] = None #because during deployment on quix cloud later, we won't need to specify the kafka broker address as it will automatically create a client for us
    kafka_topic_name: str 
    product_ids: List[str]
    #product_id: str = 'ETH/USD'
    live_or_historical: str 
    last_n_days: Optional[int] = 1 #Optional because it is not required for live data
    # Validate the live_or_historical argument using a pydantic field validator
    @field_validator('live_or_historical')
    @classmethod # This is a class method, meaning it is called on the class itself, not on an instance of the class
    def validate_live_or_historical(cls, value):
        assert value in {
            'live',
            'historical',
        }, f'Invalid value for live_or_historical: {value}'
        return value

config = Config()
