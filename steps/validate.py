import glob
import logging
import subprocess
from pathlib import Path


def validateScripts():
    executionMap = {}
    for file in glob.iglob('output/*.py'):
        filename = Path(file).stem
        logging.info(f'validating {filename}')
        response = subprocess.call(file, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if response == 0:
            logging.info(f'{filename} successfully ran')
        else:
            logging.error(f'{filename} failed validation')

        executionMap[filename] = {
            'valid': response == 0,
            'hasCustomJS': '# TODO: Implement by hand' in open(file).read()
        }

    # save report
    with open(f'output/report.csv', 'w') as outfile:
        outfile.write('jobName,ranSuccessfully,hasCustomJS\n')
        for jobName, status in executionMap.items():
            outfile.write(f'{jobName},{status["valid"]},{status["hasCustomJS"]}\n')
