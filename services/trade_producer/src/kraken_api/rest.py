import json
from pathlib import Path
from time import sleep
from typing import Dict, List, Optional, Tuple

import requests
from loguru import logger

class KrakenRestAPI : 
    """A class used to interact with the Kraken REST API"""

    url = 'https://api.kraken.com/0/public/Trades?pair={product_ids}&since={since_ms}'

    def __init__(
            self, 
            product_ids: List[str],
            from_ms : int,
            to_ms : int 
            ) -> None:
        """Initializes the Kraken REST API
           
        Args: 
            product_ids (List[str]): A list of product ids
            from_ms (int): The start time in milliseconds
            to_ms (int): The end time in milliseconds
        
        Returns:
            None
        """
        self.product_ids = product_ids
        self.from_ms : int = from_ms
        self.to_ms : int = to_ms
        #use it to check if we are done fetching historical data
        self.is_done : bool = False
        pass

    def get_trades(self) -> List[dict]: 
        """ fetches trades from the Kraken REST API and return them as a list of dictionaries

        Args:
            product_ids (List[str]): _description_

        Returns:
            List[dict]: _description_
        """

        payload = {}
        headers = {'Accept': 'application/json'}
        url = self.url.format(product_ids = self.product_ids[0], since_ms = self.from_ms)
        #breakpoint()
        response = requests.request("GET", url, headers=headers, data=payload)
        #parse string into dicrionary
        data = json.loads(response.text)
        #breakpoint()
        #check if the error section of the response is empty
        #if data['error'] is not []:
            #raise an exception if the error section is not empty
            #raise Exception(data['error'])
        #else:
            #trades = []
            #for trade in data['result'][self.product_ids[0]]:
                #trades.append({
                    #'product_id': self.product_ids[0],
                    #'price': trade[0],
                    #'volume': trade[1],
                    #'time': trade[2]
                #})
            #using a list comprehension to get the trades
        trades = [
            {
            'product_id': self.product_ids[0],
            'price': float(trade[0]),
            'volume': float(trade[1]),
            'time': int(trade[2]*1000)
            } for trade in data['result'][self.product_ids[0]]
            ]

        #check if we are done fetching historical data
        #retrieve the last trade time in milliseconds
        last_ts_in_ms = trades[-1]['time']
        #breakpoint()
        #checking if the current time is less or equal to the last trade time
        if self.to_ms <= last_ts_in_ms:
            #if yes, then we are done fetching historical data
            self.is_done = True
        #how many trades were fetched
        logger.debug(f'fetched {len(trades)} trades')
        #when was the last trade fetched
        logger.debug(f'last trade time: {last_ts_in_ms}')
        return trades

    def done(self) -> bool:
        """Checks if we are done fetching historical data

        Returns:
            bool: True if we are done fetching historical data, False otherwise
        """
        return self.is_done
