from requests import Response
from uplink import Consumer, get, params, error_handler, post, Path, Body


class ApiError(Exception):
    pass


def raise_api_error(exc_type, exc_val, exc_tb):
    raise ApiError(exc_val)


@error_handler(raise_api_error)
class AppdController(Consumer):
    """Minimal python client for the AppDynamics API"""
    jsessionid: str = None
    xcsrftoken: str = None

    @params({"action": "login"})
    @get("/controller/auth")
    def login(self):
        """Verifies login success."""

    @params({"output": "json"})
    @get("/controller/rest/applications")
    def get_applications(self):
        """Retrieves all applications"""

    @params({"output": "json"})
    @post("controller/restui/synthetic/schedule/{application_id}/updateSchedule")
    def create_synthetic_job(self, application_id: Path('application_id'), body: Body):
        """Creates/updates synthetic job"""

    @params({"output": "json"})
    @post("controller/restui/synthetic/schedule/getJobList/{application_id}")
    def get_synthetic_jobs(self, application_id: Path):
        """Gets synthetic jobs"""
