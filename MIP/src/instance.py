import math
from typing import List, Tuple

# Custom sorting function based on the product of each pair
def sorting_key(pair):
    return pair[0] * pair[1]

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

        circuits = [(int(width), int(height)) for value in values for width, height in [value.rstrip().split(' ')]]
        self._circuits = sorted(circuits, key=sorting_key, reverse=True)

        # Getting instance name
        self._name = name_instance
        
        self._rotation = rotation

        self._simmetry_breaking = simmetry_breaking
        
        self._min_height = 0
        self._max_height = 0
        for circuit in self._circuits:
            self._min_height += circuit[0] * circuit[1]
            self._max_height += circuit[1]
        self._min_height = int(math.ceil(self._min_height / self._plate_width))

        # Circuit width and height
        if rotation:
            self._widths = [self._circuits[index][0] for index in range(len(self._circuits))]
            self._heights = [self._circuits[index][1] for index in range(len(self._circuits))]
        else:
            self._widths = [self._circuits[index][0] for index in range(len(self._circuits))]
            self._heights = [self._circuits[index][1] for index in range(len(self._circuits))]

    
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