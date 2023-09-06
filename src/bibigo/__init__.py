from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("{package_name}")
except PackageNotFoundError:
    # package is not installed
    pass
