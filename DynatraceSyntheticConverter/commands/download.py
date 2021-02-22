import json
import logging
import os

from click import command, option

from DynatraceSyntheticConverter.api.dynatrace.dynatrace_service import DynatraceService


@command(
    name='download',
    help='''
    Download all synthetic monitors from Dynatrace.
    Downloaded scripts are placed in the input directory.  
    ''')
@option(
    '--url',
    prompt=True,
    help='acme.live.dynatrace.com')
@option(
    '--token',
    prompt=True)
def download(url: str, token: str):
    logging.info(f'-----Launching download step-----')

    dynatraceService = DynatraceService(url, token)
    monitors = dynatraceService.get_synthetic_monitors()
    if monitors.error is not None:
        logging.error(monitors.error.msg)
        return

    if not os.path.exists('input'):
        os.makedirs('input')

    for monitorBase in monitors.data['monitors']:
        monitor = dynatraceService.get_synthetic_monitor(monitorBase['entityId'])
        if monitor.error is not None:
            logging.error(monitor.error.msg)
            return

        with open(f'input/{monitor.data["name"]}.json', 'w') as outfile:
            logging.debug(f'Saving {monitor.data["name"]}')
            outfile.write(json.dumps(monitor.data, indent=4, sort_keys=True))
