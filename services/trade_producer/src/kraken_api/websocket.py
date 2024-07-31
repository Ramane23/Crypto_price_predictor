import json
from typing import List
from loguru import logger
from websocket import create_connection
from kraken_api.trade import Trade
from datetime import datetime, timezone


class KrakenWebsocketTradeAPI:
    """
    A class used to interact with a Kraken websocket API
    """

    URL = 'wss://ws.kraken.com/v2'

    def __init__(
        self,
        #product_ids: List[str]
        product_ids: List[str],
    ):
        self.product_ids = product_ids
        # Create a websocket connection
        self._ws = create_connection(self.URL)
        logger.info('connection established')

        # Subscribe to the trade channel
        self._subscribe(product_ids)
        self.is_done : bool = False

    def _subscribe(self, product_ids : List[str]):
        """Subscribe to the trade channel of a product"""
        logger.info(f'subscribing to trade channel for {product_ids}')
        # Subscribe to the trade channel
        msg = {
            'method': 'subscribe',
            'params': {
                'channel': 'trade', 
                'symbol': product_ids, 
                'snapshot': False
                }
        }
        # Send the message
        self._ws.send(json.dumps(msg))
        logger.info('subscribed to trade channel successfully!')

        # ignore the first two messages
        _ = self._ws.recv()
        _ = self._ws.recv()

    def get_trades(self) -> List[Trade]:
        """Get trades from the Kraken API and return a list of trades"""
        # Get the response from the websocket API
        message = self._ws.recv()
        #breakpoint()
        # filter out the heartbeat messages
        if 'heartbeat' in message:
            # return an empty list when a heartbeat message is received
            return []

        # parse the message as a dictionary
        message = json.loads(message)
        #breakpoint()

        # print("received response", message)

        # Extracting the prices, quantities and timestamps of the trades
        trades = []
        for trade in message['data']:
            # transform the timestamp into milliseconds
            timestamp_ms= self.to_ms(trade['timestamp'])
            # append the trade to the list of trades and using the pydantic Trade class to validate the retrieved trades keys
            trades.append(
                Trade(
                    product_id=trade['symbol'],
                    price=float(trade['price']),
                    volume=float(trade['qty']),
                    timestamp_ms=timestamp_ms,
                )
            )
            # (    {
            #         'product_id': trade['symbol'],
            #         'price': trade['price'],
            #         'volume': trade['qty'],
            #         'timestamp': trade['timestamp'],
            #     }
            # )
        return trades
    
    def done(self) -> bool:
        """Checks if we are done fetching live data

        Returns:
            bool: always returns False as we are never done fetching live data
        """
        return self.is_done

    @staticmethod
    def to_ms(timestamp: str) -> int:
        """
        A function that transforms a timestamps expressed
        as a string like this '2024-06-17T09:36:39.467866Z'
        into a timestamp expressed in milliseconds.

        Args:
            timestamp (str): A timestamp expressed as a string.

        Returns:
        int: A timestamp expressed in milliseconds.
        """
        # parse a string like this '2024-06-17T09:36:39.467866Z'
        # into a datetime object assuming UTC timezone
        # and then transform this datetime object into Unix timestamp
        # expressed in milliseconds
        timestamp = datetime.fromisoformat(timestamp[:-1]).replace(tzinfo=timezone.utc) # remove the 'Z' at the end of the string and converting to UTC timezone
        return int(timestamp.timestamp() * 1000) # transform the timestamp into milliseconds