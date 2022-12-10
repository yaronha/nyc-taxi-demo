import mlrun
from kfp import dsl


@dsl.pipeline(name="train_workflow")
def pipeline(dataset: str, project_name: str):
    # Get our project object:
    project = mlrun.get_current_project()

    # Dataset Preparation:
    prepare_dataset_run = mlrun.run_function(
        function="data-prep",
        name="data-prep",
        inputs={"dataset": dataset},
        outputs=["train_dataset", "test_dataset", "label"],
        auto_build=True,
    )

    # Training
    training_run = mlrun.run_function(
        function="trainer",
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
        auto_build=True,
    )

    # Evaluating
    mlrun.run_function(
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
    serving_function.spec.graph["predict_fare"].class_args["model_path"] = str(
        training_run.outputs["model"]
    )

    # Enable model monitoring
    serving_function.set_tracking()

    # Deploy the serving function:
    deploy_return = project.deploy_function("serving").after(training_run)

    # Model server tester
    mlrun.run_function(
        function="server_tester",
        name="server_tester",
        inputs={"dataset": dataset},
        params={
            "label_column": "fare_amount",
            "endpoint": deploy_return.outputs["endpoint"],
        },
        auto_build=True,
    ).after(deploy_return)
