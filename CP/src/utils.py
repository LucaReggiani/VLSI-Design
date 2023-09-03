import os
import re
import matplotlib.pyplot as plt
import pandas as pd

def set_environment(rotation, simmetry_breaking):
    '''
    Functions that is in charge to set the output folders, depending on
    the rotation flag, the simmetry_breaking flag. It also creates the failures.txt file, 
    which contains all the failed instances according to the parameters passed. It also
    returns the model_name
    '''
    if rotation:

        if simmetry_breaking:
            subfolder = '/simmetry_breaking/'
            model_name = "./cp_rot_sb.mzn"
        else:
            subfolder = '/no_simmetry_breaking/'
            model_name = "./cp_rot.mzn"

        output_txt_path = './outRot/txt' + subfolder
        output_img_path = './outRot/img' + subfolder
        output_failure_path = './outRot/failures.txt'
        # output_timings_path = './outputRot/timings.csv'

    else:

        if simmetry_breaking:
            subfolder = '/simmetry_breaking/'
            model_name ='./cp_norot_sb.mzn'
        else:
            subfolder = '/no_simmetry_breaking/'
            model_name = "./cp_norot.mzn"
            
        output_txt_path = './out/txt' + subfolder
        output_img_path = './out/img' + subfolder
        output_failure_path = './out/failures.txt'

    # write the heading in failures file
    with open(output_failure_path, 'a') as output:
        output.write(f'\nSYMMETRY BREAKING: {simmetry_breaking}\n')
    return output_txt_path, output_img_path, output_failure_path, model_name


# Method used to plot the solution
def plot_solution(instance, height, circuits, file=None):
        
    rotation = instance.get_rotation()
    width = instance.get_plate_width()
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

def output_solution(instance, plate_height, circuits, output_path):

    rotation = instance.get_rotation()
    plate_width = instance.get_plate_width()

    solution = []
    # append plate width and height
    solution.append(str(plate_width) + ' ' + str(plate_height))
    # append number of circuits for the current instance
    solution.append(str(len(circuits)))
    # append width, height, and coordinates per circuit
    for j in range(instance.get_n_circuits()):
        if rotation:
            x_width = circuits[j][0] if circuits[j][4] == 0  else circuits[j][1]
            x_height = circuits[j][1] if circuits[j][4] == 0  else circuits[j][0]
        else:
            x_width = circuits[j][0]
            x_height = circuits[j][1]
        #out_file.write(f"{x[k]} {y[k]} {out['X'][k]} {out['Y'][k]}\n")
        solution.append(str(x_width) + ' ' + str(x_height) + ' ' + str(circuits[j][2]) + ' ' + str(circuits[j][3]))
    
    # write the array into the output file
    with open(output_path, 'w') as output:
        for item in solution:
            output.write(item)
            output.write('\n')

def decode_circuits(instance, height, output_txt_path, output_img_path, circuits):
    '''
    Decoding circuits positions, setting up width and height depending on rotation. 
    It plots the solutions in the correct folder, writing a txt file containing the textual solution.
    '''
    
    #circuits = [[widths[h], heights[h], start_x[h], start_y[h]] for h in range(instance.get_n_circuits())]

    # file name
    filename = instance.get_name().split('_')[0]

    plot_solution(instance, height, circuits, output_img_path+f'out-{int(filename) + 1}.png')
    output_solution(instance, height, circuits, output_txt_path+f'out-{int(filename) + 1}.txt')

def sorted_alphanumeric(data):
    '''
    alphanumeric sorting of instances names
    '''
    def alphanumeric_key(key):
        return [int(c) if c.isdigit() else c.lower() for c in re.split('([0-9]+)', key)]

    return sorted(data, key=alphanumeric_key)

def import_instances(folder):
    '''
    import instances, file by file
    '''
    # list of files, ordered by name
    files = [file for file in sorted_alphanumeric(os.listdir(folder))]
    # list of instances, splitted line by line each instance
    instances = [open(folder + file).read().splitlines() for file in files]
    return instances

def save_times_to_csv(rotation, simmetry_breaking, timing, ind):
    '''
    Saving time needed to solve the instances into 'timing.csv' file
    '''
    # Path to the existing CSV file
    timings_csv = './timing.csv'

    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(timings_csv)
    
        # If the csv file is empty, add all the instances as the first column
        if df.empty:
            first_column = [f'Instance {i+1}' for i in range(40)]
            # Add the new column to the DataFrame
            df['Instances'] = first_column
            df.to_csv(timings_csv, index=False)  # Write the updated DataFrame back to the CSV file

    except:
        
        # If here, the dataframe is empty and causes some problems to be imported into pandas
        df = pd.DataFrame()
        first_column = [f'Instance {i+1}' for i in range(40)]
        # Add the new column to the DataFrame
        df['Instances'] = first_column
        df.to_csv(timings_csv, index=False)  # Write the updated DataFrame back to the CSV file
    

    # Setting new column name
    if rotation:

        column_name = 'Rotation '
        if simmetry_breaking:
            column_name += 'SB'
        else:
            column_name += 'No SB'
    else:
        column_name = 'No Rotation '
        if simmetry_breaking:
            column_name += 'SB'
        else:
            column_name += 'No SB'

    # Add the new column to the DataFrame
    df.at[ind, column_name] = timing

    # Write the updated DataFrame back to the CSV file
    df.to_csv(timings_csv, index=False)

    print("CSV file up-to-date")