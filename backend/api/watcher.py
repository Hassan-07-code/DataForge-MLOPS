import hashlib
import threading
import time
from pathlib import Path

from backend.api.prediction_logger import PredictionLogger
from backend.config.settings import (
    REGISTRY_DIR,
    WATCH_INTERVAL
)


class RegistryWatcher:
    """
    Background watcher for registry.json.

    Every WATCH_INTERVAL seconds:
        - checks registry.json hash
        - if changed -> reload production model
    """

    def __init__(self, loader):

        self.loader = loader

        self.logger = PredictionLogger()

        self.registry_file = (
            Path(REGISTRY_DIR) / "registry.json"
        )

        self.current_hash = None

        self.running = False

        self.thread = None

    # =====================================================
    # Hash
    # =====================================================

    def _file_hash(self):

        if not self.registry_file.exists():
            return None

        md5 = hashlib.md5()

        with open(self.registry_file, "rb") as f:

            while True:

                chunk = f.read(8192)

                if not chunk:
                    break

                md5.update(chunk)

        return md5.hexdigest()

    # =====================================================
    # Watch Loop
    # =====================================================

    def _watch(self):

        self.current_hash = self._file_hash()

        while self.running:

            try:

                time.sleep(WATCH_INTERVAL)

                new_hash = self._file_hash()

                if new_hash != self.current_hash:

                    self.current_hash = new_hash

                    self.logger.log_event(
                        "Registry Changed"
                    )

                    self._reload_all()

            except Exception as e:

                self.logger.log_event(
                    "Watcher Error",
                    {
                        "error": str(e)
                    }
                )

    # =====================================================
    # Reload
    # =====================================================

    def _reload_all(self):

        registry = self.loader.registry.load_registry()

        for dataset in registry:

            for model in registry[dataset]:

                try:

                    self.loader.reload(
                        dataset,
                        model
                    )

                    self.logger.log_event(

                        "Model Reloaded",

                        {

                            "dataset": dataset,

                            "model": model

                        }

                    )

                except Exception as e:

                    self.logger.log_event(

                        "Reload Failed",

                        {

                            "dataset": dataset,

                            "model": model,

                            "error": str(e)

                        }

                    )

    # =====================================================
    # Start
    # =====================================================

    def start(self):

        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(

            target=self._watch,

            daemon=True

        )

        self.thread.start()

        self.logger.log_event(
            "Registry Watcher Started"
        )

    # =====================================================
    # Stop
    # =====================================================

    def stop(self):

        self.running = False

        if self.thread is not None:

            self.thread.join(timeout=2)

        self.logger.log_event(
            "Registry Watcher Stopped"
        )