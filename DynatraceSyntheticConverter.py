import logging
import click

from DynatraceSyntheticConverter.commands.download import download
from DynatraceSyntheticConverter.commands.generate import generate
from DynatraceSyntheticConverter.commands.upload import upload
from DynatraceSyntheticConverter.commands.validate import validate
from DynatraceSyntheticConverter.util.logging_utils import initLogging


@click.group()
def main():
    pass


if __name__ == '__main__':
    """
    Automate the generation of AppDynamics synthetic scripts from Dynatrace synthetic monitor script output.
    """
    initLogging(logging.INFO)

    main.add_command(download)
    main.add_command(generate)
    main.add_command(validate)
    main.add_command(upload)

    main()
