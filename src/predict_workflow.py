import mlrun
from kfp import dsl


@dsl.pipeline(name="predict_workflow")
def pipeline(batch: str, model: str):
    # Get our project object:
    project = mlrun.get_current_project()

    # Dataset Preparation:
    prepare_dataset_run = mlrun.run_function(
        function="data-prep",
        name="data-prep",
        inputs={"dataset": batch},
        params={"test_size": 0},
        outputs=["train_dataset", "test_dataset", "label"],
    )

    # batch
    project.run_function(
        function="hub://batch_inference",
        inputs={
            "dataset": prepare_dataset_run.outputs["test_dataset"],
        },
        params={
            "model": model,
            "perform_drift_analysis": True,
        },
    ).after(prepare_dataset_run)
