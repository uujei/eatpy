from __future__ import print_function, unicode_literals

import os
from gettext import install

import click
from rich.console import Console
from rich.panel import Panel

console = Console(width=88)

from ..templates.package import (
    _generate_gitignore,
    _generate_pyproject_toml,
    _generate_setup_cfg,
    _generate_vscode_settings,
)


@click.group()
def pie():
    pass


@pie.command()
@click.argument("root")
def init(root):

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
                {"name": ".vscode/setting.json", "checked": True},
                {"name": "<module>/__init__.py", "checked": True},
            ],
        },
        {"type": "confirm", "name": "confirm", "message": "Confirm Initializer"},
    ]
    conf = prompt(q_setup_cfg)
    confirm = conf.pop("confirm")
    if not confirm:
        print("[EXIT] Nothing Happend!")
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
