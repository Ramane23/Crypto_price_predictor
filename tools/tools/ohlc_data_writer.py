import hopsworks
from hsfs.feature_group import FeatureGroup
from loguru import logger
import pandas as pd

class OhlcDataWriter:
    """
    A class to help us read our OHLC data from the feature store.
    
    The Hopsworks credentials are read from the environment variables.
    - HOPSWORKS_PROJECT_NAME
    - HOPSWORKS_API_KEY
    """
    def __init__(
        self,
        hopsworks_project_name: str,
        hopsworks_api_key: str,
        feature_group_name: str,
        feature_group_version: int,
    ):
        self.feature_group_name = feature_group_name
        self.feature_group_version = feature_group_version
        self.hopsworks_project_name = hopsworks_project_name
        self.hopsworks_api_key = hopsworks_api_key

    def write_from_csv(self, csv_file_path: str):
        """
        Writes the OHLC data from a CSV file to the feature store.
        """
        feature_group = self._get_feature_group()

        # Read the data from the CSV file
        data = pd.read_csv(csv_file_path)

        feature_group.insert(
            data,
            write_options={
                'start_offline_materialization': True
            },
        )

    def _get_feature_group(self) -> FeatureGroup:
        """
        Returns (and possibly creates) the feature group we will be writing to.
        """
        # Authenticate with Hopsworks API
        project = hopsworks.login(
            project=self.hopsworks_project_name,
            api_key_value=self.hopsworks_api_key,
        )

        # Get the feature store
        feature_store = project.get_feature_store()

        feature_group = feature_store.get_or_create_feature_group(
            name=self.feature_group_name,
            version=self.feature_group_version,
            description='OHLC data coming from Kraken',
            primary_key=['product_id', 'timestamp'],
            event_time='timestamp',
            online_enabled=True,
        )

        return feature_group

def main(
    hopsworks_project_name: str,
    hopsworks_api_key: str,
    feature_group_name: str,
    feature_group_version: int,
    csv_file: str,
):
    writer = OhlcDataWriter(
        hopsworks_project_name=hopsworks_project_name,
        hopsworks_api_key=hopsworks_api_key,
        feature_group_name=feature_group_name,
        feature_group_version=feature_group_version,
    )
    writer.write_from_csv(csv_file)
    logger.debug(f'OHLC data from file {csv_file} was saved to {feature_group_name}-{feature_group_version}')

if __name__ == '__main__':

    from fire import Fire
    Fire(main)



        