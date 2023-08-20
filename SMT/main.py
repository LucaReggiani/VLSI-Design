import argparse
from tqdm import tqdm
import time
from instance import Instance
from z3 import *
from constraints import set_domain_constraints, set_non_overlap_constraints, check_rot_flags, rotation_switch
from utils import *


def solve_instance(instance, solver, plate_height):

    if rotation:
        check_rot_flags(instance, solver, plate_height)
        rotation_switch(instance, solver, plate_height)

    set_domain_constraints(instance, solver, plate_height)
    set_non_overlap_constraints(instance, solver, plate_height)

    result = solver.check()

    # check if the solving time is higher than 300 seconds
    if result == unknown:
        return "Time Expired"
    
    # Check if the solution exists
    elif result == sat:
        model = s.model()
        return model, plate_height
    else:
        plate_height += 1
        if plate_height < instance.get_max_height():
            return solve_instance(instance, solver, plate_height)
        else:
            return "Maximum Height exceeded"



if __name__ == '__main__':

    # Create an argument parser
    parser = argparse.ArgumentParser(description='SAT argument parsing')

    # Add arguments
    parser.add_argument('--folder_name', type=str, default='./input/', help='Input instance folder name')
    parser.add_argument('--rotation', action='store_true', help='Set circuit rotation to True')
    parser.add_argument('--simmetry_breaking', action='store_true', help='Set solving simmetry breaking to True')
    args = parser.parse_args()

    folder_name = args.folder_name
    rotation = args.rotation
    simmetry_breaking = args.simmetry_breaking
    output_txt_path, output_img_path, output_failure_path = set_environment(rotation, simmetry_breaking, 'SMT')
    
    instances = import_instances(folder_name)

    # list of all timing measures for each instance
    timings = []

    for i in tqdm(range(len(instances))):
    
        name_instance = f'{i}_instance'
        instance = Instance(instances[i], name_instance, rotation, simmetry_breaking)

        plate_height = instance.get_min_height()
        
        plate_width = instance.get_plate_width()

        # starting timing operation
        start_time = time.time()

        # Solver initialization
        s = Solver()
        # 5 minutes (300 sec) time limit for each instance to be solved
        tmout = 300 * 1000
        s.set(timeout = tmout)
        
        output = solve_instance(instance, s, plate_height)

        if type(output) == str:

            end_time = time.time()
            timings.append('-')

            # write the instance in failures file
            with open(output_failure_path, 'a') as output:
                output.write(f'Instance {i + 1} failed')
                output.write('\n')
            print("\nFailed to solve instance %i" % (i + 1))

        else:

            m = output[0]
            height = output[1]

            decode_circuits(instance, m, height, output_txt_path, output_img_path)

            end_time = time.time()

            timings.append(end_time - start_time)

            print(f"Solution found for instance {i + 1}")
            print(f"optimum height is: {instance.get_min_height()}")
            print(f"minimum height found is: {height}")
            print(f"The time requested for this instance was: {end_time - start_time}")
            print("\n\n\n\n\n")

    # Saving time needed to solve the instances into 'timing.csv' file
    save_times_to_csv(rotation, simmetry_breaking, timings, len(instances))
