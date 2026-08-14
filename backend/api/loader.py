import os
import json
import joblib
from streamlit import dataframe

from backend.api.cache import cache
from backend.registry.registry_manager import RegistryManager


class ModelLoader:

    def __init__(
        self,
        registry_dir,
        models_dir
    ):

        self.registry = RegistryManager(
            registry_dir,
            models_dir
        )

        self.models_dir = models_dir
        self.cache = cache

    # =====================================================
    # Metadata Path
    # =====================================================

    def _metadata_path(self,  dataset_name, model_name, version):

        return os.path.join(

            self.models_dir,

            dataset_name,

            model_name,

            version,

            "metadata.json"

        )

    # =====================================================
    # Load Metadata
    # =====================================================

    def _load_metadata(self, dataset_name, model_name, version):
        path = self._metadata_path(dataset_name, model_name, version)

        with open(path, "r") as f:
            return json.load(f)

    # =====================================================
    # Load Production Model
    # =====================================================

    def load(self, dataset_name, model_name):

        production_path = self.registry.get_production_model(
            dataset_name,
            model_name
        )

        if production_path is None:
            raise RuntimeError("No production model available.")

        version = self.registry.production_version(dataset_name, model_name)

        metadata = self._load_metadata(
            dataset_name,
            model_name,
            version
       )

        model = joblib.load(production_path)
        print("=" * 60)
        print("Loaded Model Path :", production_path)
        print("Pipeline :", type(model))
        print("=" * 60)
        preprocessor = model.named_steps["preprocessor"]
        print(list(preprocessor.feature_names_in_))

        self.cache.set(model=model, metadata=metadata, model_path=production_path)
        return model

    # =====================================================
    # Cached Model
    # =====================================================

    def get_model(self, dataset_name, model_name):

        if not self.cache.is_loaded():

            return self.load(dataset_name, model_name)

        return self.cache.get()

    # =====================================================
    # Metadata
    # =====================================================

    def metadata(self, dataset_name, model_name):

        if not self.cache.is_loaded():

            self.load(dataset_name, model_name)

        return self.cache.get_metadata()

    # =====================================================
    # Force Reload
    # =====================================================

    def reload(self, dataset_name, model_name):

        self.cache.clear()

        return self.load(dataset_name, model_name)

    # =====================================================
    # Auto Reload
    # =====================================================

    def auto_reload(self, dataset_name, model_name):
        production = self.registry.production_version(
            dataset_name,
            model_name
        )

        if production is None:
            return

        current = self.cache.get_metadata()

        if current is None:
            self.load(dataset_name, model_name)
            return

        if current["version"] != production:
            self.reload(dataset_name, model_name)

    # =====================================================
    # Predict
    # =====================================================

    def predict(self, dataset_name, model_name, dataframe):

        self.auto_reload(dataset_name, model_name)

        model = self.get_model(dataset_name, model_name)

        self._validate_features(model, dataframe)
        return model.predict(dataframe)

    # =====================================================
    # Predict Probability
    # =====================================================

    def predict_proba(self, dataset_name, model_name, dataframe):
        self.auto_reload(dataset_name, model_name)

        model = self.get_model(
            dataset_name,
            model_name
        )

        predict_proba = getattr(
            model,
            "predict_proba",
            None
        )

        if not callable(predict_proba):
            return None

        return predict_proba(dataframe)

    # =====================================================
    # Validate features
    # =====================================================
    
    def _validate_features(self, model, dataframe):

        expected = set(
           model.named_steps["preprocessor"].feature_names_in_
       )

        received = set(
            dataframe.columns
        )

        missing = expected - received
        extra = received - expected

        if missing or extra:

            raise ValueError(

                {
                    "message": "Invalid input features.",

                    "expected_features": sorted(expected),

                    "received_features": sorted(received),

                    "missing_features": sorted(missing),

                    "extra_features": sorted(extra)

                }

            )