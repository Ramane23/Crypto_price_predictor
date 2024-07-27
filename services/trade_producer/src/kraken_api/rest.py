import json
from pathlib import Path
from time import sleep
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone

import requests
from loguru import logger

class KrakenRestAPI : 
    """A class used to interact with the Kraken REST API"""

    url = 'https://api.kraken.com/0/public/Trades?pair={product_id}&since={since_sec}'

    def __init__(
            self, 
            product_id: str, 
            last_n_days: int
            ) -> None:
        """Initializes the Kraken REST API
           
        Args: 
            product_ids (List[str]): A list of product ids
            last_n_days (int): The number of days to fetch data from the Kraken API
        
        Returns:
            None
        """
        self.product_id = product_id
        self.from_ms, self.to_ms = self._init_from_to_ms(last_n_days)
        #use it to check if we are done fetching historical data
        self.is_done : bool = False
        #creating an attribute to track the timestamp of the last trade fetched
        self.last_ts_in_ms : int = self.from_ms
        logger.debug(f'Initializing Kraken REST API to fetch data from_ms: {self.from_ms}, to_ms: {self.to_ms}')
    
    @staticmethod #this is used to define a static method, meaning method that can be called on the class without creating an instance of the class
    def _init_from_to_ms(last_n_days: int) -> Tuple[int, int]:
        """
         Returns the from_ms and to_ms timestamps for the historical data.
        These values are computed using today's date at midnight and the last_n_days.

        Args:
            last_n_days (int): The number of days from which we want to get historical data.

        Returns:
        Tuple[int, int]: A tuple containing the from_ms and to_ms timestamps.
        """
        # get the current date at midnight using UTC timezone and remove the time part
        today_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        # today_date to milliseconds
        to_ms = int(today_date.timestamp() * 1000)

        # from_ms is last_n_days ago from today, so
        from_ms = to_ms - last_n_days * 24 * 60 * 60 * 1000

        return from_ms, to_ms

    def get_trades(self) -> List[dict]: 
        """ fetches trades from the Kraken REST API and return them as a list of dictionaries

        Args:
            product_ids (List[str]): _description_

        Returns:
            List[dict]: _description_
        """

        payload = {}
        headers = {'Accept': 'application/json'}
        since_sec = self.last_ts_in_ms // 1000
        url = self.url.format(product_id = self.product_id, since_sec = self.from_ms)
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
            'product_id': self.product_id,
            'price': float(trade[0]),
            'volume': float(trade[1]),
            'time': int(trade[2]*1000) #converting the time to milliseconds
            } for trade in data['result'][self.product_id]
            ]
        #breakpoint()
        #Enuring that the trades are exactly in the time range we want
        trades = [trade for trade in trades if trade['time'] <= (self.to_ms)]
        #check if we are done fetching historical data
        #retrieve the last trade time in milliseconds
        #breakpoint()
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
