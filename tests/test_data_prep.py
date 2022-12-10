import unittest

import pandas as pd

from src.data_prep import clean_df, data_preparation


class MyTest(unittest.TestCase):
    def test_data_preparation_pipline(self):
        df = self.get_data()
        train, test, label = data_preparation(df, 0.2)

        assert label == "fare_amount"

        # check for expected types
        assert isinstance(train, pd.DataFrame)
        assert isinstance(test, pd.DataFrame)

    def test_clean_df(self):
        df = self.get_data()
        df = clean_df(df)

        # check if df contains unexpected values
        assert 0 in df["fare_amount"]
        assert 0 in df["pickup_longitude"]

    def get_data(self):
        return pd.DataFrame(
            {
                "key": [
                    "2009-06-15 17:26:21.0000001",
                    "2010-01-05 16:52:16.0000002",
                    "2011-08-18 00:35:00.00000049",
                ],
                "fare_amount": [4.5, 16.9, 5.7],
                "pickup_datetime": [
                    "2009-06-15 17:26:21 UTC",
                    "2010-01-05 16:52:16 UTC",
                    "2011-08-18 00:35:00 UTC",
                ],
                "pickup_longitude": [-73.844311, -74.016048, -73.982738],
                "pickup_latitude": [40.721319, 40.711303, 40.76127],
                "dropoff_longitude": [-73.84161, -73.979268, -73.991242],
                "dropoff_latitude": [40.712278, 40.782004, 40.750562],
                "passenger_count": [1, 1, 2],
            }
        )
