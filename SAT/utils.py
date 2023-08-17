import re
import os
import pandas as pd
import matplotlib.pyplot as plt

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

def decode_positions(encoding, min_value=0):
        
        """
        Decode an encoded position.

        Args:
            encoding (list of bool): Order-encoded value in the form [False, ..., False, True, True, ...]
            min_value (int, optional): Starting value of the domain of the encoded value. Default is 0.

        Returns:
            int: The decoded position
        """

        decoded_position = next((i + min_value for i, val in enumerate(encoding) if val), len(encoding) + min_value)
        return decoded_position


def decode_circuits(instance, m, height, output_txt_path, output_img_path):
    '''
    Decoding circuits positions, setting up width and height depending on rotation. 
    It plots the solutions in the correct folder, writing a txt file containing the textual solution.
    '''
    rotation = instance.get_rotation()
    rot_flags = instance.get_rotation_flags()
    x_positions = instance.get_x_positions()
    y_positions = instance.get_y_positions()
    
    # decode the X circuits position
    px_eval = [[m.evaluate(x_positions[c][j], model_completion = True) for j in range(len(x_positions[c]))] for c in range(len(x_positions))]
    x_decoded = [decode_positions(p) for p in px_eval]

    # decode the Y circuits position
    py_eval = [[m.evaluate(y_positions[c][j], model_completion = True) for j in range(len(y_positions[c]))] for c in range(len(y_positions))]
    y_decoded = [decode_positions(p) for p in py_eval]

    # file name
    filename = instance.get_name().split('_')[0]

    # Setting circuits width and height
    if rotation:

        circuits = []
        for h in range(instance.get_n_circuits()):
            rotation_flag = m.evaluate(rot_flags[h], model_completion = True)
            if rotation_flag:
                rectangle_width = instance.get_circuit(h)[1]
                rectangle_height = instance.get_circuit(h)[0]
            else:
                rectangle_width = instance.get_circuit(h)[0]
                rectangle_height = instance.get_circuit(h)[1]
        
            circuits.append([rectangle_width, rectangle_height, x_decoded[h], y_decoded[h]])
    else:
        circuits = [[instance.get_circuit(h)[0], instance.get_circuit(h)[1], x_decoded[h], y_decoded[h]] for h in range(instance.get_n_circuits())]

    plot_solution(instance.get_plate_width(), height, circuits, output_img_path+f'out-{int(filename) + 1}.png')
    output_solution(circuits, instance.get_plate_width(), height, output_txt_path+f'out-{int(filename) + 1}.txt')


# Method used to plot the solution
# EX: plot_solution(9, 12, [[3, 3, 4, 0],[2, 4, 7, 0],[2, 8, 7, 4],[3, 9, 4, 3],[4, 12, 0, 0 ]])
# To save the image plotted, add a location to the file argument. Note: image will not be shown when saved.
def plot_solution(width, height, circuits, file=None):
    SIZE = 10
    fig, ax = plt.subplots()

    # fig.set_size_inches(SIZE, SIZE * height / width)
    fig.set_size_inches(SIZE, SIZE * height / width)
    colors = ['tab:red','tab:orange', 'yellow', 'tab:green','tab:blue','tab:purple','tab:brown', 'tab:grey']
    for i in range(len(circuits)):
        
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
    ax.set_xlim(0, width)
    ax.set_xticks(range(width + 1))
    ax.set_yticks(range(height + 1))
    ax.grid(color='b', linewidth = 1)

    if file is not None:
        plt.savefig(file)
        plt.close()
    else:
        plt.show()

def output_solution(circuits, plate_width, plate_height, output_path):

    solution = []
    # append plate width and height
    solution.append(str(plate_width) + ' ' + str(plate_height))
    # append number of circuits for the current instance
    solution.append(str(len(circuits)))
    # append width, height, and coordinates per circuit
    for x in circuits:
        
        x_width = x[0]
        x_height = x[1]
            
        solution.append(str(x_width) + ' ' + str(x_height) + ' ' + str(x[2]) + ' ' + str(x[3]))
    
    # write the array into the output file
    with open(output_path, 'w') as output:
        for item in solution:
            output.write(item)
            output.write('\n')

def save_times_to_csv(rotation, simmetry_breaking, timings, n_instances):
        '''
        Saving time needed to solve the instances into 'timing.csv' file
        '''
    # Path to the existing CSV file
        timings_csv = './SAT/timing.csv'

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