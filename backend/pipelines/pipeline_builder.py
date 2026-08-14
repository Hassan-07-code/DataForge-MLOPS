from sklearn.pipeline import Pipeline

from backend.pipelines.preprocessing import PreprocessingBuilder


class PipelineBuilder:
    """
    Production-ready Pipeline Builder.

    Creates a complete ML pipeline consisting of:
        Raw Data
            ↓
        Preprocessing
            ↓
        ML Model
            ↓
        Predictions

    The returned object is a standard sklearn Pipeline and can be
    trained, saved, loaded, exported and deployed without any
    additional preprocessing code.
    """

    @staticmethod
    def build(model, X):
        """
        Parameters
        ----------
        model : sklearn estimator
            Any sklearn-compatible estimator.

        X : pandas.DataFrame
            Training features.

        Returns
        -------
        sklearn.pipeline.Pipeline
        """

        preprocessor = PreprocessingBuilder.build(X)

        pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", model)
            ]
        )

        return pipeline