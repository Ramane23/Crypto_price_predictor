import os
from typing import Optional
from pydantic_settings import BaseSettings
import dotenv

# Load the environment variables from the .env file
dotenv.load_dotenv(dotenv.find_dotenv())

class Config(BaseSettings):
    """
    Configuration class for the price predictor service.
    """

    comet_ml_api_key: str = os.environ.get("COMET_ML_API_KEY")
    comet_ml_project_name: str = os.environ.get("COMET_ML_PROJECT_NAME")
    comet_ml_workspace: str = os.environ.get("COMET_ML_WORKSPACE")


config = Config()
