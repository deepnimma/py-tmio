"""
Trackmania.io API Wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~

A wrapper for Trackmania.io api service.

:copyright: (c) 2022-present Deepesh Nimma.
:license: MIT, see LICENSE for more details.
"""
import asyncio
import logging
import os

from .ad import *
from .config import *
from .cotd import *
from .errors import *
from .matchmaking import *
from .player import *
from .tmmap import *
from .tmx import *
from .totd import *
from .trophy import *

__title__ = "py-tmio"
__author__ = "Deepesh Nimma"
__license__ = "MIT"
__copyright__ = "Copyright 2022-present Deepesh Nimma"
__version__ = "v0.4.0"

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.getLogger(__name__).addHandler(logging.NullHandler())
