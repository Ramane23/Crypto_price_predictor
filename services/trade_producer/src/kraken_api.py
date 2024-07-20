import json

from loguru import logger
from websocket import create_connection


class KrakenWebsoceketTradeAPI:
    """
    A class used to interact with a Kraken websocket API
    """

    URL = 'wss://ws.kraken.com/v2'

    def __init__(
        self,
        product_id: str,
    ):
        self.product_id = product_id
        # Create a websocket connection
        self._ws = create_connection(self.URL)
        logger.info('connection established')

        # Subscribe to the trade channel
        self._subscribe(product_id)

    def _subscribe(self, product_id: str):
        """Subscribe to the trade channel of a product"""
        logger.info(f'subscribing to trade channel for {product_id}')
        # Subscribe to the trade channel
        msg = {
            'method': 'subscribe',
            'params': {'channel': 'trade', 'symbol': [product_id], 'snapshot': False},
        }
        # Send the message
        self._ws.send(json.dumps(msg))
        logger.info('subscribed to trade channel successfully!')

        # ignore the first two messages
        _ = self._ws.recv()
        _ = self._ws.recv()

    def get_trades(self):
        """Get trades from the Kraken API"""
        # Get the response from the websocket API
        message = self._ws.recv()

        # filter out the heartbeat messages
        if 'heartbeat' in message:
            # return an empty list when a heartbeat message is received
            return []

        # parse the message as a dictionary
        message = json.loads(message)

        # print("received response", message)

        # Extracting the prices, quantities and timestamps of the trades
        trades = []
        for trade in message['data']:
            # append the trade to the list of trades
            trades.append(
                {
                    'product_id': self.product_id,
                    'price': trade['price'],
                    'volume': trade['qty'],
                    'timestamp': trade['timestamp'],
                }
            )
        return trades
