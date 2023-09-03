import re
import os
import matplotlib.pyplot as plt
import pandas as pd

def set_environment(rotation, simmetry_breaking, approach):
    '''
    Functions that is in charge to set the output folders, depending on
    the rotation flag, the simmetry_breaking flag. It also creates the failures.txt file, 
    which contains all the failed instances according to the parameters passed
    '''
    if rotation:

        if simmetry_breaking:
            subfolder = '/simmetry_breaking/'
        else:
            subfolder = '/no_simmetry_breaking/'

        output_txt_path = f'./{approach}/outputRot/txt' + subfolder
        output_img_path = f'./{approach}/outputRot/img' + subfolder
        output_failure_path = f'./{approach}/outputRot/failures.txt'
        # output_timings_path = './outputRot/timings.csv'

    else:

        if simmetry_breaking:
            subfolder = '/simmetry_breaking/'
        else:
            subfolder = '/no_simmetry_breaking/'
        output_txt_path = f'./{approach}/output/txt' + subfolder
        output_img_path = f'./{approach}/output/img' + subfolder
        output_failure_path = f'./{approach}/output/failures.txt'

    # write the heading in failures file
    with open(output_failure_path, 'a') as output:
        output.write(f'\nSYMMETRY BREAKING: {simmetry_breaking}\n')
    
    return output_txt_path, output_img_path, output_failure_path


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


# Method used to plot the solution
# EX: plot_solution(9, 12, [[3, 3, 4, 0],[2, 4, 7, 0],[2, 8, 7, 4],[3, 9, 4, 3],[4, 12, 0, 0 ]])
# To save the image plotted, add a location to the file argument. Note: image will not be shown when saved.
def plot_solution(instance, model, circuits, height, file=None):

    SIZE = 10
    fig, ax = plt.subplots()
    rotation = rotation = instance.get_rotation()
    plate_width = instance.get_plate_width()

    # fig.set_size_inches(SIZE, SIZE * height / width)
    fig.set_size_inches(SIZE, SIZE * height / plate_width)
    colors = ['tab:red','tab:orange', 'yellow', 'tab:green','tab:blue','tab:purple','tab:brown', 'tab:grey']
    for i in range(len(circuits)):
        
        if rotation:
            i_width = model[circuits[i][0]].as_long()
            i_height = model[circuits[i][1]].as_long()
        
        else:
            i_width = circuits[i][0]
            i_height = circuits[i][1]
        
        i_x_coordinate = circuits[i][2]
        i_y_coordinate = circuits[i][3]
        ax.broken_barh([(i_x_coordinate, i_width)], (i_y_coordinate, i_height),
                        facecolors=colors[i % len(colors)],
                        edgecolors=("black"),
                        linewidths=(2,),)
    #ax.set_ylim(0, height)
    ax.set_ylim(0,height)
    ax.set_xlim(0, plate_width)
    ax.set_xticks(range(plate_width + 1))
    ax.set_yticks(range(height + 1))
    ax.grid(color='b', linewidth = 1)

    if file is not None:
        plt.savefig(file)
        plt.close()
    else:
        plt.show()

def output_solution(instance, model, circuits, plate_height, output_path):

    rotation = instance.get_rotation()
    plate_width = instance.get_plate_width()

    solution = []
    # append plate width and height
    solution.append(str(plate_width) + ' ' + str(plate_height))
    # append number of circuits for the current instance
    solution.append(str(len(circuits)))
    # append width, height, and coordinates per circuit
    for x in circuits:
        if rotation:
            x_width = model[x[0]].as_long()
            x_height = model[x[1]].as_long()
        else:
            x_width = x[0]
            x_height = x[1]
        solution.append(str(x_width) + ' ' + str(x_height) + ' ' + str(x[2]) + ' ' + str(x[3]))
    
    # write the array into the output file
    with open(output_path, 'w') as output:
        for item in solution:
            output.write(item)
            output.write('\n')

def decode_circuits(instance, m, height, output_txt_path, output_img_path):
    '''
    Decoding circuits positions, setting up width and height depending on rotation. 
    It plots the solutions in the correct folder, writing a txt file containing the textual solution.
    '''
    rotation = instance.get_rotation()
    rot_flags = instance.get_rotation_flags()
    corners = instance.get_corners()
    widths = instance.get_circuit_widths()
    heights = instance.get_circuit_heights()

    eval_corners = [[int(m.evaluate(corners[h][j]).as_string()) for j in range(2)] for h in range(instance.get_n_circuits())]
    # Save solution
    start_x = []
    start_y = []
    for j in range(len(eval_corners)):
        start_x.append(int(eval_corners[j][0]))
        start_y.append(int(eval_corners[j][1]))

    circuits = [[widths[h], heights[h], start_x[h], start_y[h]] for h in range(instance.get_n_circuits())]

    # file name
    filename = instance.get_name().split('_')[0]

    plot_solution(instance, m, circuits, height, output_img_path+f'out-{int(filename) + 1}.png')
    output_solution(instance, m, circuits, height, output_txt_path+f'out-{int(filename) + 1}.txt')


def save_times_to_csv(rotation, simmetry_breaking, timings, n_instances):
    '''
    Saving time needed to solve the instances into 'timing.csv' file
    '''
    # Path to the existing CSV file
    timings_csv = './SMT/timing.csv'

    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(timings_csv)
    
        # If the csv file is empty, add all the instances as the first column
        if df.empty:
            first_column = [f'Instance {i+1}' for i in range(n_instances)]
            # Add the new column to the DataFrame
            df['Instances'] = first_column
            df.to_csv(timings_csv, index=False)  # Write the updated DataFrame back to the CSV file

    except pd.errors.EmptyDataError:
        
        # If here, the dataframe is empty and causes some problems to be imported into pandas
        df = pd.DataFrame()
        first_column = [f'Instance {i+1}' for i in range(n_instances)]
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
    df[column_name] = timings

    # Write the updated DataFrame back to the CSV file
    df.to_csv(timings_csv, index=False)

    print("CSV file up-to-date")