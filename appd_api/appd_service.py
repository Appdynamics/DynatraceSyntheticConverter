import json
import logging
import re
import sys
from dataclasses import dataclass
from typing import Any

from uplink import Body

from appd_api.appd_controller import AppdController


@dataclass
class Result:
    """Basic implementation of  'Go-like' error handling"""

    @dataclass
    class Error:
        msg: str

    data: Any
    error: Error


class AppDService:
    controller: AppdController

    def __init__(
            self,
            host: str,
            port: int,
            ssl: bool,
            accountname: str,
            username: str,
            pwd: str):
        logging.debug(f'Initializing controller service for {host}')
        connection_url = f'{"https" if ssl else "http"}://{host}:{port}'
        auth = (f'{username}@{accountname}', pwd)
        self.controller = AppdController(base_url=connection_url, auth=auth)

    def login_to_controller(self) -> Result:
        logging.debug("Attempt controller connection.")
        response = self.controller.login()
        if response.status_code is not 200:
            logging.error(f'Controller login failed with {response.status_code}')
            return Result(response, Result.Error(f'Controller login failed with {response.status_code}'))

        try:
            jsessionid = re.search('JSESSIONID=(\\w|\\d)*', response.headers['Set-Cookie']) \
                .group(0).split('JSESSIONID=')[1]
            self.controller.jsessionid = jsessionid
        except AttributeError:
            logging.debug("JSESSIONID not returned, already logged in with valid credentials.")
        try:
            xcsrftoken = re.search('X-CSRF-TOKEN=(\\w|\\d)*', response.headers['Set-Cookie']) \
                .group(0).split('X-CSRF-TOKEN=')[1]
            self.controller.xcsrftoken = xcsrftoken
        except AttributeError:
            logging.debug("X-CSRF-TOKEN not returned, already logged in with valid credentials.")

        self.controller.session.headers['X-CSRF-TOKEN'] = self.controller.xcsrftoken
        self.controller.session.headers[
            "Set-Cookie"] = f"JSESSIONID={self.controller.jsessionid};X-CSRF-TOKEN={self.controller.xcsrftoken};"
        self.controller.session.headers['Content-Type'] = 'application/json;charset=UTF-8'

        logging.debug(f'Controller initialization successful.')
        return Result(self.controller, None)

    def get_applications(self) -> Result:
        logging.debug(f'Gathering applications')
        response = self.controller.get_applications()
        error = None if response.status_code == 200 else Result.Error(response.status_code)
        return Result(json.loads(response.content), error)

    def create_synthetic_job(self, jobMap, synthetic_name: str, code: str) -> Result:
        logging.debug(f'Creating synthetic job {synthetic_name} for application {jobMap["eumApplicationId"]}')
        self.login_to_controller()
        code = code\
            .encode("unicode_escape").decode("utf-8") \
            .replace("\"", "\\\"")
        body = open("resources/appd\syntheticPayload.json") \
            .read() \
            .replace("$code", str(code)) \
            .replace("$syntheticName", str(synthetic_name)) \
            .replace("$browserCodes", f'{jobMap["browserCodes"].split(",")}'.replace("'", '"')) \
            .replace("$locationCodes", f'{jobMap["locationCodes"].split(",")}'.replace("'", '"')) \
            .replace("$timeoutSeconds", jobMap["timeoutSeconds"]) \
            .replace("$executionRateValue", jobMap["executionRateValue"]) \
            .replace("$executionRateUnit", jobMap["executionRateUnit"])
        response = self.controller.create_synthetic_job(jobMap["eumApplicationId"], body)
        if response.status_code == 204:
            error = None
        elif response.status_code == 500:
            error = Result.Error('Already Exists')
        else:
            error = Result.Error(response.status_code)
        return Result(None, error)

    def overwrite_synthetic_job(self, jobMap, synthetic_name: str, code: str, uploadedJob) -> Result:
        logging.debug(f'Creating synthetic job {synthetic_name} for application {jobMap["eumApplicationId"]}')
        self.login_to_controller()

        uploadedJob['config']['script']['script'] = code
        uploadedJob['config']['browserCodes'] = jobMap["browserCodes"].split(",")
        uploadedJob['config']['locationCodes'] = jobMap["locationCodes"].split(",")
        uploadedJob['config']['timeoutSeconds'] = int(jobMap["timeoutSeconds"])
        uploadedJob['config']['rate']['value'] = int(jobMap["executionRateValue"])
        uploadedJob['config']['rate']['unit'] = jobMap["executionRateUnit"]

        response = self.controller.create_synthetic_job(jobMap['eumApplicationId'], json.dumps(uploadedJob['config']))
        error = None if response.status_code == 204 else Result.Error(response.status_code)
        return Result(None, error)

    def get_synthetic_jobs(self, eumApplicationId: str) -> Result:
        logging.debug(f'Getting synthetic jobs for application {eumApplicationId}')
        self.login_to_controller()
        response = self.controller.get_synthetic_jobs(eumApplicationId)
        error = None if response.status_code == 200 else Result.Error(response.status_code)
        return Result(json.loads(response.content), error)
