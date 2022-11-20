import lightgbm as lgbm

# [MLRun] Import MLRun:
import mlrun
import pandas as pd
from mlrun.frameworks.lgbm import apply_mlrun
from sklearn.model_selection import train_test_split


@mlrun.handler()
def train(
    train_set: pd.DataFrame,
    label_column: str = "fare_amount",
    model_name: str = "lgbm_ny_taxi",
    boosting_type: str = "gbdt",
    subsample: float = 0.8,
    min_split_gain: float = 0.5,
    min_child_samples: int = 10,
):
    y = train_set[label_column]
    train_df = train_set.drop(columns=[label_column])

    x_train, x_test, y_train, y_test = train_test_split(
        train_df, y, random_state=123, test_size=0.10
    )

    model = lgbm.LGBMRegressor(
        boosting_type=boosting_type,
        subsample=subsample,
        min_split_gain=min_split_gain,
        min_child_samples=min_child_samples,
    )

    # -------------------- The only line you need to add for MLOps -------------------------
    # Wraps the model with MLOps (test set is provided for analysis & accuracy measurements)
    apply_mlrun(model=model, model_name=model_name, x_test=x_test, y_test=y_test)
    # --------------------------------------------------------------------------------------

    model.fit(X=x_train, y=y_train)

    return model
