import requests

from backend.config.settings import (
    API_HOST,
    API_PORT,
    API_TIMEOUT
)

from backend.api.api_client.exceptions import (
    APIConnectionError,
    APITimeoutError,
    APIServerError
)


class APIClient:

    def __init__(

        self,

        host=API_HOST,

        port=API_PORT,

        timeout=API_TIMEOUT

    ):

        self.base_url = f"http://{host}:{port}"

        self.timeout = timeout

    # =====================================================
    # URL
    # =====================================================

    def url(self, endpoint):

        if not endpoint.startswith("/"):

            endpoint = "/" + endpoint

        return self.base_url + endpoint

    # =====================================================
    # GET
    # =====================================================

    def get(

        self,

        endpoint,

        params=None

    ):

        try:

            response = requests.get(

                self.url(endpoint),

                params=params,

                timeout=self.timeout

            )

        except requests.exceptions.ConnectionError:

            raise APIConnectionError(
                "Cannot connect to DataForge API."
            )

        except requests.exceptions.Timeout:

            raise APITimeoutError(
                "API request timed out."
            )

        if response.status_code >= 500:

            raise APIServerError(
                response.text
            )

        return response

    # =====================================================
    # POST
    # =====================================================

    def post(

        self,

        endpoint,

        payload

    ):

        try:

            response = requests.post(

                self.url(endpoint),

                json=payload,

                timeout=self.timeout

            )

        except requests.exceptions.ConnectionError:

            raise APIConnectionError(
                "Cannot connect to DataForge API."
            )

        except requests.exceptions.Timeout:

            raise APITimeoutError(
                "API request timed out."
            )

        if response.status_code >= 500:

            raise APIServerError(
                response.text
            )

        return response

    # =====================================================
    # Ping
    # =====================================================

    def ping(self):

        try:

            response = self.get("/")

            return response.status_code == 200

        except Exception:

            return False