import csv
import glob
import json
import logging
from pathlib import Path

from click import command, option, password_option

from DynatraceSyntheticConverter.api.appd.appd_service import AppDService
from DynatraceSyntheticConverter.util.click_utils import DynamicOptionPrompt, parse_port_number_from_host, parse_is_ssl_from_host, parse_account_from_host


@command(
    name='upload',
    help='''
    Upload generated scripts to AppD.
    If only-useful-scripts is chosen, only scripts from the output/report.csv which ranSuccessfully will be uploaded. 
    ''')
@option(
    '--host',
    prompt=True,
    help='acme.saas.appdynamics.com')
@option(
    '--port',
    prompt=True,
    cls=DynamicOptionPrompt,
    default_option='host',
    default=lambda x: parse_port_number_from_host(x),
    help="SaaS: 443\nOn Prem: 8090")
@option(
    '--ssl/--no-ssl',
    prompt=True,
    is_flag=True,
    cls=DynamicOptionPrompt,
    default_option='host',
    default=lambda x: parse_is_ssl_from_host(x))
@option(
    '--account',
    prompt=True,
    cls=DynamicOptionPrompt,
    default_option='host',
    default=lambda x: parse_account_from_host(x),
    help="SaaS: first segment of controller host\nOn Prem: customer1")
@option(
    '--username',
    prompt=True,
    help='must use local account')
@password_option()
@option(
    '--only-successful-scripts',
    help="Only scripts from the output/report.csv which ranSuccessfully will be uploaded.",
    is_flag=True)
@option(
    '--overwrite',
    help="Overwrite scripts on destination controller with the same name.",
    is_flag=True)
def upload(
        host: str,
        port: int,
        ssl: bool,
        account: str,
        username: str,
        password: str,
        only_successful_scripts: bool,
        overwrite: bool
):
    logging.info(f'-----Launching upload step-----')

    controllerService = AppDService(host, port, ssl, account, username, password)
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
                response = controllerService.get_synthetic_jobs(jobMap['eumApplicationId'])
                if response.error is not None:
                    logging.error(response.error)
                    return
                uploadedJobs = response.data['jobListDatas']

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
                logging.error(f'Failed to upload synthetic script {filename} with error: {response.error}')
        else:
            logging.info(f'Only uploading validated scripts, skipping {filename}')
