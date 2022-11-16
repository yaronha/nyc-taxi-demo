from typing import Dict, Union
import numpy as np


def preprocess(vector: Union[Dict]) -> Dict:
    """Converting a simple text into a structured body for the serving function

    :param vector: The input to predict
    """
    vector.pop('timestamp')
    return {"inputs": [[*vector.values()]]}


def postprocess(model_response: Dict) -> str:
    """Transfering the prediction to the gradio interface.

    :param model_response: A dict with the model output
    """
    return f'predicted fare amount is {model_response["outputs"][0]}'

def sphere_dist_step(df):
    df["distance"] = sphere_dist(df["pickup_latitude"], df["pickup_longitude"],
                                 df["dropoff_latitude"],df["dropoff_longitude"],)
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
    a = (np.sin(dlat / 2.0) ** 2 + np.cos(pickup_lat) * np.cos(dropoff_lat) * np.sin(dlon / 2.0) ** 2)
    return 2 * R_earth * np.arcsin(np.sqrt(a))
