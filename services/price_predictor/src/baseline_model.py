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
        #making a copy of the input dataframe to avoid modifying the original dataframe
        X_= X.copy()
        # creating and setting the target column to 0, meaning all the prices remain the same, no change at all
        X_['target'] = 0
        #This will be the predictions of the Baseline model, i.e the baselinemodel will always predict that the price will remain the same
        return X_['target']