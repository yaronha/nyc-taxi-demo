from datetime import datetime

import mlrun
import numpy as np
import pandas as pd
import plotly.express as px


@mlrun.handler(
    outputs=[
        "count",
        "error_count",
        "avg_latency",
        "min_latency",
        "max_latency",
        "latency_chart:plot",
    ]
)
def model_server_tester(
    dataset: pd.DataFrame,
    project_name: str,
    label_column: str,
    rows: int = 100,
    max_error: int = 5,
):
    """Test a model server
    :param project_name:
    :param dataset:         csv/parquet table with test data
    :param label_column:  name of the label column in table
    :param rows:          number of rows to use from test set
    :param max_error:     maximum error for
    """

    project = mlrun.get_or_create_project(
        name=project_name, user_project=True, context="./"
    )
    if rows and rows < dataset.shape[0]:
        dataset = dataset.sample(rows)
    y_list = dataset.pop(label_column).values.tolist()
    dataset = (
        radian_conv_step(
            add_airport_dist(clean_df(dataset).dropna(how="any", axis="rows"))
        )
        .drop(columns=["key"])
        .rename(columns={"pickup_datetime": "timestamp"})
    )

    count = err_count = 0
    times, y_true, y_pred = [], [], []
    serving_function = project.get_function("serving")
    for i, y in zip(range(dataset.shape[0]), y_list):
        count += 1
        event_data = dataset.iloc[i].to_dict()
        try:
            start = datetime.now()
            resp = serving_function.invoke(path="/predict", body=event_data)
            if "result_str" not in resp:
                project.logger.error(f"bad function resp!!\n{resp.text}")
                err_count += 1
                continue
            times.append((datetime.now() - start).microseconds)

        except OSError as err:
            project.logger.error(f"error in request, data:{event_data}, error: {err}")
            err_count += 1
            continue
        if err_count == max_error:
            raise ValueError(f"reached error max limit = {max_error}")

        y_true.append(y)
        y_pred.append(resp["result"])

    times_arr = np.array(times)
    latency_chart = px.line(
        x=range(2, len(times) + 1),
        y=times_arr[1:],
        title="<i><b>Latency (microsec) X  Invokes</b></i>",
        labels={"y": "latency (microsec)", "x": "invoke number"},
    )

    return (
        count,
        err_count,
        int(np.mean(times_arr)),
        int(np.amin(times_arr)),
        int(np.amax(times_arr)),
        latency_chart,
    )


# ---- STEPS -------
def clean_df(df):
    if "fare_amount" in df.columns:
        return df[
            (df.fare_amount > 0)
            & (df.fare_amount <= 500)
            & (
                (df.pickup_longitude != 0)
                & (df.pickup_latitude != 0)
                & (df.dropoff_longitude != 0)
                & (df.dropoff_latitude != 0)
            )
        ]
    else:
        return df[
            (
                (df.pickup_longitude != 0)
                & (df.pickup_latitude != 0)
                & (df.dropoff_longitude != 0)
                & (df.dropoff_latitude != 0)
            )
        ]


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
