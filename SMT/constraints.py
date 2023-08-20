from z3 import *
import numpy as np

def rotation_switch(instance, s, plate_height):

    rot_flags = instance.get_rotation_flags()
    widths = instance.get_circuit_widths()
    heights = instance.get_circuit_heights()

    # Rotation constraints
    for cir in range(instance.get_n_circuits()):
        s.add(If(rot_flags[cir], widths[cir] == instance.get_circuit(cir)[1], widths[cir] == instance.get_circuit(cir)[0]))
        s.add(If(rot_flags[cir], heights[cir] == instance.get_circuit(cir)[0], heights[cir] == instance.get_circuit(cir)[1]))


def check_rot_flags(instance, solver, plate_height):

    plate_width = instance.get_plate_width()
    s = solver
    rot_flags = instance.get_rotation_flags()

    for cir in range(instance.get_n_circuits()):
        # check width
        if instance.get_circuit(cir)[1] > plate_width:
            # do not allow rotation if rectangle height (width) is larger than strip width (height)
            s.add(Not(rot_flags[cir]))

        # force rotation if rectangle width (height) is larger than strip width (height)
        if instance.get_circuit(cir)[1] > plate_width:
            s.add(rot_flags[cir])

        
        # check height
        if instance.get_circuit(cir)[0] > plate_height:
            # do not allow rotation if rectangle height (width) is larger than strip width (height)
            s.add(Not(rot_flags[cir]))

        # force rotation if rectangle width (height) is larger than strip width (height)
        if instance.get_circuit(cir)[1] > plate_height:
            s.add(rot_flags[cir])

#domain constraint
def set_domain_constraints(instance, solver, plate_height):

    s = solver
    corners = instance.get_corners()
    widths = instance.get_circuit_widths()
    heights = instance.get_circuit_heights()
    plate_width = instance.get_plate_width()
    rotation = instance.get_rotation()
    simmetry_breaking = instance.get_simmetry_breaking()

    lr = instance.lr
    ud = instance.ud

    for cir in range(instance.get_n_circuits()):

        # Every X coordinate of each circuit's corner must be >= 0
        s.add(corners[cir][0] >= 0)
        # Every Y coordinate of each circuit's corner must be >= 0
        s.add(corners[cir][1] >= 0)
        # Every X coordinate of each circuit's corner + the width of the circuit must be <= the plate width
        s.add(corners[cir][0] + widths[cir] <= plate_width)
        # Every Y coordinate of each circuit's corner + the height of the circuit must be <= the plate height
        s.add(corners[cir][1] + heights[cir] <= plate_height)

        if simmetry_breaking:
            # Biggest circuit by Area
            widest_idx = np.argmax([instance.get_circuit(r)[0] * instance.get_circuit(r)[1] for r in range(instance.get_n_circuits())])

            # if c is the widest index, it should be as left as possible, with a small left-slide movement
            if cir == widest_idx:
                s.add(corners[cir][0] <= (plate_width - widths[cir])/2)
                s.add(corners[cir][1] <= (plate_height - heights[cir])/2)
            else:
                # if the width of c is > the maximum slide allowed for the widest index 
                # c cannot be placed on the left of the widest index
                if instance.get_circuit(cir)[0] > (plate_width - instance.get_circuit(widest_idx)[0])/2:
                    s.add(lr[cir][widest_idx] == False)

                if instance.get_circuit(cir)[1] > (plate_height - instance.get_circuit(widest_idx)[1])/2:
                    s.add(ud[cir][widest_idx] == False)
        

# non-overlapping constraint
def set_non_overlap_constraints(instance, s, plate_height):
    
    corners = instance.get_corners()
    widths = instance.get_circuit_widths()
    heights = instance.get_circuit_heights()
    plate_width = instance.get_plate_width()
    simmetry_breaking = instance.get_simmetry_breaking()

    lr = instance.lr
    ud = instance.ud

    # Pairwise constraints
    for cir in range(instance.get_n_circuits()):

        for j in range(cir+1, instance.get_n_circuits()):

            # Non overlapping constraints
            s.add((corners[cir][0] + widths[cir] <= corners[j][0]) == lr[cir][j])
            s.add((corners[cir][1] + heights[cir] <= corners[j][1]) == ud[cir][j])
            s.add((corners[j][0] + widths[j] <= corners[cir][0]) == lr[j][cir])
            s.add((corners[j][1] + heights[j] <= corners[cir][1]) == ud[j][cir])

            s.add(Or(lr[cir][j], lr[j][cir], ud[cir][j], ud[j][cir]))

            if simmetry_breaking:
                # Rectangle pair incompatibilities
                # SR: Breaking symmetries for same-sized rectangles
                s.add(Implies(And(widths[cir] == widths[j], heights[cir] == heights[j]), lr[j][cir] == False))
                s.add(Implies(And(widths[cir] == widths[j], heights[cir] == heights[j]), ud[j][cir] == False))

                # LR (horizontal)
                s.add(Implies(widths[cir] + widths[j] > plate_width, lr[cir][j] == False))
                s.add(Implies(widths[j] + widths[cir] > plate_width, lr[j][cir] == False))
                # LR (vertical)
                s.add(Implies(heights[cir] + heights[j] > plate_height, ud[cir][j] == False))
                s.add(Implies(heights[j] + heights[cir] > plate_height, ud[j][cir] == False))