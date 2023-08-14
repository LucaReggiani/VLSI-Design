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
rotation = False
simmetry_breaking = False

if rotation:

    if simmetry_breaking:
        subfolder = '/simmetry_breaking/'
    else:
        subfolder = '/no_simmetry_breaking/'

    output_txt_path = './SAT/outputRot/txt' + subfolder
    output_img_path = './SAT/outputRot/img' + subfolder
    output_failure_path = './SAT/outputRot/failures.txt'
    # output_timings_path = './outputRot/timings.csv'

else:

    if simmetry_breaking:
        subfolder = '/simmetry_breaking/'
    else:
        subfolder = '/no_simmetry_breaking/'
    output_txt_path = './SAT/output/txt' + subfolder
    output_img_path = './SAT/output/img' + subfolder
    output_failure_path = './SAT/output/failures.txt'


# write the heading in failures file
with open(output_failure_path, 'a') as output:
    output.write(f'\nSYMMETRY BREAKING: {simmetry_breaking}\n')

instances = import_instances(folder_name)


def add_non_overlapping_constraint(instance, c, j, s, to_add = [True, True, True, True]):
    # non-overlapping constraint
    literals_4l = []
    if to_add[0]:
        literals_4l.append(lr[c][j])
        add_3l_clause(instance, lr, x_positions, c, j, 'x', plate_height)
    if to_add[1]:
        literals_4l.append(lr[j][c])
        add_3l_clause(instance, lr, x_positions, j, c, 'x', plate_height)
    if to_add[2]:
        literals_4l.append(ud[c][j])
        add_3l_clause(instance, ud, y_positions, c, j, 'y', plate_height)
    if to_add[3]:
        literals_4l.append(ud[j][c])
        add_3l_clause(instance, ud, y_positions, j, c, 'y', plate_height)

    s.add(Or(literals_4l))

def add_3l_clause(instance, lrud, pxy, index_1, index_2, direction, plate_height):
        """
        Add the normal 3-literal clause.
        I.e.
        - For the x-coordinate:
            ~lr[i][j] \/ px[i][e] \/ ~px[j][e + w_i].

        - For the y-coordinate:
            ~ud[i][j] \/ py[i][f] \/ ~py[j][f + h_i].

        Parameters
        ----------
        s : z3.Solver
            solver on which to add the clauses
        direction : string
            either 'x' or 'y'.
        index_1 : int
            index of the first rectangle.
        index_2 : int
            index of the second rectangle.
        """
        if direction == 'x':
            rectangle_measure = instance.get_circuit(index_1)[0]
            strip_measure = instance.get_plate_width()
        elif direction == 'y':
            rectangle_measure = instance.get_circuit(index_1)[1]
            strip_measure = plate_height
        else:
            print("The direction must be either 'x' or 'y'")
            return

        #if rectangle 1 is left of rectangle 2, rectangle 2 cannot be at the left of the right edge of rectangle 1.
        for k in range(rectangle_measure):
            try:
                s.add(Or(Not(lrud[index_1][index_2]), Not(pxy[index_2][k])))
            except:
                pass

        for k in range(strip_measure - rectangle_measure):
            k1 = k + rectangle_measure
            s.add(Or(Not(lrud[index_1][index_2]), pxy[index_1][k], Not(pxy[index_2][k1])))
            

