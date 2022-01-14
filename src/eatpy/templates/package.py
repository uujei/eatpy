import json
import os


################################################################
# Helpers
################################################################
# make dir if not exist and write file
def _makedir_and_write(fp, content, mode="w"):
    # make directory
    _dir = fp.rsplit("/", 1)[0]
    os.makedirs(_dir, exist_ok=True)

    # write file
    _ext = fp.rsplit(".", 1)[-1]
    with open(fp, mode) as f:
        if _ext.lower() in ["json"]:
            json.dump(content, f)
        else:
            f.write(content)


# list of string to setup.cfg format
def _list_to_cfg_format(x: list):
    TAB = "    "
    if x is None:
        return ""

    if "" not in x:
        x = ["", *x]
    return f"\n{TAB}".join(x)


################################################################
# setup.cfg
################################################################
def _generate_setup_cfg(
    root,
    project,
    description,
    long_description,
    author,
    author_email,
    keywords,
    license,
    python_requires,
    install_requires,
):
    FILE = "setup.cfg"

    content = f"""\
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

    fp = os.path.join(root, FILE)
    _makedir_and_write(fp, content)


################################################################
# pyproject.toml
################################################################
def _generate_pyproject_toml(root):
    FILE = "pyproject.toml"

    content = f"""\
[build-system]
requires = [ "setuptools>=41", "wheel", "setuptools-git-versioning" ]
build-backend = "setuptools.build_meta"

[tool.setuptools-git-versioning]
enabled = true
template = "{{tag}}"
"""

    fp = os.path.join(root, FILE)
    _makedir_and_write(fp, content)


################################################################
# .vscode/setting.json
################################################################
def _generate_vscode_settings(root):
    FILE = ".vscode/settings.json"

    content = {
        "python.formatting.provider": "black",
        "python.formatting.blackArgs": ["--line-length", "119"],
        "python.linting.flake8Enabled": True,
        "python.linting.enabled": True,
        "editor.formatOnSave": True,
        "autoDocstring.generateDocstringOnEnter": True,
        "autoDocstring.docstringFormat": "sphinx",
    }

    fp = os.path.join(root, FILE)
    _makedir_and_write(fp, content)


################################################################
# .gitignore
################################################################
def _generate_gitignore(root):
    FILE = ".gitignore"

    content = """\
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# IPython and Jupyter Notebook
profile_default/
ipython_config.py
.ipynb_checkpoints

# pyenv
.python-version

# PEP 582; used by e.g. github.com/David-OConnor/pyflow
__pypackages__/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# Pyre type checker
.pyre/
"""

    fp = os.path.join(root, FILE)
    _makedir_and_write(fp, content)
