import json
import logging
import threading
from datetime import datetime
from pathlib import Path

from backend.config.settings import LOGS_DIR


class PredictionLogger:
    """
    Enterprise Prediction Logger

    Logs every inference request in JSONL format.

    One request = One JSON object
    """

    def __init__(self):

        Path(LOGS_DIR).mkdir(
            parents=True,
            exist_ok=True
        )

        self.log_file = Path(LOGS_DIR) / "predictions.jsonl"

        self.lock = threading.Lock()

        self.logger = logging.getLogger("PredictionLogger")

        self.logger.setLevel(logging.INFO)

        self.logger.propagate = False

        if not self.logger.handlers:

            handler = logging.FileHandler(
                self.log_file,
                encoding="utf-8"
            )

            handler.setFormatter(
                logging.Formatter("%(message)s")
            )

            self.logger.addHandler(handler)

    # =====================================================
    # Internal
    # =====================================================

    def _write(self, payload: dict):

        with self.lock:

            self.logger.info(
                json.dumps(
                    payload,
                    default=str
                )
            )

    # =====================================================
    # Success
    # =====================================================

    def log_prediction(

        self,

        client_ip,

        endpoint,

        dataset_name,

        model_name,

        version,

        latency_ms,

        prediction_count,

        status="Success"

    ):

        payload = {

            "timestamp": datetime.utcnow().isoformat(),

            "client_ip": client_ip,

            "endpoint": endpoint,

            "dataset": dataset_name,

            "model": model_name,

            "version": version,

            "latency_ms": round(
                latency_ms,
                3
            ),

            "prediction_count": prediction_count,

            "status": status

        }

        self._write(payload)

    # =====================================================
    # Error
    # =====================================================

    def log_error(

        self,

        client_ip,

        endpoint,

        dataset_name,

        model_name,

        error

    ):

        payload = {

            "timestamp": datetime.utcnow().isoformat(),

            "client_ip": client_ip,

            "endpoint": endpoint,

            "dataset": dataset_name,

            "model": model_name,

            "status": "FAILED",

            "error": str(error)

        }

        self._write(payload)

    # =====================================================
    # Generic Event
    # =====================================================

    def log_event(

        self,

        event,

        details=None

    ):

        payload = {

            "timestamp": datetime.utcnow().isoformat(),

            "event": event,

            "details": details or {}

        }

        self._write(payload)

    # =====================================================
    # Read Logs
    # =====================================================

    def tail(

        self,

        lines=100

    ):

        if not self.log_file.exists():

            return []

        with open(

            self.log_file,

            "r",

            encoding="utf-8"

        ) as f:

            records = f.readlines()

        return [

            json.loads(x)

            for x in records[-lines:]

        ]

    # =====================================================
    # Clear Logs
    # =====================================================

    def clear(self):
    
        with self.lock:

            # Flush and close existing handlers
            for handler in self.logger.handlers[:]:
                try:
                    handler.flush()
                    handler.close()
                    self.logger.removeHandler(handler)
                except Exception:
                    pass

            # Remove existing log file
            if self.log_file.exists():
                self.log_file.unlink()

            # Recreate the file handler
            handler = logging.FileHandler(
                self.log_file,
                encoding="utf-8"
            )

            handler.setFormatter(
                logging.Formatter("%(message)s")
            )

            self.logger.addHandler(handler)