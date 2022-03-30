"""Trackmania.io API Wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~

A wrapper for Trackmania.io api service.

:copyright: (c) 2022-present Deepesh Nimma.
:license: MIT, see LICENSE for more details.
"""
import asyncio
import os
import logging

from .api import *
from .config import *
from .constants import *
from .errors import *
from .structures.ad import *
from .structures.cotd import *
from .structures.map import *
from .structures.medal_times import *
from .structures.player import *

__title__ = "py-tmio"
__author__ = "Deepesh Nimma"
__license__ = "MIT"
__copyright__ = "Copyright 2022-present Deepesh Nimma"
__version__ = "0.3.1"

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.getLogger(__name__).addHandler(logging.NullHandler())
