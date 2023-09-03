import gurobipy as gp
from gurobipy import GRB, quicksum
import time
from utils import *
from tqdm import tqdm
import argparse
from instance import Instance as ins
        
if __name__ == '__main__':
    # Create an argument parser
    parser = argparse.ArgumentParser(description='MIP argument parsing')

    # Add arguments
    parser.add_argument('--folder_name', type=str, default='./input/', help='Input instance folder name')
    parser.add_argument('--rotation', action='store_true', help='Set circuit rotation to True')
    parser.add_argument('--simmetry_breaking', action='store_true', help='Set solving simmetry breaking to True')
    args = parser.parse_args()
    
    folder_name = args.folder_name
    rotation = args.rotation
    simmetry_breaking = args.simmetry_breaking
    output_txt_path, output_img_path, output_failure_path = set_environment(rotation, simmetry_breaking)
    
    instances = import_instances(folder_name)

    for i in tqdm(range(len(instances))):
        name_instance = f'{i}_instance'
        instance = ins(instances[i], name_instance, rotation, simmetry_breaking)
        n = instance.get_n_circuits()
        w = instance.get_plate_width()
        x = instance.get_circuit_widths()
        y = instance.get_circuit_heights()
        
        m = gp.Model()
        m.Params.TimeLimit = 5*60
        m.Params.LogToConsole = 0
        h = m.addVar(lb=instance.get_min_height(),ub=instance.get_max_height(),vtype=GRB.INTEGER, name='h')
        X = m.addVars(n, lb=0,ub=w-min(x),vtype=GRB.INTEGER ,name='X')
        Y = m.addVars(n, lb=0,ub=instance.get_max_height()-min(y),vtype=GRB.INTEGER, name='Y')
        b = m.addVars(n, n, 4, vtype = GRB.BINARY, name = 'b')
        m.setObjective(h, GRB.MINIMIZE)
        
        if simmetry_breaking:
            m.addConstr(X[0] == 0, 'biggest_circuit_0_width_constr')
            m.addConstr(Y[0] == 0, 'biggest_circuit_0_height_constr')
        
        m.addConstrs(((X[i] + x[i] <= w) for i in range(n)), "max_width_constr")
        m.addConstrs(((Y[i] + y[i] <= h) for i in range(n)), "max_height_constr")
        
        M1=w
        M2=instance.get_max_height()
        m.addConstrs(((X[i] + x[i] <= X[j]+M1*b[i,j,0]) for i in range(n) for j in range(i+1, n)), "hor1_constr")
        m.addConstrs(((X[j] + x[j] <= X[i]+M1*b[i,j,1]) for i in range(n) for j in range(i+1, n)), "hor2_constr")
        m.addConstrs(((Y[i] + y[i] <= Y[j]+M2*b[i,j,2]) for i in range(n) for j in range(i+1, n)), "ver1_constr")  
        m.addConstrs(((Y[j] + y[j] <= Y[i]+M2*b[i,j,3]) for i in range(n) for j in range(i+1, n)), "ver2_constr")
        m.addConstrs((quicksum(b[i,j,k] for k in range(4)) <= 3 for i in range(n) for j in range(i+1,n)),"b_constr")
                
        start_time = time.time()
        m.optimize()
        run_time = time.time() - start_time
            
        try:
            height = int(m.ObjVal)
        except:
            with open(output_failure_path, 'a') as output:
                output.write(f'Instance {i + 1} failed')
                output.write('\n')
            print("\nFailed to solve instance %i" % (i + 1))
            save_times_to_csv(rotation, simmetry_breaking, '-', i)
            continue

        X = []
        Y = []
        for j in range(n):
            X.append(int(m.getVarByName(f'X[{j}]').X))
            Y.append(int(m.getVarByName(f'Y[{j}]').X))
        
        circuits = [[instance.get_circuit_widths()[h],instance.get_circuit_heights()[h],X[h],Y[h]] for h in range(instance.get_n_circuits())]
        decode_circuits(instance, height, output_txt_path, output_img_path, circuits)
        print(f"\nSolution found for instance {i + 1}")
        print(f"optimum height is: {instance.get_min_height()}")
        print(f"minimum height found is: {height}")
        print(f"The time requested for this instance was: {run_time}")
        save_times_to_csv(rotation, simmetry_breaking, run_time, i)
        

