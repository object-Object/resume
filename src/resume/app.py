import subprocess
from pathlib import Path
from typing import Annotated

import yaml
from dotenv import load_dotenv
from jinja2 import Environment, PackageLoader, StrictUndefined
from typer import Option, Typer

from resume.models import Resume

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
):
    # load config

    with config_path.open("r", encoding="utf-8") as f:
        data = yaml.load(f, yaml.CLoader)
        resume = Resume.model_validate(data)

    # set up Jinja

    env = Environment(
        loader=PackageLoader("resume"),
        undefined=StrictUndefined,
    )

    template_args = {
        "resume": resume,
    }

    # render template

    template = env.get_template("resume.tex.jinja")
    result = template.render(template_args)

    output_dir.mkdir(parents=True, exist_ok=True)
    tex_filename = "resume.tex"
    tex_path = output_dir / tex_filename
    tex_path.write_text(result)

    # compile LaTeX to PDF

    subprocess.run(
        ["pdflatex", tex_filename],
        cwd=output_dir,
        check=True,
    )


if __name__ == "__main__":
    load_dotenv()
    app()
