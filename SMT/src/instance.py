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


        # Declaration of the integer bottom-left corner of each circuit
        # Dictionary of tuples:
        #   -) the key is the circuit's index
        #   -) the value is a tuple:
        #     -) first element --> integer variable, x coordinate
        #     -) second element --> integer variable, y coordinate
        self._corners = {circuit_index: (Int(f"circuit_{circuit_index}_X"), Int(f"circuit_{circuit_index}_Y")) for circuit_index in range(self.get_n_circuits())}

        # Circuit width and height
        if rotation:
            # If rotation is enabled, widths and height must be declared as encoded variables, because they can change depending on the constraints
            self._widths = [Int(str(f) + "_w") for f in range(self.get_n_circuits())]
            self._heights = [Int(str(f) + "_h") for f in range(self.get_n_circuits())]
        else:
            # If rotation is disabled, widths and heights are defined by the input file, so it is not needed to rotate them
            self._widths = [self._circuits[index][0] for index in range(len(self._circuits))]
            self._heights = [self._circuits[index][1] for index in range(len(self._circuits))]

        # List of boolean flags, in order to understand if a specific circuit at a certain position is rotated or not.
        self._rot_flags = [Bool(str(circuit_index)+"_rotation") for circuit_index in range(self.get_n_circuits())]

        # list of booleans. If True, the circuit at index 1 is placed at the left of the circuit at index 2. False otherwise.
        self.lr = [[Bool(f"LeftRight_{circuit_index_1+1}_{circuit_index_2+1}") if circuit_index_1 != circuit_index_2 else 0 for circuit_index_2 in range(self.get_n_circuits())] for circuit_index_1 in range(self.get_n_circuits())]
        # list of booleans. If True, the circuit at index 1 is placed at the bottom of the circuit at index 2. False otherwise
        self.ud = [[Bool(f"DownUp_{circuit_index_1+1}_{circuit_index_2+1}") if circuit_index_1 != circuit_index_2 else 0 for circuit_index_2 in range(self.get_n_circuits())] for circuit_index_1 in range(self.get_n_circuits())]

        # Solution height
        self._height = Int("height")
    
    def get_name(self):
        '''
        Returning the instance name
        '''
        return self._name
    
    ###################################
    ##### Get circuits information ####
    ###################################
    
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
    
    ###################################
    ##### Get plate information ####
    ###################################

    def get_plate_width(self):
        '''
        Returning the instance width
        '''
        return self._plate_width
    
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
    ###### Get Encoded Variables #####
    ##################################

    def get_corners(self):
        '''
        Returning corners
        '''
        return self._corners
    
    def get_rotation_flags(self):
        '''
        Returning rotation flags
        '''
        return self._rot_flags
    

    def get_circuit_widths(self):
        '''
        Get Circuit Widths
        '''
        return self._widths
    
    def get_circuit_heights(self):
        '''
        Get Circuit Width
        '''
        return self._heights
    
    ##################################
    ########### Get Height ###########
    ##################################
    def get_height(self):
        '''
        Get Plate Height
        '''
        return self._height
