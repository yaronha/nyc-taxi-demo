import mlrun
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


@mlrun.handler(
    outputs=["train_dataset:dataset", "test_dataset:dataset", "label_column"]
)
def data_preparation(dataset: pd.DataFrame, test_size=0.2):
    """A function which preparation the NY taxi dataset

    :param dataset: input dataset dataframe
    :param test_size: the amount (%) of data to use for test

    :return train_dataset, test_dataset, label_column
    """

    # preform all the steps on the dataset
    dataset = clean_df(dataset)
    dataset = add_datetime_info(
        sphere_dist_step(
            sphere_dist_bear_step(
                radian_conv_step(
                    add_airport_dist(dataset.dropna(how="any", axis="rows"))
                )
            )
        )
    ).drop(columns=["key", "pickup_datetime"])
    if test_size != 0:
        train, test = train_test_split(dataset, test_size=test_size)
    else:
        train, test = dataset, dataset
    return train, test, "fare_amount"


# ---- STEPS -------
def clean_df(df):
    if "fare_amount" in df.columns:
        return df.drop(
            df.loc[
                (df.fare_amount <= 0)
                | (df.fare_amount > 500)
                | (
                    (df.pickup_longitude == 0)
                    | (df.pickup_latitude == 0)
                    | (df.dropoff_longitude == 0)
                    | (df.dropoff_latitude == 0)
                )
            ].index
        )
    else:
        return df.drop(
            df.loc[
                (
                    (df.pickup_longitude == 0)
                    | (df.pickup_latitude == 0)
                    | (df.dropoff_longitude == 0)
                    | (df.dropoff_latitude == 0)
                )
            ].index
        )


def add_airport_dist(df):
    """
    Return minumum distance from pickup or dropoff coordinates to each airport.
    JFK: John F. Kennedy International Airport
    EWR: Newark Liberty International Airport
    LGA: LaGuardia Airport
    SOL: Statue of Liberty
    NYC: Newyork Central
    """
    jfk_coord = (40.639722, -73.778889)
    ewr_coord = (40.6925, -74.168611)
    lga_coord = (40.77725, -73.872611)
    sol_coord = (40.6892, -74.0445)  # Statue of Liberty
    nyc_coord = (40.7141667, -74.0063889)

    pickup_lat = df["pickup_latitude"]
    dropoff_lat = df["dropoff_latitude"]
    pickup_lon = df["pickup_longitude"]
    dropoff_lon = df["dropoff_longitude"]

    pickup_jfk = sphere_dist(pickup_lat, pickup_lon, jfk_coord[0], jfk_coord[1])
    dropoff_jfk = sphere_dist(jfk_coord[0], jfk_coord[1], dropoff_lat, dropoff_lon)
    pickup_ewr = sphere_dist(pickup_lat, pickup_lon, ewr_coord[0], ewr_coord[1])
    dropoff_ewr = sphere_dist(ewr_coord[0], ewr_coord[1], dropoff_lat, dropoff_lon)
    pickup_lga = sphere_dist(pickup_lat, pickup_lon, lga_coord[0], lga_coord[1])
    dropoff_lga = sphere_dist(lga_coord[0], lga_coord[1], dropoff_lat, dropoff_lon)
    pickup_sol = sphere_dist(pickup_lat, pickup_lon, sol_coord[0], sol_coord[1])
    dropoff_sol = sphere_dist(sol_coord[0], sol_coord[1], dropoff_lat, dropoff_lon)
    pickup_nyc = sphere_dist(pickup_lat, pickup_lon, nyc_coord[0], nyc_coord[1])
    dropoff_nyc = sphere_dist(nyc_coord[0], nyc_coord[1], dropoff_lat, dropoff_lon)

    df["jfk_dist"] = pickup_jfk + dropoff_jfk
    df["ewr_dist"] = pickup_ewr + dropoff_ewr
    df["lga_dist"] = pickup_lga + dropoff_lga
    df["sol_dist"] = pickup_sol + dropoff_sol
    df["nyc_dist"] = pickup_nyc + dropoff_nyc

    return df


def add_datetime_info(df):
    # Convert to datetime format
    df["pickup_datetime"] = pd.to_datetime(
        df["pickup_datetime"], format="%Y-%m-%d %H:%M:%S UTC"
    )
    df["pickup_datetime_hour"] = df.pickup_datetime.dt.hour
    df["pickup_datetime_day"] = df.pickup_datetime.dt.day
    df["pickup_datetime_month"] = df.pickup_datetime.dt.month
    df["pickup_datetime_weekday"] = df.pickup_datetime.dt.weekday
    df["pickup_datetime_year"] = df.pickup_datetime.dt.year
    return df


def radian_conv_step(df):
    features = [
        "pickup_latitude",
        "pickup_longitude",
        "dropoff_latitude",
        "dropoff_longitude",
    ]
    for feature in features:
        df[feature] = np.radians(df[feature])
    return df


def sphere_dist_bear_step(df):
    df["bearing"] = sphere_dist_bear(
        df["pickup_latitude"],
        df["pickup_longitude"],
        df["dropoff_latitude"],
        df["dropoff_longitude"],
    )
    return df


def sphere_dist_step(df):
    df["distance"] = sphere_dist(
        df["pickup_latitude"],
        df["pickup_longitude"],
        df["dropoff_latitude"],
        df["dropoff_longitude"],
    )
    return df


# ---- Distance Calculation Formulas -------
def sphere_dist(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon):
    """
    Return distance along great radius between pickup and dropoff coordinates.
    """
    # Define earth radius (km)
    R_earth = 6371
    # Convert degrees to radians
    pickup_lat, pickup_lon, dropoff_lat, dropoff_lon = map(
        np.radians, [pickup_lat, pickup_lon, dropoff_lat, dropoff_lon]
    )
    # Compute distances along lat, lon dimensions
    dlat = dropoff_lat - pickup_lat
    dlon = dropoff_lon - pickup_lon
    # Compute haversine distance
    a = (
        np.sin(dlat / 2.0) ** 2
        + np.cos(pickup_lat) * np.cos(dropoff_lat) * np.sin(dlon / 2.0) ** 2
    )
    return 2 * R_earth * np.arcsin(np.sqrt(a))


def sphere_dist_bear(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon):
    """
    Return distance along great radius between pickup and dropoff coordinates.
    """
    # Convert degrees to radians
    pickup_lat, pickup_lon, dropoff_lat, dropoff_lon = map(
        np.radians, [pickup_lat, pickup_lon, dropoff_lat, dropoff_lon]
    )
    # Compute distances along lat, lon dimensions
    dlon = pickup_lon - dropoff_lon
    # Compute bearing distance
    a = np.arctan2(
        np.sin(dlon * np.cos(dropoff_lat)),
        np.cos(pickup_lat) * np.sin(dropoff_lat)
        - np.sin(pickup_lat) * np.cos(dropoff_lat) * np.cos(dlon),
    )
    return a
