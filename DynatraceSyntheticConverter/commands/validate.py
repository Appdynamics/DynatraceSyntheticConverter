import glob
import logging
import subprocess
from pathlib import Path

from click import command


@command(
    name='validate',
    help="""
    Validates generated scripts by running them locally.
    Creates report.csv in the output directory.
    """)
def validate():
    logging.info(f'-----Launching validate step-----')

    executionMap = {}
    for file in glob.iglob('output/*.py'):
        filename = Path(file).stem
        logging.info(f'validating {filename}')

        def log_subprocess_output(stdout, stderr):
            for line in iter(stdout.readline, b''):
                logging.info(f'script output: {line}')
            for line in iter(stderr.readline, b''):
                logging.error(f'script output: {line}')

        process = subprocess.Popen(['python', file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with process.stdout:
            log_subprocess_output(process.stdout, process.stderr)
        exitcode = process.wait()
        if exitcode == 0:
            logging.info(f'{filename} successfully ran')
        else:
            logging.error(f'{filename} failed validation')

        executionMap[filename] = {
            'valid': exitcode == 0,
            'hasCustomJS': 'driver.execute_script' in open(file).read()
        }

    # save report
    with open(f'output/report.csv', 'w') as outfile:
        outfile.write('jobName,ranSuccessfully,hasCustomJS\n')
        for jobName, status in executionMap.items():
            outfile.write(f'{jobName},{status["valid"]},{status["hasCustomJS"]}\n')
