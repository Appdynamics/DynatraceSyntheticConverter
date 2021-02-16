import json
import logging

from dyna_api.dyna_service import DynatraceService


def downloadScripts(url: str, token: str):
    dynatraceService = DynatraceService(url, token)
    monitors = dynatraceService.get_synthetic_monitors()
    if monitors.error is not None:
        logging.error(monitors.error.msg)
        return
    for monitorBase in monitors.data['monitors']:
        monitor = dynatraceService.get_synthetic_monitor(monitorBase['entityId'])
        if monitor.error is not None:
            logging.error(monitor.error.msg)
            return
        with open(f'input/{monitor.data["name"]}.json', 'w') as outfile:
            logging.debug(f'Saving {monitor.data["name"]}')
            outfile.write(json.dumps(monitor.data, indent=4, sort_keys=True))
