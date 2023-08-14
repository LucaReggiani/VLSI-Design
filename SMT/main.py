import time
from utils import *
from instance import Instance
import numpy as np
from tqdm import tqdm
from z3 import *
'''
terminal args
'''
folder_name = './input/'
rotation = True
simmetry_breaking = True

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

    # Declaration of the integer bottom-left corner of each circuit
    # Dictionary of tuples:
    #   -) the key is the circuit's index
    #   -) the value is a tuple:
    #     -) first element --> integer variable, x coordinate
    #     -) second element --> integer variable, y coordinate

    corners = {f: (Int(f"circuit_{f}_X"), Int(f"circuit_{f}_Y")) for f in range(instance.get_n_circuits())}
    
    lr = [[Bool(f"lr_{h+1}_{j+1}") if h != j else 0 for j in range(instance.get_n_circuits())] for h in range(instance.get_n_circuits())]
    ud = [[Bool(f"ud_{h+1}_{j+1}") if h != j else 0 for j in range(instance.get_n_circuits())] for h in range(instance.get_n_circuits())]  

    widest_idx = np.argmax([instance.get_circuit(r)[0] * instance.get_circuit(r)[1] for r in range(instance.get_n_circuits())])

    if rotation:
        # widths and heights arrays for each circuit, defined as variables because of the change of rotation
        widths = [Int(str(f) + "_w") for f in range(instance.get_n_circuits())]
        heights = [Int(str(f) + "_h") for f in range(instance.get_n_circuits())]
        # List of boolean flags, in order to understand if a specific circuit at a certain position is rotated or not.
        rot_flags = [Bool(str(f)+"_rot") for f in range(instance.get_n_circuits())]  

    # Loop in order to iterate the range of heights
    while solution_found == False and plate_height < instance.get_max_height() +1:
        
        s = Solver()
        # 5 minutes (300 sec) time limit for each instance to be solved
        tmout = 300 * 1000
        s.set(timeout = tmout)

        # if the rotation is disabled, the list of rotation flags is set to False
        #s.add([rot_flags[c]==False for c in range(instance.get_n_circuits()) if rotation is False])

        for c in range(instance.get_n_circuits()):


            if not rotation:
                '''
                #############################################################
                first constraint: each circtuit's corner must be in the plate
                #############################################################
                '''
                # Every X coordinate of each circuit's corner must be >= 0
                s.add(corners[c][0] >= 0)
                # Every Y coordinate of each circuit's corner must be >= 0
                s.add(corners[c][1] >= 0)
                # Every X coordinate of each circuit's corner + the width of the circuit must be <= the plate width
                s.add(corners[c][0] + instance.get_circuit(c)[0] <= plate_width)
                # Every Y coordinate of each circuit's corner + the height of the circuit must be <= the plate height
                s.add(corners[c][1] + instance.get_circuit(c)[1] <= plate_height)

                if simmetry_breaking:
                    # if c is the widest index, it should be as left as possible, with a small left-slide movement
                    if c == widest_idx:
                        s.add(corners[c][0]<=(plate_width-instance.get_circuit(c)[0])//2)

                    # if the width of c is > the maximum slide allowed for the widest index 
                    # c cannot be placed on the left of the widest index
                    elif instance.get_circuit(c)[0]>(plate_width - instance.get_circuit(widest_idx)[0])//2:
                        s.add(lr[c][widest_idx] == False)
                    
                    '''if c == tallest_idx:
                        opt.add(corner_y[i]<=(ub-instance.get_c_height(i))//2)
                    elif instance.get_c_height(i)>(ub - instance.get_c_height(tallest_idx))//2:
                        opt.add(ud[i][tallest_idx] == False)'''
                    
                    '''
                    #############################################################
                    second constraint: non-overlapping constraint
                    #############################################################
                    '''

                    # Pairwise constraints
                    for j in range(c+1, instance.get_n_circuits()):

                        # Non overlapping constraints
                        s.add((corners[c][0] + instance.get_circuit(c)[0] <= corners[j][0]) == lr[c][j])
                        s.add((corners[c][1] + instance.get_circuit(c)[1] <= corners[j][1]) == ud[c][j])
                        s.add((corners[j][0] + instance.get_circuit(j)[0] <= corners[c][0]) == lr[j][c])
                        s.add((corners[j][1] + instance.get_circuit(j)[1] <= corners[c][1]) == ud[j][c])

                        s.add(Or(lr[c][j], lr[j][c], ud[c][j], ud[j][c]))

                        # Rectangle pair incompatibilities
                        if instance.get_circuit(c)[0] + instance.get_circuit(j)[0] > plate_width:
                            # horizontal constraint
                            s.add(Implies(instance.get_circuit(c)[0] + instance.get_circuit(j)[0] > plate_width, lr[c][j] == False))
                            s.add(Implies(instance.get_circuit(j)[0] + instance.get_circuit(c)[0] > plate_width, lr[j][c] == False))

                        if instance.get_circuit(c)[1] + instance.get_circuit(j)[1] > plate_height:
                            # vertical constraint
                            s.add(Implies(instance.get_circuit(c)[1] + instance.get_circuit(j)[1] > plate_height, ud[c][j] == False))
                            s.add(Implies(instance.get_circuit(j)[1] + instance.get_circuit(c)[1] > plate_height, ud[j][c] == False))
                else:
                    # Pairwise constraints
                    for j in range(c+1, instance.get_n_circuits()):

                        # Non overlapping constraints
                        s.add((corners[c][0] + instance.get_circuit(c)[0] <= corners[j][0]) == lr[c][j])
                        s.add((corners[c][1] + instance.get_circuit(c)[1] <= corners[j][1]) == ud[c][j])
                        s.add((corners[j][0] + instance.get_circuit(j)[0] <= corners[c][0]) == lr[j][c])
                        s.add((corners[j][1] + instance.get_circuit(j)[1] <= corners[c][1])== ud[j][c])

                        s.add(Or(lr[c][j], lr[j][c], ud[c][j], ud[j][c]))
            else:

                '''
                #############################################################
                first constraint: each circtuit's corner must be in the plate
                #############################################################
                '''
                # Every X coordinate of each circuit's corner must be >= 0
                s.add(corners[c][0] >= 0)
                # Every Y coordinate of each circuit's corner must be >= 0
                s.add(corners[c][1] >= 0)
                # Every X coordinate of each circuit's corner + the width of the circuit must be <= the plate width
                s.add(corners[c][0] + widths[c] <= plate_width)
                # Every Y coordinate of each circuit's corner + the height of the circuit must be <= the plate height
                s.add(corners[c][1] + heights[c] <= plate_height)

                # Widths and heights constraints
                # s.add(Or(widths[c] == instance.get_circuit(c)[1], widths[c] == instance.get_circuit(c)[0]))
                # s.add(Or(heights[i] == instance.get_circuit(c)[1], heights[i] == instance.get_circuit(c)[0]))

                # Pairwise constraints
                for j in range(c+1, instance.get_n_circuits()):

                    # Non overlapping constraints
                    s.add((corners[c][0] + widths[c] <= corners[j][0]) == lr[c][j])
                    s.add((corners[c][1] + heights[c] <= corners[j][1])== ud[c][j])
                    s.add((corners[j][0] + widths[j] <= corners[c][0]) == lr[j][c])
                    s.add((corners[j][1] + heights[j] <= corners[c][1])== ud[j][c])

                    s.add(Or(lr[c][j], lr[j][c], ud[c][j], ud[j][c]))

                    if simmetry_breaking:
                        # Rectangle pair incompatibilities
                        s.add(Implies(widths[c] + widths[j] > plate_width, lr[c][j] == False))
                        s.add(Implies(widths[j] + widths[c] > plate_width, lr[j][c] == False))

                        s.add(Implies(heights[c] + heights[j] > plate_height, ud[c][j] == False))
                        s.add(Implies(heights[j] + heights[c] > plate_height, ud[j][c] == False))

                # Rotation constraints
                s.add(If(rot_flags[c], widths[c] == instance.get_circuit(c)[1], widths[c] == instance.get_circuit(c)[0]))
                s.add(If(rot_flags[c], heights[c] == instance.get_circuit(c)[0], heights[c] == instance.get_circuit(c)[1]))

        result = s.check()
        
        # check if the solving time is higher than 300 seconds
        if result == unknown:
            break

        # Check if the solution exists
        elif result == sat:
            m = s.model()
            sol =  [[int(m.evaluate(corners[h][j]).as_string()) for j in range(2)] for h in range(instance.get_n_circuits())]

            # Save solution
            start_x = []
            start_y = []
            for j in range(len(sol)):
                start_x.append(int(sol[j][0]))
                start_y.append(int(sol[j][1]))

            if rotation:
                circuits = [[widths[h], heights[h], start_x[h], start_y[h]] for h in range(instance.get_n_circuits())]
            else:
                circuits = [[instance.get_circuit(h)[0], instance.get_circuit(h)[1], start_x[h], start_y[h]] for h in range(instance.get_n_circuits())]
            plot_solution(plate_width, plate_height, circuits, m, rotation, output_img_path+f'out-{i + 1}.png')
            output_solution(circuits, plate_width, plate_height, rotation, m, output_txt_path+f'out-{i + 1}.txt')
            solution_found = True
            end_time = time.time()
            print(f"Solution found for instance {i + 1}")
            print(f"optimum height is: {instance.get_min_height()}")
            print(f"minimum height found is: {plate_height}")
            print(f"The time requested for this instance was: {end_time - start_time}")
            print("\n\n\n\n\n")
        
        else:
        # if here, it means that the time is not expired and it doesn't exist a solution that satisfies the constraint
            plate_height += 1

    if(not solution_found):
        # write the instance in failures file
        with open(output_failure_path, 'a') as output:
            output.write(f'Instance {i + 1} failed')
            output.write('\n')
        print("\nFailed to solve instance %i" % (i + 1))