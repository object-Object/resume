import logging
import os
import subprocess
from pathlib import Path
from typing import Annotated

import yaml
from dotenv import load_dotenv
from jinja2 import Environment, PackageLoader, StrictUndefined
from typer import Option, Typer

from resume.models import Resume
from resume.resources import load_resource_dir
from resume.utils.logging import setup_logging

logger = logging.getLogger(__name__)

app = Typer(
    pretty_exceptions_show_locals=False,
)


@app.command()
def main(
    config_path: Annotated[
        Path,
        Option("--config", "-c", envvar="RESUME_CONFIG"),
    ] = Path("resume.yaml"),
    output_dir: Annotated[
        Path,
        Option("--output-dir", "-o", envvar="RESUME_OUTPUT"),
    ] = Path("out"),
    do_compile: Annotated[bool, Option("--compile")] = True,
    verbosity: Annotated[int, Option("--verbose", "-v", count=True)] = 0,
):
    setup_logging(verbosity, ci=is_ci())

    # load config

    logger.info(f"Loading config file: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        data = yaml.load(f, yaml.CLoader)
        resume = Resume.model_validate(data)

    # set up Jinja

    logger.info("Setting up Jinja environment.")

    env = Environment(
        loader=PackageLoader("resume"),
        undefined=StrictUndefined,
    )

    template_args = {
        "resume": resume,
    }

    # render template

    typst_filename = "resume.typ"
    typst_path = output_dir / typst_filename

    logger.info(f"Rendering Typst file: {typst_path}")

    template = env.get_template("resume.typ.jinja")
    result = template.render(template_args)

    output_dir.mkdir(parents=True, exist_ok=True)
    typst_path.write_text(result)

    # compile Typst to PDF

    if do_compile:
        logger.info("Compiling Typst file to PDF.")

        with load_resource_dir("fonts") as fonts_dir:
            logger.debug(f"{fonts_dir=}")
            subprocess.run(
                ["typst", "compile", typst_filename],
                cwd=output_dir,
                env={
                    "TYPST_FONT_PATHS": str(fonts_dir),
                },
                check=True,
            )


def is_ci():
    return bool(os.getenv("CI"))


if __name__ == "__main__":
    load_dotenv()
    app()
