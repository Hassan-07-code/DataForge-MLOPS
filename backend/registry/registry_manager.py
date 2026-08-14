from importlib import metadata
import os
import json
import copy
import shutil

from threading import Lock
from datetime import datetime


# =====================================================
# Model Stages
# =====================================================

DEVELOPMENT = "Development"
STAGING = "Staging"
PRODUCTION = "Production"
ARCHIVED = "Archived"


class RegistryManager:

    # =====================================================
    # Constructor
    # =====================================================

    def __init__(
        self,
        registry_dir,
        models_dir
    ):

        self.registry_dir = registry_dir
        self.models_dir = models_dir

        os.makedirs(
            self.registry_dir,
            exist_ok=True
        )

        os.makedirs(
            self.models_dir,
            exist_ok=True
        )

        self.registry_file = os.path.join(
            self.registry_dir,
            "registry.json"
        )

        # Thread-safe writes
        self.lock = Lock()

        if not os.path.exists(self.registry_file):
            self.save_registry({})

    # =====================================================
    # Registry File
    # =====================================================

    def load_registry(self):

        if not os.path.exists(self.registry_file):
            return {}

        with open(self.registry_file, "r") as f:
            return json.load(f)

    def save_registry(self, registry):

        with open(self.registry_file, "w") as f:
            json.dump(
                registry,
                f,
                indent=4
            )

    # =====================================================
    # Validation
    # =====================================================

    def _validate_model(

        self,

        registry,

        dataset_name,

        model_name

    ):

        if dataset_name not in registry:

            raise ValueError(

                f"Dataset '{dataset_name}' not found."

            )

        if model_name not in registry[dataset_name]:

            raise ValueError(

                f"Model '{model_name}' not found."

            )

    def _validate_version(

        self,

        registry,

        dataset_name,

        model_name,

        version

    ):

        self._validate_model(

            registry,

            dataset_name,

            model_name

        )

        if version not in registry[dataset_name][model_name]["versions"]:

            raise ValueError(

                f"Version '{version}' not found."

            )

    # =====================================================
    # Metadata Helper
    # =====================================================

    def _metadata_path(

        self,

        dataset_name,

        model_name,

        version

    ):

        return os.path.join(

            self.models_dir,

            dataset_name,

            model_name,

            version,

            "metadata.json"

        )

    def _update_metadata_stage(

        self,

        dataset_name,

        model_name,

        version,

        stage

    ):

        metadata_path = self._metadata_path(

            dataset_name,

            model_name,

            version

        )

        if not os.path.exists(metadata_path):

            return

        with open(metadata_path, "r") as f:

            metadata = json.load(f)

        metadata["stage"] = stage

        with open(metadata_path, "w") as f:

            json.dump(

                metadata,

                f,

                indent=4

            )

    # =====================================================
    # Folder Helper
    # =====================================================

    def create_model(

        self,

        dataset_name,

        model_name

    ):

        model_dir = os.path.join(

            self.models_dir,

            dataset_name,

            model_name

        )

        os.makedirs(

            model_dir,

            exist_ok=True

        )

        return model_dir

    # =====================================================
    # Version Helper
    # =====================================================

    def get_latest_version(

        self,

        dataset_name,

        model_name

    ):

        model_dir = self.create_model(

            dataset_name,

            model_name

        )

        versions = [

            d

            for d in os.listdir(model_dir)

            if d.startswith("v")

        ]

        if len(versions) == 0:

            return 1

        nums = [

            int(v.replace("v", ""))

            for v in versions

        ]

        return max(nums) + 1

    def _validate_identifier(self, value, field_name):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} must be a non-empty string")

        value = value.strip()

        if value in {".", ".."}:
            raise ValueError(f"Invalid {field_name}: {value}")

        if "/" in value or "\\" in value:
            raise ValueError(f"Invalid {field_name}: path separators are not allowed")

        if any(char in value for char in '<>:"|?*'):
            raise ValueError(f"Invalid {field_name}: contains invalid characters")

        return value

    # =====================================================
    # Register Model
    # =====================================================

    def register_model(
        self,
        dataset_name,
        model_name,
        model_path,
        metrics
    ):
        if not isinstance(dataset_name, str) or not dataset_name.strip():
            raise ValueError("dataset_name must be a non-empty string")

        if not isinstance(model_name, str) or not model_name.strip():
            raise ValueError("model_name must be a non-empty string")

        if not isinstance(model_path, str) or not model_path.strip():
            raise ValueError("model_path must be a non-empty string")

        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        """
        Register a newly trained model.

        Flow
        ----
        temp_model.joblib
                │
                ▼
        Create Version Folder
                │
                ▼
        Move model.joblib
                │
                ▼
        Create metadata.json
                │
                ▼
        Update registry.json
                │
                ▼
        Return final model path
        """

        dataset_name = self._validate_identifier(
            dataset_name,
            "dataset_name"
        )

        model_name = self._validate_identifier(
            model_name,
            "model_name"
        )

        with self.lock:

            registry = self.load_registry()

            backup = copy.deepcopy(registry)

            try:

                # -----------------------------------------
                # Create dataset/model entry
                # -----------------------------------------

                if dataset_name not in registry:
                    registry[dataset_name] = {}

                if model_name not in registry[dataset_name]:

                    registry[dataset_name][model_name] = {

                        "latest_version": None,

                        "production": None,

                        "staging": None,

                        "versions": {}

                    }

                # -----------------------------------------
                # New Version
                # -----------------------------------------

                version = f"v{self.get_latest_version(dataset_name, model_name)}"

                version_dir = os.path.join(

                    self.models_dir,
                    dataset_name,
                    model_name,
                    version

                )

                os.makedirs(
                    version_dir,
                    exist_ok=True
                )

                # -----------------------------------------
                # Move model
                # -----------------------------------------

                final_model_path = os.path.join(
                    version_dir,
                    "model.joblib"
                )

                shutil.move(
                    model_path,
                    final_model_path
                )

                # -----------------------------------------
                # Metadata
                # -----------------------------------------

                created_at = datetime.now().isoformat()

                metadata = {

                    "dataset": dataset_name,

                    "model": model_name,

                    "version": version,

                    "stage": DEVELOPMENT,

                    "created_at": created_at,

                    "metrics": metrics

                }

                metadata_path = os.path.join(
                    version_dir,
                    "metadata.json"
                )

                with open(metadata_path, "w") as f:

                    json.dump(
                        metadata,
                        f,
                        indent=4
                    )

                # -----------------------------------------
                # Registry Update
                # -----------------------------------------

                registry[dataset_name][model_name]["latest_version"] = version

                registry[dataset_name][model_name]["versions"][version] = {

                    "stage": DEVELOPMENT,

                    "created_at": created_at,

                    "metrics": metrics

                }

                self.save_registry(registry)

                return final_model_path

            except Exception:

                # -----------------------------------------
                # Rollback Registry
                # -----------------------------------------

                self.save_registry(backup)

                # Remove partially-created folder

                version_dir = os.path.join(
                    self.models_dir,
                    dataset_name,
                    model_name,
                    version
                )

                if os.path.exists(version_dir):

                    shutil.rmtree(
                        version_dir,
                        ignore_errors=True
                    )

                raise

    
    def update_metadata_stage(
        self,
        version_dir,
        stage
    ):

        metadata_path = os.path.join(
            version_dir,
            "metadata.json"
        )

        if not os.path.exists(metadata_path):
            raise FileNotFoundError(
                "metadata.json not found"
            )

        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        metadata["stage"] = stage
        metadata["updated_at"] = datetime.now().isoformat()

        with open(metadata_path, "w") as f:
            json.dump(
                metadata,
                f,
                indent=4
            )

    # =====================================================
    # Promote to Staging
    # =====================================================

    def promote_to_staging(
        self,
        dataset_name,
        model_name,
        version
    ):
        with self.lock:
            registry = self.load_registry()
            backup = copy.deepcopy(registry)

            try:
                self._validate_version(
                    registry,
                    dataset_name,
                    model_name,
                    version
                )

                model = registry[dataset_name][model_name]
                version_data = model["versions"][version]

                # A Production model should not be moved backward.
                if version_data["stage"] == PRODUCTION:
                    raise ValueError(
                        f"Production version '{version}' cannot be promoted to Staging."
                    )

                old_staging = model["staging"]

                # Move previous staging version back to Development.
                if old_staging is not None and old_staging != version:
                    model["versions"][old_staging]["stage"] = DEVELOPMENT

                    self._update_metadata_stage(
                        dataset_name,
                        model_name,
                        old_staging,
                        DEVELOPMENT
                    )

                # Set new staging version.
                model["staging"] = version
                version_data["stage"] = STAGING

                self._update_metadata_stage(
                    dataset_name,
                    model_name,
                    version,
                    STAGING
                )

                self.save_registry(registry)

                return True

            except Exception:
                self.save_registry(backup)
                raise
    # =====================================================
    # Promote to Production
    # =====================================================

    def promote_to_production(
        self,
        dataset_name,
        model_name,
        version
    ):
        with self.lock:
            registry = self.load_registry()
            backup = copy.deepcopy(registry)

        try:
            self._validate_version(
                registry,
                dataset_name,
                model_name,
                version
            )

            model = registry[dataset_name][model_name]
            version_data = model["versions"][version]

            current_stage = version_data["stage"]

            # Production promotion MUST come from Staging.
            current_stage = version_data["stage"]

            # Already production: idempotent operation.
            if current_stage == PRODUCTION:
                if model["production"] == version:
                    return True

                raise ValueError(
                    f"Version '{version}' is marked Production "
                    f"but is not the active production version."
                )

            # Normal lifecycle requires Staging → Production.
            if current_stage != STAGING:
                raise ValueError(
                    f"Version '{version}' must be in {STAGING} "
                    f"before it can be promoted to {PRODUCTION}."
    )
            old_prod = model["production"]

            # Archive previous production model.
            if old_prod is not None and old_prod != version:

                model["versions"][old_prod]["stage"] = ARCHIVED

                self._update_metadata_stage(
                    dataset_name,
                    model_name,
                    old_prod,
                    ARCHIVED
                )

            # Remove version from staging.
            if model["staging"] == version:
                model["staging"] = None

            # Promote to production.
            model["production"] = version
            version_data["stage"] = PRODUCTION

            self._update_metadata_stage(
                dataset_name,
                model_name,
                version,
                PRODUCTION
            )

            self.save_registry(registry)

            return True

        except Exception:
            self.save_registry(backup)
            raise

    # =====================================================
    # Archive Version
    # =====================================================

    def archive_version(
        self,
        dataset_name,
        model_name,
        version
    ):

        with self.lock:

            registry = self.load_registry()
            backup = copy.deepcopy(registry)

            try:

                self._validate_version(
                    registry,
                    dataset_name,
                    model_name,
                    version
                )

                model = registry[dataset_name][model_name]

                model["versions"][version]["stage"] = ARCHIVED

                if model["production"] == version:
                    model["production"] = None

                if model["staging"] == version:
                    model["staging"] = None

                self._update_metadata_stage(
                    dataset_name,
                    model_name,
                    version,
                    ARCHIVED
                )

                self.save_registry(registry)

            except Exception:

                self.save_registry(backup)
                raise
        
    # =====================================================
    # Queries
    # =====================================================

    def list_versions(
        self,
        dataset_name,
        model_name
    ):

        registry = self.load_registry()

        self._validate_model(
            registry,
            dataset_name,
            model_name
        )

        return registry[dataset_name][model_name]["versions"]


    # =====================================================
    # Latest Version
    # =====================================================

    def latest_version(
        self,
        dataset_name,
        model_name
    ):

        registry = self.load_registry()

        self._validate_model(
            registry,
            dataset_name,
            model_name
        )

        return registry[dataset_name][model_name]["latest_version"]


    # =====================================================
    # Production Version
    # =====================================================

    def production_version(
        self,
        dataset_name,
        model_name
    ):

        registry = self.load_registry()

        self._validate_model(
            registry,
            dataset_name,
            model_name
        )

        return registry[dataset_name][model_name]["production"]


    # =====================================================
    # Staging Version
    # =====================================================

    def staging_version(
        self,
        dataset_name,
        model_name
    ):

        registry = self.load_registry()

        self._validate_model(
            registry,
            dataset_name,
            model_name
        )

        return registry[dataset_name][model_name]["staging"]


    # =====================================================
    # Get Production Model
    # =====================================================

    def get_production_model(
        self,
        dataset_name,
        model_name
    ):

        registry = self.load_registry()

        self._validate_model(
            registry,
            dataset_name,
            model_name
        )

        production = registry[dataset_name][model_name]["production"]

        if production is None:
            return None

        return os.path.join(
            self.models_dir,
            dataset_name,
            model_name,
            production,
            "model.joblib"
        )


    # =====================================================
    # Get Version Metadata
    # =====================================================

    def get_version_metadata(
        self,
        dataset_name,
        model_name,
        version
    ):

        self._validate_version(
            self.load_registry(),
            dataset_name,
            model_name,
            version
        )

        metadata_path = self._metadata_path(
            dataset_name,
            model_name,
            version
        )

        with open(metadata_path, "r") as f:
            return json.load(f)


    # =====================================================
    # Delete Version
    # =====================================================

    def delete_version(
        self,
        dataset_name,
        model_name,
        version
    ):

        with self.lock:

            registry = self.load_registry()
            backup = copy.deepcopy(registry)

            try:

                self._validate_version(
                    registry,
                    dataset_name,
                    model_name,
                    version
                )

                model = registry[dataset_name][model_name]

                if model["production"] == version:
                    raise ValueError(
                        f"Production version '{version}' cannot be deleted. "
                        f"Archive it before deletion."
                    )

                folder = os.path.join(
                    self.models_dir,
                    dataset_name,
                    model_name,
                    version
                )

                if os.path.exists(folder):
                    shutil.rmtree(folder)

                del registry[dataset_name][model_name]["versions"][version]

                if registry[dataset_name][model_name]["production"] == version:
                    registry[dataset_name][model_name]["production"] = None

                if registry[dataset_name][model_name]["staging"] == version:
                    registry[dataset_name][model_name]["staging"] = None

                versions = registry[dataset_name][model_name]["versions"]

                if versions:
                    latest = sorted(
                        versions.keys(),
                        key=lambda x: int(x[1:])
                    )[-1]

                    registry[dataset_name][model_name]["latest_version"] = latest

                else:

                    registry[dataset_name].pop(model_name)

                    if not registry[dataset_name]:
                        registry.pop(dataset_name)

                self.save_registry(registry)

            except Exception:

                self.save_registry(backup)
                raise