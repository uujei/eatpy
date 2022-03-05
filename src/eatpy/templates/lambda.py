import json
import os

from rich.console import Console
from rich.panel import Panel

from common import _generate_gitignore, _generate_vscode_settings, _list_to_cfg_format, _makedir_and_write

console = Console(width=88)

APP_DIR = "app"
APP = "app.py"
HANDLER = "handler"

################################################################
# init package
################################################################
def init_lambda(root):
    from PyInquirer import print_json, prompt

    root = os.path.abspath(root)
    lambda_func = root.rsplit("/", 1)[-1]

    questions = [
        {"type": "input", "name": "lambda_func", "default": lambda_func, "message": "Lambda Function Name"},
        {"type": "input", "name": "python_version", "default": "3.8", "message": "Python Version"},
        {"type": "input", "name": "maintainer", "message": "Maintainer"},
        {"type": "input", "name": "maintainer_email", "message": "Maintainer Email"},
        {
            "type": "input",
            "name": "install_requires",
            "message": "Requirements",
            "filter": lambda x: [_.strip() for _ in x.split(",")],
        },
        {
            "type": "checkbox",
            "name": "files",
            "message": "Select Options",
            "choices": [
                {"name": ".gitignore", "checked": True},
                {"name": ".vscode/settings.json", "checked": True},
            ],
        },
        {"type": "confirm", "name": "confirm", "message": "Confirm Initializer"},
    ]
    conf = prompt(questions)
    confirm = conf.pop("confirm")

    # write common files
    if not confirm:
        print("[EXIT] Nothing Happened!")
        return
    files = conf.pop("files")
    if ".vscode/settings.json" in files:
        _generate_vscode_settings(root=root)
    if ".gitignore" in files:
        _generate_gitignore(root=root)

    # write
    _generate_requirements_txt(root=root, conf=conf)
    _generate_app_py(root=root, conf=conf)
    _generate_dockerfile(root=root, conf=conf)

    summary = "\n".join(
        [
            f"[bold]Python Lambda Function '{lambda_func}' is ready.[/bold]",
        ]
    )

    print()
    console.print(Panel(summary))


################################################################
# requirements.txt
################################################################
def _generate_requirements_txt(root, conf):
    FILE = "requirements.txt"
    content = "\n".join(conf.get("requirements", []))
    fp = os.path.join(root, FILE)
    _makedir_and_write(fp, content)


################################################################
# <app>.py
################################################################
APP_PY = f"""\
def {HANDLER}(event, context):
    return {"results": "Hello, World!", "event": event, "context": context}
"""


# <app>.py
def _generate_app_py(root, conf):
    FILE = f"{conf.get('app_name', 'app')}.py"
    content = APP_PY
    fp = os.path.join(root, APP_DIR, FILE)
    _makedir_and_write(fp, content)


################################################################
# setup.cfg
################################################################
def GEN_DOCKERFILE(python_version):
    return f"""\
# 가장 기본적인 Dockerfile for AWS lambda
FROM public.ecr.aws/lambda/python:{python_version}
ENV LAMBDA_TASK_ROOT=/var/run

# app 폴더에 있는 코드를 이미지로 복사합니다.
COPY ./{APP_DIR}/* ${{LAMBDA_TASK_ROOT}}

# Install python packages.
COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${{LAMBDA_TASK_ROOT}}"

# Set the CMD to your handler.
#  - could also be done as a parameter override outside of the Dockerfile
CMD [ "{APP}.{HANDLER}" ]
"""


# Dockerfile
def _generate_dockerfile(root, conf):
    FILE = "Dockerfile"
    python_version = conf.get("python_version", "3.8")
    content = GEN_DOCKERFILE(python_version)
    fp = os.path.join(root, FILE)
    _makedir_and_write(fp, content)
