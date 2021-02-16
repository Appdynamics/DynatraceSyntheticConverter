from requests import Response
from uplink import Consumer, get, params, error_handler, post, Path, Body


class ApiError(Exception):
    pass


def raise_api_error(exc_type, exc_val, exc_tb):
    raise ApiError(exc_val)


@error_handler(raise_api_error)
class DynatraceController(Consumer):
    """Minimal python client for the Dynatrace API"""
    authToken: str

    @params({"output": "json"})
    @get("/api/v1/synthetic/monitors")
    def get_synthetic_monitors(self):
        """Retrieves all applications"""

    @params({"output": "json"})
    @get("/api/v1/synthetic/monitors/{monitorId}")
    def get_synthetic_monitor(self, monitorId: Path):
        """Retrieves all applications"""
