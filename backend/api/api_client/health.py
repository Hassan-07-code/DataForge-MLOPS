from backend.api.api_client.client import APIClient


class HealthClient:

    def __init__(self):

        self.client = APIClient()

    # =====================================================
    # Health Check
    # =====================================================

    def is_alive(self):

        try:

            response = self.client.get("/api/health")

            return response.status_code == 200

        except Exception:

            return False

    # =====================================================
    # Health Details
    # =====================================================

    def status(self):

        response = self.client.get("/api/health")

        return response.json()