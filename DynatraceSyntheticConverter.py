import logging

from steps.generate import generateScripts
from steps.upload import uploadScripts
from steps.validate import validateScripts
from util.click_utils import *
from util.logging import initLogging


@click.group(name='DynatraceSyntheticConverter')
def DynatraceSyntheticConverter():
    """DT synthetic commands"""
    pass


@DynatraceSyntheticConverter.command(
    name='generate',
    help='''
    Generate python scripts from Dynatrace synthetic monitor JSON.
    Generated scripts are placed in the output directory and will overwrite existing scripts of the same name.  
    ''')
def generate_cmd():
    logging.info(f'-----Launching generate step-----')
    generateScripts()


@DynatraceSyntheticConverter.command(
    name='validate',
    help="""
    Validates generated scripts by running them locally.
    Creates report.csv in the output directory.
    """)
def validate_cmd():
    logging.info(f'-----Launching validate step-----')
    validateScripts()


@DynatraceSyntheticConverter.command(
    name='upload',
    help='''
    Upload generated scripts to AppD.
    If only-useful-scripts is chosen, only scripts from the output/report.csv which ranSuccessfully will be uploaded. 
    ''')
@click.option(
    '--host',
    prompt=True,
    help='acme.saas.appdynamics.com')
@click.option(
    '--port',
    prompt=True,
    cls=DynamicOptionPrompt,
    default_option='host',
    default=lambda x: parse_port_number_from_host(x),
    help="SaaS: 443\nOn Prem: 8090")
@click.option(
    '--ssl/--no-ssl',
    prompt=True,
    is_flag=True,
    cls=DynamicOptionPrompt,
    default_option='host',
    default=lambda x: parse_is_ssl_from_host(x))
@click.option(
    '--account',
    prompt=True,
    cls=DynamicOptionPrompt,
    default_option='host',
    default=lambda x: parse_account_from_host(x),
    help="SaaS: first segment of controller host\nOn Prem: customer1")
@click.option(
    '--username',
    prompt=True,
    help='must use local account')
@click.password_option()
@click.option(
    '--only-successful-scripts',
    help="Only scripts from the output/report.csv which ranSuccessfully will be uploaded.",
    is_flag=True)
@click.option(
    '--overwrite',
    help="Overwrite scripts on destination controller with the same name.",
    is_flag=True)
def upload_cmd(
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
    uploadScripts(host, port, ssl, account, username, password, only_successful_scripts, overwrite)


if __name__ == '__main__':
    """
    Automate the generation of AppDynamics synthetic scripts from Dynatrace synthetic monitor script output.
    """
    initLogging(logging.INFO)
    DynatraceSyntheticConverter()
