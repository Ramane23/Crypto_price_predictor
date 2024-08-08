import pandas as pd


class BaselineModel:

    def __init__(
        self,
        n_candles_into_future: int,
    ):
        self.n_candles_into_future = n_candles_into_future

    def predict(self, X: pd.DataFrame) -> pd.Series:
        """
        To predict the target metric for a given row of X, we compute the last observed
        target metric (aka the last observer price change) and we use that as our
        prediction
        """
        X_= X.copy()

        X_['target'] = 0
        
        return X_['target']