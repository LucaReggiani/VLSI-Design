import os
from datetime import timedelta
import time
from minizinc import Solver, Instance, Model
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt

path_init = "./instances/txt/"
model_name = "./cp_rot_sb.mzn"
output_txt_path = "./results_rot/txt/rot_sb/"
output_img_path = "./results_rot/img/rot_sb/"
solvers = ["chuffed", "gecode"]
rotation = 1

def plot_solution(width, height, circuits, rotation, file=None):
    SIZE = 10
    fig, ax = plt.subplots()

    fig.set_size_inches(SIZE, SIZE * height / width)
    colors = ['tab:red','tab:orange', 'yellow', 'tab:green','tab:blue','tab:purple','tab:brown', 'tab:grey']
    for j in range(len(circuits)):
        
        if rotation:
            i_width = circuits[j][0] if circuits[j][4] == 0  else circuits[j][1]
            i_height = circuits[j][1] if circuits[j][4] == 0  else circuits[j][0]
        
        else:
            i_width = circuits[j][0]
            i_height = circuits[j][1]
        
        i_x_coordinate = circuits[j][2]
        i_y_coordinate = circuits[j][3]
        ax.broken_barh([(i_x_coordinate, i_width)], (i_y_coordinate, i_height),
                        facecolors=colors[j % len(colors)],
                        edgecolors=("black"),
                        linewidths=(2,),)
    ax.set_ylim(0,height)
    ax.set_xlim(0, width)
    ax.set_xticks(range(width + 1))
    ax.set_yticks(range(height + 1))
    ax.grid(color='b', linewidth = 1)

    if file is not None:
        plt.savefig(file)
        plt.close()
    else:
        plt.show()

def run_solver():
    
    for i in tqdm(range(1, 41)):  
        
        input_file = path_init + 'ins-' + str(i) + '.txt'
        
        file1 = open(input_file, 'r')
        
        lines = file1.readlines()
    
        w = int(lines[0])
        n = int(lines[1])
    
        x = []
        y = []
    
        for j in range(n):
            shape = lines[j + 2].split(' ')
            x.append(int(shape[0]))
            y.append(int(shape[1]))
            
        model = Model(model_name)
        solver = Solver.lookup(solvers[0])
        inst = Instance(solver, model)
        inst["w"] = w
        inst["n"] = n
        inst["widths"] = np.array(x)
        inst["heights"] = np.array(y)
    
        out_file = os.path.join(output_txt_path, f'ins-{i}-out.txt')
    
        print(f'Solving instance {i}')  
    
        start_time = time.time()
        out = inst.solve(timeout=timedelta(seconds=300), processes = 8, free_search=True) 
        run_time = time.time() - start_time
            
        h = out['objective']
        print(f'h = {h}, runtime = {run_time * 1000:.1f} ms')
        
        with open(out_file, 'w') as out_file:
            #print(f'{out_file}:', end='\n', flush=True)
            print(f'{run_time * 1000:.1f} ms')
            #out_file.write(f'{run_time}')
            out_file.write(f'{w} {h}\n{n}\n')
            for k in range(n):
                out_file.write(f"{x[k]} {y[k]} {out['X'][k]} {out['Y'][k]}\n")
        #circuits = [[x[h],y[h],out['X'][h],out['Y'][h]] for h in range(n)]
        circuits_rot = [[x[h],y[h],out['X'][h],out['Y'][h], out['rotate'][h]] for h in range(n)]
        plot_solution(w, h, circuits_rot, rotation, output_img_path+f'out-{i}.png')
        
            
run_solver()
