from google_crc32c import value
import mlflow
import mlflow.sklearn
from backend.config.settings import (
    MLFLOW_TRACKING_URI,
    MLFLOW_EXPERIMENT_NAME
)


class MLflowLogger:

    def __init__(self):
        print("=" * 60)

        print("Config URI :", MLFLOW_TRACKING_URI)

        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

        print("Actual URI :", mlflow.get_tracking_uri())

        mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

        print("Experiment :", MLFLOW_EXPERIMENT_NAME)

        print("=" * 60)

        self.active = False

    def start_run(self, run_name=None):
        active_run = mlflow.active_run()
        print("=" * 60)
        print("Tracking URI:", mlflow.get_tracking_uri())
        print("Active Run:", mlflow.active_run())
        print("=" * 60)

        if active_run is not None:
            print(f"Ending active run: {active_run.info.run_id}")
            mlflow.end_run()

        mlflow.start_run(run_name=run_name)

        self.active = True

    def end_run(self):

        if self.active:
            mlflow.end_run()

            self.active = False

    def log_params(self, params: dict):

        clean_params = {}

        for key, value in params.items():

            if value is None:
                continue

            try:
                clean_params[key] = value if isinstance(
                    value,
                    (str, int, float, bool)
                ) else str(value)

            except Exception:
                pass

        mlflow.log_params(clean_params)

    def log_metrics(self, metrics: dict):

        if not metrics:
            return

        clean_metrics = {}

        for k, v in metrics.items():

            if v is None:
                continue

            try:
                clean_metrics[k] = float(v)

            except Exception:
                pass

        mlflow.log_metrics(clean_metrics)

    def log_metric(self, key: str, value):
        if value is None:
            return

        try:
            mlflow.log_metric(key, float(value))
        except Exception as e:
            print(f"[MLflow] Failed to log metric '{key}': {e}")

    def log_tags(self, tags: dict):

        if tags:

            mlflow.set_tags(tags)

    def log_artifact(self, path):

        mlflow.log_artifact(path)

    def log_model(self, pipeline, input_example=None):

        mlflow.sklearn.log_model(

            sk_model=pipeline,

            # name="pipeline",
            artifact_path="pipeline",

            input_example=input_example

            # skops_trusted_types=[np.dtype, np.ndarray]

        )

    def log_text(self, text, filename):

        mlflow.log_text(text, filename)


    def log_performance_metrics(self, metrics: dict):
        clean_metrics = {}

        for k, v in metrics.items():
            try:
                clean_metrics[k] = float(v)
            except Exception:
                pass

        mlflow.log_metrics(clean_metrics)