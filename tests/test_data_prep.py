import pandas as pd

from src.data_prep import *


def test_data_preparation_pipline():
    df = get_data()
    train, test, label = data_preparation_pipline(df)

    assert label == 'fare_amount'

    # check for expected types
    assert isinstance(train, pd.DataFrame)
    assert isinstance(test, pd.DataFrame)


def test_clean_df():
    df = get_data()
    df = clean_df(df)

    # check if df contains unexpected values
    assert 0 in df['fare_amount']
    assert 0 in df['pickup_longitude']


def get_data():
    return pd.read_csv('../data/dataset.csv')