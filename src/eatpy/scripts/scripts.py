from __future__ import print_function, unicode_literals

import os
from gettext import install

import click

from ..templates.package import init_package


################################################################
# CLIs
################################################################
@click.group()
def eatpy():
    pass


@eatpy.group()
def init():
    pass


@init.command()
@click.argument("root")
def package(root):
    init_package(root)
