import re
import math
import random


class Building:
    """Pods."""

    def __init__(self, name):
        self.name = name
        self.floors = {}
        self.color = "greygreen"

    @property
    def size(self):
        return len(self.floors)
