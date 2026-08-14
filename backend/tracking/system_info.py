import platform
import psutil
import sklearn
import pandas
import numpy
import mlflow
import time


class SystemInfo:

    @staticmethod
    def collect():

        return {

            "python_version": platform.python_version(),

            "operating_system": platform.system(),

            "os_release": platform.release(),

            "machine": platform.machine(),

            "processor": platform.processor(),

            "cpu_cores_physical": psutil.cpu_count(logical=False),

            "cpu_cores_logical": psutil.cpu_count(),

            "ram_gb": round(
                psutil.virtual_memory().total / (1024**3),
                2
            ),

            "sklearn_version": sklearn.__version__,

            "pandas_version": pandas.__version__,

            "numpy_version": numpy.__version__,

            "mlflow_version": mlflow.__version__
        }

    @staticmethod
    def process_memory_mb():

        process = psutil.Process()

        return round(
            process.memory_info().rss / (1024 * 1024),
            2
        )

    @staticmethod
    def cpu_percent():

        return psutil.cpu_percent(interval=0.2)