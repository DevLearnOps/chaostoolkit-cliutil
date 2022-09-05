import os
import subprocess
import tempfile

import click

from . import models
from .aws import s3


@click.group(help="Run a ChaosToolkit experiment")
def cli():
    pass


@cli.command("run")
@click.option(
    "--config-file",
    "-c",
    required=True,
    help="The location of the chaos config file",
)
def run(config_file: str):
    experiment_path = os.path.dirname(config_file)
    config_file_name = os.path.basename(config_file)

    with tempfile.TemporaryDirectory(prefix="ctk_") as tempdirname:
        s3.download_objects(experiment_path, outdir=tempdirname)

        cmd = models.CtkCommand.from_file(
            os.path.join(tempdirname, config_file_name)
        )

        subprocess.run(cmd.render(), check=True, cwd=tempdirname)

        s3.upload_file(
            os.path.join(tempdirname, "chaostoolkit.log"),
            os.path.join(experiment_path, "chaostoolkit.log"),
        )
        s3.upload_file(
            os.path.join(tempdirname, "journal.json"),
            os.path.join(experiment_path, "journal.json"),
        )


if __name__ == "__main__":
    cli()
