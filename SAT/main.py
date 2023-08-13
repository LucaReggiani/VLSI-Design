import time
from utils import *
from instance import Instance
import numpy as np
from tqdm import tqdm
'''
terminal args
'''
folder_name = './input/'
rotation = False
simmetry_breaking = False

if rotation:

    if simmetry_breaking:
        subfolder = '/simmetry_breaking/'
    else:
        subfolder = '/no_simmetry_breaking/'

    output_txt_path = './outputRot/txt' + subfolder
    output_img_path = './outputRot/img' + subfolder
    output_failure_path = './outputRot/failures.txt'
    # output_timings_path = './outputRot/timings.csv'

else:

    if simmetry_breaking:
        subfolder = '/simmetry_breaking/'
    else:
        subfolder = '/no_simmetry_breaking/'
    output_txt_path = './output/txt' + subfolder
    output_img_path = './output/img' + subfolder
    output_failure_path = './output/failures.txt'


# write the heading in failures file
with open(output_failure_path, 'a') as output:
    output.write(f'\nSYMMETRY BREAKING: {simmetry_breaking}\n')

instances = import_instances(folder_name)

for i in tqdm(range(len(instances))):
    name_instance = f'{i}_instance'
    instance = Instance(instances[i], name_instance, rotation)

    solution_found = False
    plate_height = instance.get_min_height()
    
    plate_width = instance.get_plate_width()

    # starting timing operation
    start_time = time.time()
    
    x_positions = [[Bool(f"px_{i+1}_{e}") for e in range(plate_width)] for i in range(instance.get_n_circuits())]
    y_positions = [[Bool(f"py_{i+1}_{f}") for f in range(plate_height)] for i in range(instance.get_n_circuits())]

    lr = [[Bool(f"lr_{h+1}_{j+1}") if h != j else 0 for j in range(instance.get_n_circuits())] for h in range(instance.get_n_circuits())]
    ud = [[Bool(f"ud_{h+1}_{j+1}") if h != j else 0 for j in range(instance.get_n_circuits())] for h in range(instance.get_n_circuits())]

    # Loop in order to iterate the range of heights
    while solution_found == False and plate_height < instance.get_max_height() +1:
        
        s = Solver()

        # Domain constraints
        for i in range(instance.get_n_circuits()):
            for e in range(plate_width - instance.get_circuit(i)[0], plate_width):
                s.add(x_positions[i][e])
            '''
            for f in range(self.H - self.rectangles[i].h, self.H):
                self.s.add(self._py[i][f])
            '''
        if simmetry_breaking:
            widest_idx = np.argmax([instance.get_circuit(r)[0] * instance.get_circuit(r)[1] for r in range(instance.get_n_circuits())])
            for e in range((plate_width - instance.get_circuit(widest_idx)[0]) // 2, plate_width - instance.get_circuit(widest_idx)[0]):
                s.add(x_positions[widest_idx][e])
            '''
            for f in range((self.H - self.rectangles[m].h) // 2, self.H - self.rectangles[m].h):
                self.s.add(self._py[m][f])
            '''
        
        # ordering constraint
        # Da Controllare
        for i in range(instance.get_n_circuits()):
            for e in range(plate_width - instance.get_circuit(i)[0] - 1):
                s.add(Implies(x_positions[i][e], x_positions[i][e + 1]))
            
            '''
            for f in range(self.H - self.rectangles[i].h - 1):
                s.add(Implies(self._py[i][f], self._py[i][f + 1]))
            '''