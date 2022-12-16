from __future__ import print_function, unicode_literals

import os
from gettext import install

import click

from ..templates.package import init_package
from ..templates.aws_lambda import init_lambda
from ..templates.settings import init_settings

################################################################
# eatpy
################################################################


@click.group()
def eatpy():
    pass


################################################################
# init
################################################################
@eatpy.group()
def init():
    pass


@init.command()
@click.argument("root")
def package(root):
    init_package(root)


@init.command()
@click.argument("root")
def aws_lambda(root):
    init_lambda(root)


@init.command()
@click.argument("root")
def settings(root):
    init_settings(root)

################################################################
# dotenv
################################################################


@eatpy.group()
def dotenv():
    pass


@dotenv.command()
def status():
    pass


@dotenv.command()
def push():
    pass
