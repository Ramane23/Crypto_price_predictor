import json
from datetime import datetime, timezone
from time import sleep
from typing import Dict, List, Tuple

import requests
from loguru import logger


#creating a class to fetch data from the Kraken REST API for multiple products, using the initia KrakenRestAPI class
class KrakenRestAPIMultipleProducts:
    def __init__(
        self,
        product_ids: List[str],
        last_n_days: int,
        #n_threads: Optional[int] = 1,
        #cache_dir: Optional[str] = None,
    ) -> None:
        self.product_ids = product_ids
        #create an instance of the KrakenRestAPI for each product_id we want to fetch data for
        self.kraken_apis = [
            KrakenRestAPI(
                product_id=product_id, last_n_days=last_n_days
            )
            for product_id in product_ids
        ]

        #self.n_threads = n_threads

    def get_trades(self) -> List[Dict]:
        """Fetches trade data from the Kraken REST API for all product ids
        Args:
            None
        Returns:
            List[Dict]: A list of trades for all product ids
        """
        trades : List[Dict] = []
        #fetch trades for each product id as long as we are not done fetching h
        for kraken_api in self.kraken_apis:
            if kraken_api.done():
                continue
            else: 
                trades = kraken_api.get_trades()# use the get_trades method of the KrakenRestAPI class to fetch trades
        return trades
    
    def done(self) -> bool:
        """Checks if we are done fetching historical data for all product ids
        Args:
            None
        Returns:
            bool: True if we are done fetching historical data for all product ids, False otherwise"""
        for kraken_api in self.kraken_apis:
            #as long as one of the kraken_apis is not done fetching historical data
            if not kraken_api.done():
                return False
            #if all of the kraken_apis are done fetching historical data
        return True

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
        url = self.url.format(product_id = self.product_id, since_sec = since_sec)
        #breakpoint()
        response = requests.request("GET", url, headers=headers, data=payload)
        #parse string into dicrionary
        data = json.loads(response.text)
        #breakpoint()
         # TODO: Error handling
        # It can happen that we get an error response from KrakenRESTAP like the following:
        # data = {'error': ['EGeneral:Too many requests']}
        # To solve this have several options
        #
        # Option 1. Check if the `error` key is present in the `data` and has
        # a non-empty list value. If so, we could raise an exception, or even better, implment
        # a retry mechanism, using a library like `retry` https://github.com/invl/retry
        # Option 2. Simply slow down the rate at which we are making requests to the Kraken API,
        # and cross your fingers.
        # Option 3. Implement both Option 1 and Option 2, so you don't need to cross your fingers.
        # Here is an example of how you could implement Option 2
        if ('error' in data) and ('EGeneral:Too many requests' in data['error']):
                # slow down the rate at which we are making requests to the Kraken API
                logger.info('Too many requests. Sleeping for 30 seconds')
                sleep(30)

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
        #slowing down the rate at which we are making requests to the Kraken API
        sleep(1)
        return trades

    def done(self) -> bool:
        """Checks if we are done fetching historical data

        Returns:
            bool: True if we are done fetching historical data, False otherwise
        """
        return self.is_done
