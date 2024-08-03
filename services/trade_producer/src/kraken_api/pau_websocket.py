import json
from datetime import datetime, timezone
from typing import List

from kraken_api.trade import Trade
from loguru import logger
from websocket import create_connection


class KrakenWebsocketTradeAPI:
    URL = 'wss://ws.kraken.com/v2'

    def __init__(
        self,
        product_ids: List[str],
    ):
        self.product_ids = product_ids

        # establish connection to the Kraken websocket API
        self._ws = create_connection(self.URL)
        logger.info('Connection established')

        # subscribe to the trades for the given `product_id`
        self._subscribe(product_ids)

    def _subscribe(self, product_ids: List[str]):
        """
        Establish connection to the Kraken websocket API and subscribe to the trades for the given `product_id`.
        """
        logger.info(f'Subscribing to trades for {product_ids}')
        # let's subscribe to the trades for the given `product_id`
        msg = {
            'method': 'subscribe',
            'params': {
                'channel': 'trade',
                'symbol': product_ids,
                'snapshot': False,
            },
        }
        self._ws.send(json.dumps(msg))
        logger.info('Subscription worked!')

        # For each product_id we dump
        # the first 2 messages we got from the websocket, because they contain
        # no trade data, just confirmation on their end that the subscription was successful
        for product_id in product_ids:
            _ = self._ws.recv()
            _ = self._ws.recv()

    def get_trades(self) -> List[Trade]:
        """
        Fetches trade data from the Kraken Websocket API and returns a list
        of Trades.
        """
        message = self._ws.recv()

        if 'heartbeat' in message:
            # when I get a heartbeat, I return an empty list
            return []

        # parse the message string as a dictionary
        message = json.loads(message)

        # extract trades from the message['data'] field
        trades = []
        for trade in message['data']:
            # transform the timestamp from Kraken which is a string
            # like '2024-06-17T09:45:38.494012Z' into Unix
            # milliseconds
            timestamp_ms = self.to_ms(trade['timestamp'])

            trades.append(
                Trade(
                    product_id=trade['symbol'],
                    price=trade['price'],
                    volume=trade['qty'],
                    timestamp_ms=timestamp_ms,
                )
            )

        return trades

    def done(self) -> bool:
        """The websocket never stops, so we never stop fetching trades."""
        return False

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

        timestamp = datetime.fromisoformat(timestamp[:-1]).replace(tzinfo=timezone.utc)
        return int(timestamp.timestamp() * 1000)
