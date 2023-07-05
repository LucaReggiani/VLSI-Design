import math
from pathlib import Path
from typing import List, Tuple
from z3 import *

class Instance():

    _plate_width: int
    _n_circuits : int
    _circuits : List[Tuple[int, int]]
    _min_height: int
    _max_height: int
    _name : str
    _rotation: bool

    def __init__(self, raw_instance, name_instance, rotation=False):
        
        # getting the width of the silicon plate
        self._plate_width = int(raw_instance[0])

        # getting the number of circuits to place inside the plate
        self._n_circuits = int(raw_instance[1])

        # Getting circuits width and height
        values = raw_instance[2:]
        circuits = [(int(width), int(height)) for value in values for width, height in [value.split(' ')]]
        self._circuits = sorted(circuits, reverse=True)

        # Getting instance name
        self._name = name_instance

        # Getting circuits min height and max height
        self._min_height = 0
        self._max_height = 0
        # min and max height computation
        for circuit in self._circuits:
            self._min_height += circuit[0] * circuit[1]
            self._max_height += circuit[1]
        
        self._min_height = int(math.ceil(self._min_height / self._plate_width))

        self._rotation = rotation

        self._corners = {}

        # widths and heights lists initialization
        self._widths = []
        self._heights = []

        # List of rotation flags: If True, the circuit is rotated, 
        # if False, it is not rotated
        self._rotation_flags = []

    
    def get_plate_width(self):
        return self._plate_width
    
    def get_n_circuits(self):
        return self._n_circuits
    
    def get_circuit(self, index):
        return self._circuits[index]
    
    def get_min_height(self):
        return self._min_height
    
    def get_max_height(self):
        return self._max_height

    def get_name(self):
        return self._name