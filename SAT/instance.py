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

    def __init__(self, raw_instance, name_instance, rotation=False, simmetry_breaking=True):
        
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

        self._simmetry_breaking = simmetry_breaking


        # list of booleans. If True, the circuit that is looping can be placed at that specific x-position, False otherwise
        self._x_positions = [[Bool(f"px_{circuit_index+1}_{w}") for w in range(self._plate_width)] for circuit_index in range(self.get_n_circuits())]
        
        # list of booleans. If True, the circuit that is looping can be placed at that specific y-position, False otherwise
        self._y_positions = [[Bool(f"py_{circuit_index+1}_{h}") for h in range(self._min_height)] for circuit_index in range(self.get_n_circuits())]

        # List of boolean flags, in order to understand if a specific circuit at a certain position is rotated or not.
        self._rot_flags = [Bool(str(circuit_index)+"_rotation") for circuit_index in range(self.get_n_circuits())]

        # list of booleans. If True, the circuit at index 1 is placed at the left of the circuit at index 2. False otherwise.
        self.lr = [[Bool(f"LeftRight_{circuit_index_1+1}_{circuit_index_2+1}") if circuit_index_1 != circuit_index_2 else 0 for circuit_index_2 in range(self.get_n_circuits())] for circuit_index_1 in range(self.get_n_circuits())]
        # list of booleans. If True, the circuit at index 1 is placed at the bottom of the circuit at index 2. False otherwise
        self.ud = [[Bool(f"DownUp_{circuit_index_1+1}_{circuit_index_2+1}") if circuit_index_1 != circuit_index_2 else 0 for circuit_index_2 in range(self.get_n_circuits())] for circuit_index_1 in range(self.get_n_circuits())]


    def set_y_positions(self, height):

        self._min_height += 1

        # list of booleans. If True, the circuit that is looping can be placed at that specific y-position, False otherwise
        self._y_positions = [[Bool(f"py_{circuit_index+1}_{h}") for h in range(self._min_height)] for circuit_index in range(self.get_n_circuits())]

    def get_plate_width(self):
        '''
        Returning the instance width
        '''
        return self._plate_width
    
    def get_n_circuits(self):
        '''
        Returning the number of circuits
        '''
        return self._n_circuits
    
    def get_circuit(self, index):
        '''
        Returning a circuit by index
        '''
        return self._circuits[index]
    
    def get_min_height(self):
        '''
        Returning the minimum height
        '''
        return self._min_height
    
    def get_max_height(self):
        '''
        Returning the maximum height
        '''
        return self._max_height

    def get_name(self):
        '''
        Returning the instance name
        '''
        return self._name
    
    ####################################
    # Get Rotation / Simmetry_Breaking #
    ####################################
    def get_rotation(self):
        '''
        Returning rotation
        '''
        return self._rotation

    def get_simmetry_breaking(self):
        '''
        Returning simmetry breaking
        '''
        return self._simmetry_breaking

    ##################################
    ###### Get/Set x/y-positions #####
    ##################################

    # Get
    def get_x_positions(self):
        '''
        Returning x-positions
        '''
        return self._x_positions
    
    def get_y_positions(self):
        '''
        Returning y-positions
        '''
        return self._y_positions
    
    def get_rotation_flags(self):
        '''
        Returning rotation flags
        '''
        return self._rot_flags