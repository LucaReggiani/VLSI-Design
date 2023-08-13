import re
import os
import matplotlib.pyplot as plt
from z3 import *

# alphanumeric sorting of instances names
def sorted_alphanumeric(data):

    def alphanumeric_key(key):
        return [int(c) if c.isdigit() else c.lower() for c in re.split('([0-9]+)', key)]

    return sorted(data, key=alphanumeric_key)

# import instances, file by file
def import_instances(folder):
    # list of files, ordered by name
    files = [file for file in sorted_alphanumeric(os.listdir(folder))]
    # list of instances, splitted line by line each instance
    instances = [open(folder + file).read().splitlines() for file in files]
    return instances

def add_non_overlapping_constraint(corners, widths, heights, c1, c2, non_overlapping_constraints = [True, True, True, True]):
    non_overlap = []
    if non_overlapping_constraints[0]:
        non_overlap.append(corners[c1][0] + widths[c1] <= corners[c2][0])
    if non_overlapping_constraints[1]:
        non_overlap.append(corners[c2][0] + widths[c2] <= corners[c1][0])
    if non_overlapping_constraints[2]:
        non_overlap.append(corners[c1][1] + heights[c1] <= corners[c2][1])
    if non_overlapping_constraints[3]:
        non_overlap.append(corners[c2][1] + heights[c2] <= corners[c1][1])
    return non_overlap


# be sure to non-overlap the rectangles with simmetry breaking enabled.
# size can be either eidth or height
def non_overlapping_constraint(solver, corners, size, c1, c2, flag):
    solver.add(If(flag, corners[c1][0] + size[c1] <= corners[c2][0], BoolVal(True)))
    
# Method used to plot the solution
# EX: plot_solution(9, 12, [[3, 3, 4, 0],[2, 4, 7, 0],[2, 8, 7, 4],[3, 9, 4, 3],[4, 12, 0, 0 ]])
# To save the image plotted, add a location to the file argument. Note: image will not be shown when saved.
def plot_solution(width, height, circuits, model, rotation, file=None):
    SIZE = 10
    fig, ax = plt.subplots()

    # fig.set_size_inches(SIZE, SIZE * height / width)
    fig.set_size_inches(SIZE, SIZE * height / width)
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
    ax.set_xlim(0, width)
    ax.set_xticks(range(width + 1))
    ax.set_yticks(range(height + 1))
    ax.grid(color='b', linewidth = 1)

    if file is not None:
        plt.savefig(file)
        plt.close()
    else:
        plt.show()

def output_solution(circuits, plate_width, plate_height, rotation, model, output_path):

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