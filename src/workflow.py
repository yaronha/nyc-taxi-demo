import mlrun
from kfp import dsl
from mlrun.feature_store.steps import DateExtractor


@dsl.pipeline(name="lgbm_ny_taxi_pipeline")
def kfpipeline(
    dataset: str,
):
    # Get our project object:
    project = mlrun.get_current_project()

    # Dataset Preparation:
    prepare_dataset_run = mlrun.run_function(
        function="data-prep",
        handler="data_preparation",
        name="data-prep",
        inputs={"dataset": dataset},
        outputs=["train_dataset", "test_dataset", "label"],
    )

    # Training
    training_run = mlrun.run_function(
        function="trainer",
        handler="train",
        name="trainer",
        inputs={"train_set": prepare_dataset_run.outputs["train_dataset"]},
        hyperparams={
            "boosting_type": ["gbdt"],
            "subsample": [0.2, 0.5, 0.8],
            "min_split_gain": [0.2, 0.5, 0.7],
            "min_child_samples": [5, 10, 15],
        },
        selector="min.mean_squared_error",
        outputs=["model"],
    )

    # Evaluating
    evaluating_run = mlrun.run_function(
        function="evaluate",
        name="evaluate",
        handler="evaluate",
        inputs={"dataset": prepare_dataset_run.outputs["test_dataset"]},
        params={
            "model": training_run.outputs["model"],
            "label_columns": "fare_amount",
        },
    )

    # Get the function:
    serving_function = project.get_function("serving")

    # Enable model monitoring
    serving_function.set_tracking()

    if serving_function.spec.graph is None:
        graph = serving_function.set_topology("flow", engine="async")

        # Build the serving graph:
        graph.to(handler="sphere_dist_bear_step", name="bearing_calculation").to(
            handler="sphere_dist_step", name="distance_calculation"
        ).to(
            DateExtractor(
                parts=["hour", "day", "month", "day_of_week", "year"],
                timestamp_col="timestamp",
            )
        ).to(
            handler="preprocess", name="peprocess"
        ).to(
            class_name="mlrun.frameworks.lgbm.LGBMModelServer",
            name="lgbm_ny_taxi",
            model_path=str(training_run.outputs["model"]),
        ).to(
            handler="postprocess", name="postprocess"
        ).respond()

    # Deploy the serving function:
    project.deploy_function("serving").after(training_run)
