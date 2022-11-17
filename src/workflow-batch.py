import mlrun
from kfp import dsl


@dsl.pipeline(name="lgbm_ny_taxi_pipeline_batch_predict")
def kfpipeline(
        batch: str,
        model: str
):
    # Get our project object:
    project = mlrun.get_current_project()

    # Dataset Preparation:
    prepare_dataset_run = mlrun.run_function(
        function="data-prep",
        handler="data_preparation",
        name="data-prep",
        inputs={"dataset": batch},
        params={'test_size':0},
        outputs=["train_dataset", 'test_dataset', 'label'],
    )

    # batch
    batcing_run = project.run_function(
        function='batch_predict',
        inputs={
            "dataset": prepare_dataset_run.outputs["test_dataset"],
        },
        params={
            "model": model,
            "perform_drift_analysis" : True,
        },
    ).after(prepare_dataset_run)
