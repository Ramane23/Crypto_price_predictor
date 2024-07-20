from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    kafka_broker_address: Optional[str] = 'localhost:9092'
    kafka_topic_name: str = 'trades'
    product_id: str = 'BTC/USD'
    

config = Config()
