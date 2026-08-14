from datetime import datetime
import hashlib
import pandas as pd


class ExperimentManager:

    @staticmethod
    def create_run_name(model_name, dataset_name):

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        return f"{model_name}_{dataset_name}_{timestamp}"

    @staticmethod
    def dataset_metadata(df: pd.DataFrame,
                         target: str,
                         dataset_name: str,
                         problem_type: str):

        memory_mb = round(
            df.memory_usage(deep=True).sum() / (1024 * 1024),
            3
        )

        missing_values = int(df.isna().sum().sum())

        duplicate_rows = int(df.duplicated().sum())

        rows = len(df)

        columns = df.shape[1]

        numeric_cols = list(
            df.select_dtypes(include=["number"]).columns
        )

        categorical_cols = list(
            df.select_dtypes(include=["object", "category"]).columns
        )

        bool_cols = list(
            df.select_dtypes(include=["bool"]).columns
        )

        datetime_cols = list(
            df.select_dtypes(include=["datetime"]).columns
        )

        dataset_hash = hashlib.md5(
            pd.util.hash_pandas_object(
                df,
                index=True
            ).values
        ).hexdigest()

        metadata = {

            # Dataset Identity
            "dataset_name": dataset_name,
            "dataset_hash": dataset_hash,

            # Shape
            "rows": rows,
            "columns": columns,
            "features": columns - 1,

            # Target
            "target": target,
            "problem_type": problem_type,

            # Quality
            "missing_values": missing_values,
            "missing_percent": round(
                (missing_values / (rows * columns)) * 100,
                3
            ),

            "duplicate_rows": duplicate_rows,

            "duplicate_percent": round(
                (duplicate_rows / rows) * 100,
                3
            ),

            # Memory
            "memory_mb": memory_mb,

            # Schema
            "numeric_columns": len(numeric_cols),
            "categorical_columns": len(categorical_cols),
            "boolean_columns": len(bool_cols),
            "datetime_columns": len(datetime_cols)
        }

        return metadata