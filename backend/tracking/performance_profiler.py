import os
import time
import psutil


class PerformanceProfiler:

    @staticmethod
    def training_timer(start_time):
        return round(time.perf_counter() - start_time, 4)

    @staticmethod
    def inference_latency(model, X):

        sample = X.iloc[[0]]

        start = time.perf_counter()

        model.predict(sample)

        end = time.perf_counter()

        return round((end - start) * 1000, 4)

    @staticmethod
    def throughput(model, X):

        start = time.perf_counter()

        model.predict(X)

        end = time.perf_counter()

        elapsed = end - start

        if elapsed == 0:
            return 0

        return round(len(X) / elapsed, 2)

    @staticmethod
    def model_size(model_path):

        if os.path.exists(model_path):
            return round(
                os.path.getsize(model_path) / (1024 * 1024),
                3
            )

        return 0

    @staticmethod
    def process_memory():

        process = psutil.Process()

        return round(
            process.memory_info().rss / (1024 * 1024),
            2
        )

    @staticmethod
    def cpu_usage():

        return psutil.cpu_percent(interval=0.2)