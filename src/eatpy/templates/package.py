import json
import os

from rich.console import Console
from rich.panel import Panel

from common import _generate_gitignore, _generate_vscode_settings, _list_to_cfg_format, _makedir_and_write

console = Console(width=88)

################################################################
# init package
################################################################
def init_package(root):
    from PyInquirer import print_json, prompt

    root = os.path.abspath(root)
    project = root.rsplit("/", 1)[-1]

    q_setup_cfg = [
        {"type": "input", "name": "project", "default": project, "message": "Project Name"},
        {"type": "input", "name": "author", "message": "Author"},
        {"type": "input", "name": "author_email", "message": "Author Email"},
        {"type": "input", "name": "description", "message": "Description"},
        {"type": "input", "name": "long_description", "default": "file: README.md", "message": "Long Description"},
        {"type": "input", "name": "keywords", "message": "Keywords"},
        {"type": "input", "name": "license", "default": "MIT License", "message": "License"},
        {"type": "input", "name": "python_requires", "default": ">= 3.8", "message": "Python Requires"},
        {
            "type": "input",
            "name": "install_requires",
            "message": "Install Requires",
            "filter": lambda x: [_.strip() for _ in x.split(",")],
        },
        {
            "type": "checkbox",
            "name": "files",
            "message": "Select Options",
            "choices": [
                {"name": ".gitignore", "checked": True},
                {"name": ".vscode/settings.json", "checked": True},
                {"name": "<module>/__init__.py", "checked": True},
            ],
        },
        {"type": "confirm", "name": "confirm", "message": "Confirm Initializer"},
    ]
    conf = prompt(q_setup_cfg)
    confirm = conf.pop("confirm")
    if not confirm:
        print("[EXIT] Nothing Happened!")
        return
    files = conf.pop("files")
    _generate_setup_cfg(root=root, **conf)
    _generate_pyproject_toml(root=root)

    if ".vscode/settings.json" in files:
        _generate_vscode_settings(root=root)
    if ".gitignore" in files:
        _generate_gitignore(root=root)
    if "<module>/__init__.py" in files:
        _module_init = os.path.join("src", project.replace("-", "_"), "__init__.py")
        _module_init_abs = os.path.join(root, _module_init)
        if not os.path.exists(_module_init_abs):
            os.makedirs(_module_init_abs.rsplit("/", 1)[0], exist_ok=True)
            with open(_module_init_abs, "w") as f:
                f.write(f"# MODULE NAME: {project}")
                f.write("")

    summary = "\n".join(
        [
            f"[bold]Python project '{project}' is ready.[/bold]",
            " - Build Package: 'python -m build', python package 'build' is required.",
            " - Upload to PyPI: 'twine upload dist/*', python package 'twine is required.",
        ]
    )

    print()
    console.print(Panel(summary))


################################################################
# setup.cfg
################################################################
def GEN_SETUP_CFG(
    project, description, long_description, author, author_email, keywords, license, python_requires, install_requires
):
    return f"""\
[metadata]
name = {project}
description = {description}
long_description = {long_description}
author = {author}
author_email = {author_email}
keywords = {keywords}
license = {license}

[options]
python_requires = {python_requires}
package_dir=
    =src
packages = find:
install_requires = {_list_to_cfg_format(install_requires)}
include_package_data = True

[options.packages.find]
where = src

[options.entry_points]
console_scripts =
    # <cli command> = <module>.<submodule>:<function>
"""


def _generate_setup_cfg(root, **kwargs):
    FILE = "setup.cfg"
    content = GEN_SETUP_CFG(**kwargs)
    fp = os.path.join(root, FILE)
    _makedir_and_write(fp, content)


################################################################
# pyproject.toml
################################################################
PYPROJECT_TOML = """\
[build-system]
requires = [ "setuptools>=41", "wheel", "setuptools-git-versioning" ]
build-backend = "setuptools.build_meta"

[tool.setuptools-git-versioning]
enabled = true
template = "{tag}"
"""


def _generate_pyproject_toml(root):
    FILE = "pyproject.toml"
    content = PYPROJECT_TOML
    fp = os.path.join(root, FILE)
    _makedir_and_write(fp, content)