def order_decode(encoding, vmin=0):
        """
        Parameters
        ----------
        encoding : list of bool
            order encoded value in the form [False, ..., False, True, True, ...]
        vmin : int, default 0
            starting value of the domain of the encoded value

        Returns
        -------
        int
            the decoded value
        """
        for i, val in enumerate(encoding):
            if val:
                return i + vmin
        return len(encoding) + vmin

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

        # y_positions = [[Bool(f"py_{i+1}_{f}") for f in range(plate_height)] for i in range(instance.get_n_circuits())]

        s = Solver()
        # 5 minutes (300 sec) time limit for each instance to be solved
        tmout = 300 * 1000
        s.set(timeout = tmout)

        # Domain constraints
        for cir in range(instance.get_n_circuits()):
            for e in range(plate_width - instance.get_circuit(cir)[0], plate_width):
                s.add(x_positions[cir][e])
            
            for f in range(plate_height - instance.get_circuit(cir)[1], plate_height):
                s.add(y_positions[cir][f])
            
        if simmetry_breaking:
            widest_idx = np.argmax([instance.get_circuit(r)[0] * instance.get_circuit(r)[1] for r in range(instance.get_n_circuits())])
            for e in range((plate_width - instance.get_circuit(widest_idx)[0]) // 2, plate_width - instance.get_circuit(widest_idx)[0]):
                s.add(x_positions[widest_idx][e])
            
            for f in range((plate_height - instance.get_circuit(widest_idx)[1]) // 2, plate_height - instance.get_circuit(widest_idx)[1]):
                s.add(y_positions[widest_idx][f])
            
            '''
            # ordering constraint
            # Da Controllare
            for cir in range(instance.get_n_circuits()):
                for e in range(plate_width - instance.get_circuit(cir)[0] - 1):
                    s.add(Implies(x_positions[cir][e], x_positions[cir][e + 1]))
            '''
            '''
            for f in range(self.H - self.rectangles[i].h - 1):
                s.add(Implies(self._py[i][f], self._py[i][f + 1]))
            '''
        # non-overlap constraints
        if simmetry_breaking:
            widest_idx = np.argmax([instance.get_circuit(r)[0] * instance.get_circuit(r)[1] for r in range(instance.get_n_circuits())])
            for c in range(instance.get_n_circuits()):
                for j in range(c+1, instance.get_n_circuits()):
                    # LS: Reducing the domain for the largest rectangle
                    if j == widest_idx:
                        large_width = instance.get_circuit(c)[0] > (plate_width - instance.get_circuit(widest_idx)[0])//2
                        large_height = instance.get_circuit(c)[1] > (plate_height - instance.get_circuit(widest_idx)[1])//2
                        if large_width and large_height:
                            add_non_overlapping_constraint(instance, c, j, s, to_add=[False, True, False, True])
                        elif large_width:
                            add_non_overlapping_constraint(instance, c, j, s, to_add=[False, True, True, True])
                        elif large_height:
                            add_non_overlapping_constraint(instance, c, j, s, to_add=[True, True, False, True])
                        else:
                            add_non_overlapping_constraint(instance, c, j, s)

                    # SR: Breaking symmetries for same-sized rectangles
                    elif instance.get_circuit(c)[0] == instance.get_circuit(j)[0] and instance.get_circuit(c)[1] == instance.get_circuit(j)[1]:
                        add_non_overlapping_constraint(instance, c, j, s, to_add=[True, False, True, False])
                        # s.add(Or(Not(ud[c][j], lr[j][c])))

                    # LR (horizontal)
                    elif instance.get_circuit(c)[0] + instance.get_circuit(j)[0] > plate_width:
                        add_non_overlapping_constraint(instance, c, j, s, to_add=[False, False, True, True])
                    # LR (vertical)
                    elif instance.get_circuit(c)[1] + instance.get_circuit(j)[1] > plate_height:
                        add_non_overlapping_constraint(instance, c, j, s, to_add=[True, True, False, False])
                    else:
                        add_non_overlapping_constraint(instance, c, j, s)
        else:
            for c in range(instance.get_n_circuits()):
                for j in range(c+1, instance.get_n_circuits()):
                    add_non_overlapping_constraint(instance, c, j, s)


        result = s.check()
        
        # check if the solving time is higher than 300 seconds
        if result == unknown:
            break
        # Check if the solution exists
        elif result == sat:
            m = s.model()

            px_eval = [[m.evaluate(x_positions[c][j], model_completion = True) for j in range(len(x_positions[c]))] for c in range(len(x_positions))]
            x_values = [order_decode(p) for p in px_eval]
            py_eval = [[m.evaluate(y_positions[c][j], model_completion = True) for j in range(len(y_positions[c]))] for c in range(len(y_positions))]
            y_values = [order_decode(p) for p in py_eval]

            circuits = [[instance.get_circuit(h)[0], instance.get_circuit(h)[1], x_values[h], y_values[h]] for h in range(instance.get_n_circuits())]
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
