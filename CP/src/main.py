from datetime import timedelta
import time
from minizinc import Solver, Instance, Model
from instance import Instance as ins
import numpy as np
from tqdm import tqdm
from utils import *
import argparse

solvers = ["chuffed", "gecode"]

if __name__ == '__main__':
    # Create an argument parser
    parser = argparse.ArgumentParser(description='CP argument parsing')

    # Add arguments
    parser.add_argument('--folder_name', type=str, default='./input/', help='Input instance folder name')
    parser.add_argument('--rotation', action='store_true', help='Set circuit rotation to True')
    parser.add_argument('--simmetry_breaking', action='store_true', help='Set solving simmetry breaking to True')
    args = parser.parse_args()
    
    folder_name = args.folder_name
    rotation = args.rotation
    simmetry_breaking = args.simmetry_breaking
    output_txt_path, output_img_path, output_failure_path, model_name = set_environment(rotation, simmetry_breaking)
    
    instances = import_instances(folder_name)

    for i in tqdm(range(len(instances))):
        name_instance = f'{i}_instance'
        instance = ins(instances[i], name_instance, rotation, simmetry_breaking)
                
        model = Model(model_name)
        solver = Solver.lookup(solvers[0])
        inst = Instance(solver, model)
        inst["w"] = instance.get_plate_width()
        inst["n"] = instance.get_n_circuits()
        inst["widths"] = np.array(instance.get_circuit_widths())
        inst["heights"] = np.array(instance.get_circuit_heights())
            
        # starting timing operation
        start_time = time.time()
        out = inst.solve(timeout=timedelta(seconds=300), free_search=True) 
        run_time = time.time() - start_time
        
        height = out['objective']
        
        if rotation:
            circuits = [[instance.get_circuit_widths()[h],instance.get_circuit_heights()[h],out['X'][h],out['Y'][h], out['rotate'][h]] for h in range(instance.get_n_circuits())]
        else:
            circuits = [[instance.get_circuit_widths()[h],instance.get_circuit_heights()[h],out['X'][h],out['Y'][h]] for h in range(instance.get_n_circuits())]
        decode_circuits(instance, height, output_txt_path, output_img_path, circuits)
        print(f"\nSolution found for instance {i + 1}")
        print(f"optimum height is: {instance.get_min_height()}")
        print(f"minimum height found is: {height}")
        print(f"The time requested for this instance was: {run_time}")
        save_times_to_csv(rotation, simmetry_breaking, run_time, i)
        