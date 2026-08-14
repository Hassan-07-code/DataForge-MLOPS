import threading
from datetime import datetime


class ModelCache:
    """
    Thread-safe singleton cache for the production model.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):

        if cls._instance is None:

            with cls._lock:

                if cls._instance is None:

                    cls._instance = super().__new__(cls)

                    cls._instance.model = None
                    cls._instance.metadata = None
                    cls._instance.loaded_time = None
                    cls._instance.model_path = None

        return cls._instance

    # --------------------------------------------------
    # Store Model
    # --------------------------------------------------

    def set(
        self,
        model,
        metadata,
        model_path
    ):

        with self._lock:

            self.model = model
            self.metadata = metadata
            self.model_path = model_path
            self.loaded_time = datetime.now()

    # --------------------------------------------------
    # Get Model
    # --------------------------------------------------

    def get(self):

        return self.model

    # --------------------------------------------------
    # Get Metadata
    # --------------------------------------------------

    def get_metadata(self):

        return self.metadata

    # --------------------------------------------------
    # Model Path
    # --------------------------------------------------

    def get_path(self):

        return self.model_path

    # --------------------------------------------------
    # Loaded?
    # --------------------------------------------------

    def is_loaded(self):

        return self.model is not None

    # --------------------------------------------------
    # Clear Cache
    # --------------------------------------------------

    def clear(self):

        with self._lock:

            self.model = None
            self.metadata = None
            self.model_path = None
            self.loaded_time = None

    # --------------------------------------------------
    # Loaded Time
    # --------------------------------------------------

    def get_loaded_time(self):

        return self.loaded_time

    # --------------------------------------------------
    # Cache Information
    # --------------------------------------------------

    def info(self):

        return {

            "loaded": self.is_loaded(),

            "loaded_time": (
                self.loaded_time.isoformat()
                if self.loaded_time
                else None
            ),

            "model_path": self.model_path,

            "metadata": self.metadata

        }


cache = ModelCache()