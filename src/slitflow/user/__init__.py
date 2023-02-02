import sys
import importlib
import pkgutil


def import_all(package_name):
    package = sys.modules[package_name]
    return {name: importlib.import_module(package_name + '.' + name)
            for _, name, _ in pkgutil.walk_packages(package.__path__)}


__all__ = import_all(__name__).keys()
