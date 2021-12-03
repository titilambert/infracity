import re
import math
import random

from kubernetes import client, config
from rectpack import newPacker, PackingMode
import rectpack.maxrects as maxrects


class Floor:
    """Container."""
    
    def __init__(self, name, ready, state):
        self.name = name
        self.state = state
        self.ready = ready
