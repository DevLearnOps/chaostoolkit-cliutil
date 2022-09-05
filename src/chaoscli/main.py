import os
import subprocess
import tempfile
import typing

import click
import yaml

from . import models
from .aws import s3
from .util import file as file_utils

DEFAULT_ENCODING = "UTF-8"


class Param:
    def __init__(self, paramstr: str):
        key, value = paramstr.strip().split("=", maxsplit=1)
        self.key = key
        self.value = value

    def __repr__(self):
        return f"({self.key}: {self.value})"

    @classmethod
    def to_dict(
        cls, param_strings: typing.List[str]
    ) -> typing.Dict[str, typing.Any]:
        """Converts list of parameter strings to dictionary"""
        params = [cls(param) for param in param_strings]
        return {p.key: p.value for p in params}


def _resolve(param: typing.List[str], param_file: str, experiment: str):
    configuration = {}
    if param:
        configuration = Param.to_dict(param)
    elif param_file:
        with open(param_file, "r", encoding=DEFAULT_ENCODING) as file:
            data = yaml.safe_load(file.read())
        configuration = data.get("configuration")

    with open(experiment, "r", encoding=DEFAULT_ENCODING) as file:
        content = file.read()

    resolved = file_utils.render_jinja2_template(
        content, configuration=configuration
    )
    return resolved


@click.group(help="Resolve and run chaostoolkit experiments")
def cli():
    """Main entrypoint for chaostoolkit-cliutil"""


@cli.command(
    "resolve",
    help=(
        "Resolves the experiment template in EXPERIMENT file "
        "and writes the rendered experiments to standard output."
    ),
)
@click.option(
    "--param",
    "-p",
    multiple=True,
    required=False,
    help="Override template parameter",
)
@click.option(
    "--param-file",
    "-f",
    required=False,
    type=click.Path(exists=True),
    help="A verification definition file to use as parameters source",
)
@click.option(
    "--outfile",
    "-o",
    required=False,
    help="Writes the rendered experiment to a file",
)
@click.argument("experiment", required=True, type=click.Path(exists=True))
def resolve(
    param: typing.List[str], param_file: str, outfile: str, experiment: str
):
    resolved = _resolve(param, param_file, experiment)

    if outfile:
        with open(outfile, "w", encoding=DEFAULT_ENCODING) as file:
            file.write(resolved)
    else:
        print(resolved)


@cli.command(
    "runlocal",
    help=(
        "Resolves the experiment template in EXPERIMENT file "
        "and runs the chaos experiment."
    ),
)
@click.option(
    "--param",
    "-p",
    multiple=True,
    required=False,
    help="Override template parameter",
)
@click.option(
    "--param-file",
    "-f",
    required=False,
    type=click.Path(exists=True),
    help="A verification definition file to use as parameters source",
)
@click.option(
    "--verbose",
    "-v",
    required=False,
    is_flag=True,
    help="Verbose output",
)
@click.argument("experiment", required=True, type=click.Path(exists=True))
def runlocal(
    param: typing.List[str], param_file: str, experiment: str, verbose: bool
):
    resolved = _resolve(param, param_file, experiment)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml"
    ) as temp_experiment:
        temp_experiment.write(resolved)
        temp_experiment.flush()

        cmd = ["chaos"]
        if verbose:
            cmd.append("--verbose")
        cmd.append("run")

        cmd.append(f"{temp_experiment.name}")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as err:
            print(str(err))


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

        try:
            subprocess.run(cmd.render(), check=True, cwd=tempdirname)
        except subprocess.CalledProcessError:
            pass

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
