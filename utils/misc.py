from pathlib import Path
from types import ModuleType
from typing import Union, Type, Iterable, TypeVar, List
import sys
import os
import importlib
import inspect
import pkgutil
import shutil
import numpy as np

T = TypeVar("T")


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)


def rotation_mat2d(theta: float) -> np.ndarray:
    c = np.cos(theta)
    s = np.sin(theta)

    return np.array([[c, -s], [s, c]])


def recursive_load(pkg: Union[ModuleType, str]) -> List[ModuleType]:
    pkg = (
        importlib.import_module(pkg) if isinstance(pkg, str) else pkg
    )  # type: ModuleType

    loaded_modules = [pkg]  # type: List[ModuleType]

    if hasattr(pkg, "__path__"):
        for loader, name, is_pkg in pkgutil.iter_modules(pkg.__path__):
            full_name = pkg.__name__ + "." + name
            child = importlib.import_module(full_name)
            loaded_modules += recursive_load(child)

    return loaded_modules


def get_classes_in_modules(
    m: Union[Iterable[ModuleType], ModuleType], cls: T
) -> List[T]:
    clses = []  # type: List[Type]

    if isinstance(m, Iterable):
        for v in m:
            clses += get_classes_in_modules(v, cls)

        return clses

    for name in dir(m):
        attr = getattr(m, name)

        if (
            inspect.isclass(attr)
            and issubclass(attr, cls)
            and attr.__module__ == m.__name__
        ):
            clses.append(attr)

    return clses


def clamp(x: float, lower: float, upper: float) -> float:
    """Return `lower` if `x < lower`,
    `upper` if `x > upper` and
    `x`     if `lower < x < upper`
    """
    return max(min(x, upper), lower)


def clear_directory_contents(path: Path) -> None:
    if not path.is_dir():
        return

    for child_path in path.iterdir():
        if child_path.is_file():
            child_path.unlink()
        elif child_path.is_dir():
            shutil.rmtree(str(child_path))
