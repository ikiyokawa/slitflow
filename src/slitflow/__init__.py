RANDOM_SEED = 42
MATPLOTLIB_BACKEND = "Agg"
__version__ = "0.1.4"

from . import data
from . import info
from . import setreqs
from . import setindex
from . import trj
from . import loc
from . import fig
from . import img
from . import tbl
from . import load
from . import manager
from . import name
from . import fun
from . import user

__all__ = ["data", "info", "trj", "loc", "fig", "create", "img", "tbl",
           "setreqs", "load", "setindex", "manager", "name", "fun", "user"]
