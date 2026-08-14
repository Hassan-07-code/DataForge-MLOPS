import os
import joblib
from datetime import datetime
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any, Optional
from backend.config.settings import RANDOM_STATE, TEST_SIZE, CV_FOLDS, N_JOBS
from backend.config.paths import MODELS_DIR
from backend.utils.logger import logger
from backend.tracking import SystemInfo
from backend.tracking import PerformanceProfiler
from backend.pipelines.pipeline_builder import PipelineBuilder
from backend.registry import RegistryManager
import time
import platform

from backend.tracking import (
    MLflowLogger,
    ExperimentManager
)

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, f1_score, recall_score, precision_score,
    r2_score, mean_absolute_error, mean_squared_error, roc_auc_score
)
from sklearn.preprocessing import label_binarize

from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import (
    RandomForestClassifier, RandomForestRegressor,
    GradientBoostingClassifier, GradientBoostingRegressor
)
from sklearn.svm import SVC, SVR
from sklearn.naive_bayes import GaussianNB

# xgboost optional
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except Exception:
    XGB_AVAILABLE = False

class ModelTrainer:
    """
    Robust trainer for classification & regression.
    Key features:
      - Reliable problem-type detection
      - Demo training (80/20) with safe stratify
      - Separate Test on held-out set
      - Final training on full dataset and saving
      - Detailed metrics (accuracy, f1, precision, recall, roc_auc when applicable; r2, MAE, RMSE for regression)
      - Cross-validation helper
    """

    def __init__(self, df: pd.DataFrame, target_col: str, models_dir: str = str(MODELS_DIR), dataset_name="dataset", random_state: int = RANDOM_STATE):
        self.df = df.copy()
        if target_col not in self.df.columns:
            raise ValueError(f"target_col '{target_col}' not in dataframe columns")
        self.target_col = target_col
        self.random_state = int(random_state)
        self.models_dir = str(MODELS_DIR)
        self.dataset_name = dataset_name
        self.mlflow = MLflowLogger()
        self.registry = RegistryManager(registry_dir="artifacts/registry", models_dir=self.models_dir)
        os.makedirs(self.models_dir, exist_ok=True)

        # stateful placeholders (persist within same trainer instance)
        self.X_train: Optional[pd.DataFrame] = None
        self.X_test: Optional[pd.DataFrame] = None
        self.y_train: Optional[pd.Series] = None
        self.y_test: Optional[pd.Series] = None
        self.last_pipeline = None
        self.task: Optional[str] = None  # "classification" or "regression"

    # ------------
    # Helpers
    # ------------

    def _start_experiment(self, model_name):

        dataset_name = os.path.splitext(self.dataset_name)[0]

        run_name = ExperimentManager.create_run_name(
            model_name=model_name,
            dataset_name=dataset_name
        )

        self.mlflow.start_run(run_name)

        metadata = ExperimentManager.dataset_metadata(
            df=self.df,
            target=self.target_col,
            dataset_name=os.path.splitext(self.dataset_name)[0],
            problem_type=self.detect_problem_type()
        )

        self.mlflow.log_params(metadata)
        system_info = SystemInfo.collect()
        self.mlflow.log_params(system_info)

        self.mlflow.log_tags({

            "framework": "DataForge",

            "python": platform.python_version(),

            "task": self.detect_problem_type(),

            "model": model_name

        })

    def _finish_experiment(
        self,
        pipeline,
        metrics,
        model_path,
        training_time,
        model_size,
        latency,
        throughput,
        memory,
        cpu,
    ):
        # --------------------------------------------------
        # Metrics
        # --------------------------------------------------

        self.mlflow.log_metrics(metrics)

        self.mlflow.log_metric(
            "training_time_sec",
            training_time
        )

        performance_metrics = {
            "training_time_sec": training_time,
            "inference_latency_ms": latency,
            "throughput_pred_per_sec": throughput,
            "model_size_mb": model_size,
            "memory_usage_mb": memory,
            "cpu_usage_percent": cpu,
        }

        self.mlflow.log_performance_metrics(
            performance_metrics
        )

        # --------------------------------------------------
        # Artifacts
        # --------------------------------------------------

        if os.path.exists(model_path):
            self.mlflow.log_artifact(model_path)

        # --------------------------------------------------
        # Model Signature & Input Example
        # --------------------------------------------------

        input_example = (
            self.df
            .drop(columns=[self.target_col])
            .head(5)
        )

        self.mlflow.log_model(
            pipeline=pipeline,
            input_example=input_example
        )

        # --------------------------------------------------
        # Finish Run
        # --------------------------------------------------

        self.mlflow.end_run()

    # -------------------------
    # Problem detection
    # -------------------------
    def detect_problem_type(self, require_override: Optional[str] = None) -> str:
        """
        Robust detection:
          - Non-numeric targets -> classification
          - Numeric & integer dtype with small unique count (<=20) -> classification (discrete)
          - Numeric with float dtype or many unique -> regression
          - If user passes require_override ("classification" or "regression"), that will be returned.
        """
        if require_override in ("classification", "regression"):
            return require_override

        y = self.df[self.target_col]

        # non-numeric -> classification
        if not pd.api.types.is_numeric_dtype(y):
            return "classification"

        # numeric: check uniqueness proportion and dtype
        uniq = int(y.nunique(dropna=True))
        n_rows = len(y)

        # if integer dtype and few unique labels => classification
        if pd.api.types.is_integer_dtype(y) and uniq <= 20:
            return "classification"

        # if uniqueness is low relative to rows (like categories encoded as numbers) and uniq <= 0.05*rows
        if uniq <= 50 and (uniq / max(1, n_rows)) <= 0.05:
            # still ambiguous — treat as classification if integer-like
            if pd.api.types.is_integer_dtype(y):
                return "classification"

        # otherwise treat as regression
        return "regression"

    # -------------------------
    # Model mapping
    # -------------------------
    def _get_model_map(self, task: str) -> Dict[str, Any]:
        if task == "classification":
            models = {
                "Logistic Regression": LogisticRegression(max_iter=2000, random_state=self.random_state),
                "Decision Tree": DecisionTreeClassifier(random_state=self.random_state),
                "Random Forest": RandomForestClassifier(n_jobs=N_JOBS, random_state=self.random_state),
                "SVM": SVC(probability=True, random_state=self.random_state),
                "Naive Bayes": GaussianNB(),
                "Gradient Boosting": GradientBoostingClassifier(random_state=self.random_state),
            }
            if XGB_AVAILABLE:
                models["XGBoost"] = xgb.XGBClassifier(use_label_encoder=False, eval_metric="logloss", random_state=self.random_state)
            return models
        else:
            models = {
                "Linear Regression": LinearRegression(),
                "Decision Tree Regressor": DecisionTreeRegressor(random_state=self.random_state),
                "Random Forest Regressor": RandomForestRegressor(n_jobs=N_JOBS, random_state=self.random_state),
                "SVR": SVR(),
                "Gradient Boosting Regressor": GradientBoostingRegressor(random_state=self.random_state),
            }
            if XGB_AVAILABLE:
                models["XGBoost Regressor"] = xgb.XGBRegressor(random_state=self.random_state)
            return models

    def get_available_models(self, require_task: Optional[str] = None) -> list:
        task = require_task or self.detect_problem_type()
        return list(self._get_model_map(task).keys())

    # -------------------------
    # Evaluation helpers
    # -------------------------
    def _evaluate_classification(self, model, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        preds = model.predict(X)
        res = {
            "accuracy": float(accuracy_score(y, preds)),
            "f1_weighted": float(f1_score(y, preds, average="weighted")),
            "f1_macro": float(f1_score(y, preds, average="macro")),
            "recall_weighted": float(recall_score(y, preds, average="weighted")),
            "precision_weighted": float(precision_score(y, preds, average="weighted")),
        }

        # try ROC AUC where applicable
        try:
            unique_labels = np.unique(y.dropna())
            if len(unique_labels) == 2 and hasattr(model, "predict_proba"):
                probs = model.predict_proba(X)[:, 1]
                res["roc_auc"] = float(roc_auc_score(y, probs))
            elif len(unique_labels) > 2 and hasattr(model, "predict_proba"):
                # multiclass roc_auc using ovR where possible
                try:
                    y_bin = label_binarize(y, classes=unique_labels)
                    probs = model.predict_proba(X)
                    # attempt macro average
                    res["roc_auc_ovr_macro"] = float(roc_auc_score(y_bin, probs, average="macro", multi_class="ovr"))
                except Exception:
                    res["roc_auc_ovr_macro"] = None
            else:
                res["roc_auc"] = None
        except Exception:
            res["roc_auc"] = None

        return res

    def _evaluate_regression(self, model, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        preds = model.predict(X)
        mse = mean_squared_error(y, preds)
        return {
            "r2": float(r2_score(y, preds)),
            "mae": float(mean_absolute_error(y, preds)),
            "rmse": float(np.sqrt(mse)),
            "mse": float(mse)
        }

    # -------------------------
    # Suggestion helper
    # -------------------------
    def suggest_model(self) -> Tuple[str, str]:
        task = self.detect_problem_type()
        if task == "classification":
            return ("Random Forest", "Random Forest is a reliable baseline for classification on tabular data.")
        return (("Gradient Boosting Regressor" if XGB_AVAILABLE else "Random Forest Regressor"),
                "Tree ensembles (Gradient boosting / Random Forest) often perform best for regression on tabular data.")

    # -------------------------
    # Training / Testing / Saving
    # -------------------------
    def train_demo_model(self, model_name: str, test_size: float = TEST_SIZE, require_task: Optional[str] = None) -> Tuple[Any, Dict[str, Any], int, int]:
        """
        Train a demo model on an 80/20 split (or custom test_size).
        - Returns: (trained_model_object, training_metrics_dict, n_train, n_test)
        - On success, internal placeholders (X_train, X_test, y_train, y_test, last_pipeline, task) are set.
        - Raises RuntimeError with clear message on failure.
        """
        # prepare dataset
        X = self.df.drop(columns=[self.target_col]).copy()
        y = self.df[self.target_col].copy()

        # defensive fill for features
        X = X.fillna(0)

        # target fill/clean
        if pd.api.types.is_numeric_dtype(y):
            y = y.fillna(y.mean())
        else:
            y = y.ffill().bfill()

        # determine task robustly
        self.task = require_task or self.detect_problem_type()

        logger.info(f"Demo training started | Model={model_name} | Task={self.task}")

        # decide stratify only if classification and every class has >=2 samples
        stratify = None
        if self.task == "classification":
            vc = y.value_counts(dropna=True)
            if len(vc) == 0:
                raise RuntimeError("Target column contains no values after cleaning.")
            if vc.min() >= 2:
                stratify = y
            else:
                # can't stratify when some class has 1 sample -> fallback to random split
                stratify = None

        # perform split (guard exceptions)
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=self.random_state, stratify=stratify
            )
        except Exception as e:
            logger.exception(e)
            raise RuntimeError(f"Demo training split failed: {e}")

        # get model
        model_map = self._get_model_map(self.task)
        if model_name not in model_map:
            raise ValueError(f"Model '{model_name}' not available for task '{self.task}'. Available: {list(model_map.keys())}")

        model = model_map[model_name]
        pipeline = PipelineBuilder.build(model, X_train)

        # try fitting; raise helpful message on failure
        try:
            pipeline.fit(X_train, y_train)
        except Exception as e:
            raise RuntimeError(f"pipeline.fit failed for '{model_name}': {e}")

        # evaluate on training partition (so user sees training performance)
        try:
            train_metrics = (self._evaluate_classification(pipeline, X_train, y_train)
                             if self.task == "classification"
                             else self._evaluate_regression(pipeline, X_train, y_train))
        except Exception as e:
            raise RuntimeError(f"Failed to evaluate training metrics: {e}")

        # persist state only after successful fit & eval
        self.X_train, self.X_test, self.y_train, self.y_test = X_train, X_test, y_train, y_test
        self.last_pipeline = pipeline

        logger.info(
        f"Demo training completed | Model={model_name} | "
        f"Train Samples={len(X_train)} | Test Samples={len(X_test)}"
        )

        return pipeline, train_metrics, len(X_train), len(X_test)

    def test_model(self) -> Dict[str, Any]:
        """
        Evaluate the last demo-trained model on stored test set.
        Raises RuntimeError if no demo model / test set available.
        """
        if self.last_pipeline is None or self.X_test is None or self.y_test is None:
            raise RuntimeError("No demo model or test set available. Run demo training first (and ensure it completed successfully).")

        try:
            return (self._evaluate_classification(self.last_pipeline, self.X_test, self.y_test)
                    if self.task == "classification"
                    else self._evaluate_regression(self.last_pipeline, self.X_test, self.y_test))
        except Exception as e:
            raise RuntimeError(f"Test evaluation failed: {e}")

    def train_final_model(self, model_name: str, require_task: Optional[str] = None, save: bool = True) -> Tuple[str, Dict[str, Any]]:
    # Prepare dataset
        X = self.df.drop(columns=[self.target_col]).copy().fillna(0)
        y = self.df[self.target_col].copy()

        if pd.api.types.is_numeric_dtype(y):
            y = y.fillna(y.mean())
        else:
            y = y.ffill().bfill()

        # Detect task (classification or regression)
        task = require_task or self.detect_problem_type()
        model_map = self._get_model_map(task)

        if model_name not in model_map:
            raise ValueError(f"Model '{model_name}' not available for task '{task}'. Available: {list(model_map.keys())}")

        # ✅ Use only the selected model
        model = model_map[model_name]
        pipeline = PipelineBuilder.build(model, X)
        self._start_experiment(model_name)
        hyperparameters = model.get_params()
        self.mlflow.log_params(hyperparameters)

        start = time.perf_counter()
        # 🚀 Train only the selected model
        try:
            training_start = time.perf_counter()
            pipeline.fit(X, y)
            training_time = PerformanceProfiler.training_timer(training_start)
        except Exception as e:
            raise RuntimeError(f"Final model fit failed for '{model_name}': {e}")

        # 📊 Evaluate metrics for full dataset
        try:
            metrics = (self._evaluate_classification(pipeline, X, y)
                    if task == "classification"
                    else self._evaluate_regression(pipeline, X, y))
        except Exception as e:
            raise RuntimeError(f"Failed evaluating final model metrics: {e}")

        # 💾 Save the trained model (only the selected one)
        final_model_path = ""

        if save:
            temp_model = os.path.join(self.models_dir, "temp_model.joblib")

            try:
                # Save temporary model
                joblib.dump(pipeline, temp_model)

                # Performance profiling
                latency = PerformanceProfiler.inference_latency(pipeline, X)
                throughput = PerformanceProfiler.throughput(pipeline, X)
                memory = PerformanceProfiler.process_memory()
                cpu = PerformanceProfiler.cpu_usage()

                # Register model (moves temp model into registry)
                final_model_path = self.registry.register_model(
                        dataset_name=self.dataset_name,
                        model_name=model_name,
                        model_path=temp_model,
                        metrics=metrics
                    )

                    # Calculate final registered model size
                model_size = PerformanceProfiler.model_size(final_model_path)

                    # Finish MLflow experiment
                self._finish_experiment(
                    pipeline=pipeline,
                    metrics=metrics,                        
                    model_path=final_model_path,
                    training_time=training_time,
                    model_size=model_size,
                    latency=latency,
                    throughput=throughput,
                    memory=memory,                        cpu=cpu
                )

            except Exception as e:
                raise RuntimeError(f"Failed to save final model to disk: {e}")

        return final_model_path, metrics

    # -------------------------
    # Convenience: cross-val
    # -------------------------
    def cross_val(self, model_name: str, cv: int = CV_FOLDS, scoring: Optional[str] = None) -> Dict[str, Any]:
        """
        Run cross-validation on full dataset (be careful with memory / time).
        Returns mean and std of CV scores.
        """
        X = self.df.drop(columns=[self.target_col]).copy().fillna(0)
        y = self.df[self.target_col].copy()
        task = self.detect_problem_type()
        model_map = self._get_model_map(task)
        if model_name not in model_map:
            raise ValueError(f"Model '{model_name}' not available for task '{task}'")
        model = model_map[model_name]
        pipeline = PipelineBuilder.build(model, X)
        try:
            scores = cross_val_score(pipeline, X, y, cv=cv, scoring=scoring, n_jobs=-1)
            return {"cv_mean": float(np.mean(scores)), "cv_std": float(np.std(scores)), "cv_n": len(scores)}
        except Exception as e:
            raise RuntimeError(f"Cross-validation failed: {e}")

    def _measure_inference_time(self, pipeline, X):
        import time
        sample = X.head(1)
        start = time.perf_counter()
        pipeline.predict(sample)
        end = time.perf_counter()
        return round((end - start) * 1000, 4)

    def _measure_throughput(self, pipeline, X):
        import time
        start = time.perf_counter()
        pipeline.predict(X)
        end = time.perf_counter()
        total = end - start
        return round(len(X) / total, 2)