import json
import logging
from typing import Dict, Any

from uplink.auth import ApiTokenHeader

from DynatraceSyntheticConverter.api.Result import Result
from DynatraceSyntheticConverter.api.dynatrace.dynatrace_controller import DynatraceController


class DynatraceService:
    controller: DynatraceController

    def __init__(
            self,
            url: str,
            apiToken: str):
        logging.debug(f'Initializing Dynatrace controller service for {url}')
        auth = ApiTokenHeader('Authorization', f'Api-Token {apiToken}')
        self.controller = DynatraceController(base_url=url, auth=auth)

    def get_synthetic_monitors(self) -> Result[Dict]:
        logging.debug(f'Getting all synthetic monitors')
        response = self.controller.get_synthetic_monitors()
        error = None if response.status_code == 200 else Result.Error(response.status_code)
        return Result(json.loads(response.content), error)

    def get_synthetic_monitor(self, monitorId: str) -> Result[Dict]:
        logging.debug(f'Getting synthetic monitors')
        response = self.controller.get_synthetic_monitor(monitorId)
        error = None if response.status_code == 200 else Result.Error(response.status_code)
        return Result(json.loads(response.content), error)
