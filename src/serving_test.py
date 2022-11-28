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
