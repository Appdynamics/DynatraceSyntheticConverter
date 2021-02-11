import csv
import glob
import json
import logging
from pathlib import Path

from appd_api.appd_service import AppDService


def uploadScripts(
        host: str,
        port: int,
        ssl: bool,
        accountname: str,
        username: str,
        pwd: str,
        only_successful_scripts: bool,
        overwrite: bool
):
    controllerService = AppDService(host, port, ssl, accountname, username, pwd)
    if controllerService.login_to_controller().error is not None:
        return

    with open('input/mapping.csv') as f:
        allMappings = [{k: str(v) for k, v in row.items()}
                       for row in csv.DictReader(f, skipinitialspace=True)]

    # validate mapping file
    for file in glob.iglob('output/*.py'):
        filename = Path(file).stem
        if not any(entry['jobName'] == filename for entry in allMappings):
            logging.error(f'{filename} not found in mapping file, exiting')
            return

    # pre-load our report
    if only_successful_scripts:
        with open('output/report.csv') as f:
            report = [{k: str(v) for k, v in row.items()}
                      for row in csv.DictReader(f, skipinitialspace=True)]

    # pre-load our jobs uploaded to AppD
    if overwrite:
        response = controllerService.get_synthetic_jobs('918')
        if response.error is not None:
            logging.error(response.error)
            return
        uploadedJobs = response.data['jobListDatas']

    for file in glob.iglob('output/*.py'):
        filename = Path(file).stem

        # only upload scripts which ranSuccessfully
        shouldUpload = True
        if only_successful_scripts:
            reportMapping = next(entry for entry in report if entry['jobName'] == filename)
            if not json.loads(reportMapping['ranSuccessfully'].lower()):
                shouldUpload = False
        if shouldUpload:
            code = open(file).read()
            jobMap = next(mapping for mapping in allMappings if mapping['jobName'] == filename)
            if overwrite:
                uploadedJob = next((job for job in uploadedJobs if job['config']['description'] == filename), None)
                if uploadedJob is not None:
                    response = controllerService.overwrite_synthetic_job(jobMap, filename, code, uploadedJob)
                else:
                    response = controllerService.create_synthetic_job(jobMap, filename, code)
            else:
                response = controllerService.create_synthetic_job(jobMap, filename, code)
            if response.error is None:
                logging.info(f'Successfully uploaded synthetic script {filename}')
            elif response.error.msg == 'Already Exists':
                logging.info(f'Synthetic script {filename} already exists. You can optionally run with --overwrite.')
            else:
                logging.error(f'Failed to upload synthetic script {filename} with status code {response.error}')
        else:
            logging.info(f'Only uploading validated scripts, skipping {filename}')
