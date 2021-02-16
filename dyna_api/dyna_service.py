import json
import logging
import re
import sys
from dataclasses import dataclass
from typing import Any

from uplink import Body
from uplink.auth import ApiTokenHeader

from appd_api.appd_controller import AppdController
from dyna_api.dyna_controller import DynatraceController


@dataclass
class Result:
    """Basic implementation of  'Go-like' error handling"""

    @dataclass
    class Error:
        msg: str

    data: Any
    error: Error


class DynatraceService:
    controller: DynatraceController

    def __init__(
            self,
            url: str,
            apiToken: str):
        logging.debug(f'Initializing Dynatrace controller service for {url}')
        auth = ApiTokenHeader('Authorization', f'Api-Token {apiToken}')
        self.controller = DynatraceController(base_url=url, auth=auth)

    def get_synthetic_monitors(self) -> Result:
        logging.debug(f'Getting all synthetic monitors')
        response = self.controller.get_synthetic_monitors()
        error = None if response.status_code == 200 else Result.Error(response.status_code)
        return Result(json.loads(response.content), error)

    def get_synthetic_monitor(self, monitorId: str) -> Result:
        logging.debug(f'Getting synthetic monitors')
        response = self.controller.get_synthetic_monitor(monitorId)
        error = None if response.status_code == 200 else Result.Error(response.status_code)
        return Result(json.loads(response.content), error)
