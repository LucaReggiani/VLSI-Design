from z3 import *
import numpy as np



def set_domain_constraints(instance, s, plate_height):
    '''
    Set domain constraint. Because of these constraints, it is sure the circuits are going to suit the plate, by width and by height.
    '''
    plate_width = instance.get_plate_width()
    rotation = instance.get_rotation()
    simmetry_breaking = instance.get_simmetry_breaking()

    x_positions = instance.get_x_positions()
    y_positions = instance.get_y_positions()

    rot_flags = instance.get_rotation_flags()

    # if rotation is enabled
    if rotation:

        for cir in range(instance.get_n_circuits()):

            # the "cir" circuit has the flag "rotation" set to False
            for e in range(plate_width - instance.get_circuit(cir)[0], plate_width):
                s.add(Implies(Not(rot_flags[cir]), x_positions[cir][e]))
            
            for f in range(plate_height - instance.get_circuit(cir)[1], plate_height):
                s.add(Implies(Not(rot_flags[cir]), y_positions[cir][f]))

            # the "cir" circuit has the flag "rotation" set to True
            for e in range(plate_width - instance.get_circuit(cir)[1], plate_width):
                s.add(Implies(rot_flags[cir], x_positions[cir][e]))
            
            for f in range(plate_height - instance.get_circuit(cir)[0], plate_height):
                s.add(Implies(rot_flags[cir], y_positions[cir][f]))
            
            # If we are applying simmetry breaking
            if simmetry_breaking:

                # Biggest circuit by Area
                widest_idx = np.argmax([instance.get_circuit(r)[0] * instance.get_circuit(r)[1] for r in range(instance.get_n_circuits())])

                # ---> the widest circuit has the flag "rotation" set to False. <---

                # We are setting to True the x-position of a circuit in order to allow it to "slide" horizontallly
                for e in range((plate_width - instance.get_circuit(widest_idx)[0]) // 2, plate_width - instance.get_circuit(widest_idx)[0]):
                    s.add(Implies(Not(rot_flags[widest_idx]), x_positions[widest_idx][e]))

                # We are setting to True the y-position of a circuit in order to allow it to "slide" vertically
                for f in range((plate_height - instance.get_circuit(widest_idx)[1]) // 2, plate_height - instance.get_circuit(widest_idx)[1]):
                    s.add(Implies(Not(rot_flags[widest_idx]), y_positions[widest_idx][f]))
                    
                # ---> the widest circuit has the flag "rotation" set to True. <---

                # We are setting to True the x-position of a circuit in order to allow it to "slide" horizontallly
                for e in range((plate_width - instance.get_circuit(widest_idx)[1]) // 2, plate_width - instance.get_circuit(widest_idx)[1]):
                    s.add(Implies(rot_flags[widest_idx], x_positions[widest_idx][e]))

                # We are setting to True the y-position of a circuit in order to allow it to "slide" vertically
                for f in range((plate_height - instance.get_circuit(widest_idx)[0]) // 2, plate_height - instance.get_circuit(widest_idx)[0]):
                    s.add(Implies(rot_flags[widest_idx], y_positions[widest_idx][f]))
    else:
        # If rotation is not enabled
        for cir in range(instance.get_n_circuits()):
            for e in range(plate_width - instance.get_circuit(cir)[0], plate_width):
                s.add(x_positions[cir][e])
            
            for f in range(plate_height - instance.get_circuit(cir)[1], plate_height):
                s.add(y_positions[cir][f])

            # If we are applying simmetry breaking
            if simmetry_breaking:
                widest_idx = np.argmax([instance.get_circuit(r)[0] * instance.get_circuit(r)[1] for r in range(instance.get_n_circuits())])
                for e in range((plate_width - instance.get_circuit(widest_idx)[0]) // 2, plate_width - instance.get_circuit(widest_idx)[0]):
                    s.add(x_positions[widest_idx][e])
                
                for f in range((plate_height - instance.get_circuit(widest_idx)[1]) // 2, plate_height - instance.get_circuit(widest_idx)[1]):
                    s.add(y_positions[widest_idx][f])

def ordering_constraints(instance, s, plate_height):
    plate_width = instance.get_plate_width()

    x_positions = instance.get_x_positions()
    y_positions = instance.get_y_positions()

    for cir in range(instance.get_n_circuits()):
        for e in range(plate_width - 1):
            s.add(Implies(x_positions[cir][e], x_positions[cir][e + 1]))

        for f in range(plate_height - 1):
            s.add(Implies(y_positions[cir][f], y_positions[cir][f + 1]))


def add_3l_clause(instance, lrud, pxy, circuit_idx_1, circuit_idx_2, direction, plate_height, s):
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
        circuit_idx_1 : int
            index of the first rectangle.
        circuit_idx_2 : int
            index of the second rectangle.
        """

        rotation = instance.get_rotation()
        rot_flags = instance.get_rotation_flags()

        if direction == 'x':
            rectangle_measure = instance.get_circuit(circuit_idx_1)[0]
            other_rectangle_measure = instance.get_circuit(circuit_idx_1)[1]
            strip_measure = instance.get_plate_width()
        elif direction == 'y':
            rectangle_measure = instance.get_circuit(circuit_idx_1)[1]
            other_rectangle_measure = instance.get_circuit(circuit_idx_1)[0]
            strip_measure = plate_height
        else:
            print("The direction must be either 'x' or 'y'")
            return

        if rotation:
            
            # do not allow rotation if rectangle height (width) is larger than strip width (height)
            if other_rectangle_measure > strip_measure:
                s.add(Not(rot_flags[circuit_idx_1]))

            # force rotation if rectangle width (height) is larger than strip width (height)
            if rectangle_measure > strip_measure:
                s.add(rot_flags[circuit_idx_1])

            # no rotation
            for k in range(min(rectangle_measure, strip_measure)):
                
                s.add(Implies(Not(rot_flags[circuit_idx_1]),
                                    Or(Not(lrud[circuit_idx_1][circuit_idx_2]), Not(pxy[circuit_idx_2][k]))))
                
            for k in range(strip_measure - rectangle_measure):
                k1 = k + rectangle_measure
                s.add(Implies(Not(rot_flags[circuit_idx_1]),
                                    Or(Not(lrud[circuit_idx_1][circuit_idx_2]), pxy[circuit_idx_1][k], Not(pxy[circuit_idx_2][k1]))))
            
            # rotation
            for k in range(min(other_rectangle_measure, strip_measure)):
                s.add(Implies(rot_flags[circuit_idx_1],
                                    Or(Not(lrud[circuit_idx_1][circuit_idx_2]), Not(pxy[circuit_idx_2][k]))))
            for k in range(strip_measure - other_rectangle_measure):
                k1 = k + other_rectangle_measure
                s.add(Implies(rot_flags[circuit_idx_1],
                                    Or(Not(lrud[circuit_idx_1][circuit_idx_2]), pxy[circuit_idx_1][k], Not(pxy[circuit_idx_2][k1]))))
                
        else:
            #if rectangle 1 is left of rectangle 2, rectangle 2 cannot be at the left of the right edge of rectangle 1.
            for k in range(rectangle_measure):
                s.add(Or(Not(lrud[circuit_idx_1][circuit_idx_2]), Not(pxy[circuit_idx_2][k])))

            for k in range(strip_measure - rectangle_measure):
                k1 = k + rectangle_measure
                s.add(Or(Not(lrud[circuit_idx_1][circuit_idx_2]), pxy[circuit_idx_1][k], Not(pxy[circuit_idx_2][k1])))

def add_non_overlapping_constraint(instance, c, j, s, plate_height, to_add = [True, True, True, True]):

    lr = instance.lr
    ud = instance.ud

    x_positions = instance.get_x_positions()
    y_positions = instance.get_y_positions()

    # non-overlapping constraint
    literals_4l = []
    if to_add[0]:
        literals_4l.append(lr[c][j])
        add_3l_clause(instance, lr, x_positions, c, j, 'x', plate_height, s)
    if to_add[1]:
        literals_4l.append(lr[j][c])
        add_3l_clause(instance, lr, x_positions, j, c, 'x', plate_height, s)
    if to_add[2]:
        literals_4l.append(ud[c][j])
        add_3l_clause(instance, ud, y_positions, c, j, 'y', plate_height, s)
    if to_add[3]:
        literals_4l.append(ud[j][c])
        add_3l_clause(instance, ud, y_positions, j, c, 'y', plate_height, s)

    s.add(Or(literals_4l))


def set_non_overlap_constraints(instance, s, plate_height):

    plate_width = instance.get_plate_width()
    simmetry_breaking = instance.get_simmetry_breaking()

    # non-overlap constraints
    if simmetry_breaking:
        widest_idx = np.argmax([instance.get_circuit(r)[0] * instance.get_circuit(r)[1] for r in range(instance.get_n_circuits())])

        for c in range(instance.get_n_circuits()):
            for j in range(c+1, instance.get_n_circuits()):

                # Reducing the domain for the largest rectangle
                if j == widest_idx:
                    large_width = instance.get_circuit(c)[0] > (plate_width - instance.get_circuit(widest_idx)[0])//2
                    large_height = instance.get_circuit(c)[1] > (plate_height - instance.get_circuit(widest_idx)[1])//2
                    if large_width and large_height:
                        add_non_overlapping_constraint(instance, c, j, s, plate_height, to_add=[False, True, False, True])
                    elif large_width:
                        add_non_overlapping_constraint(instance, c, j, s, plate_height, to_add=[False, True, True, True])
                    elif large_height:
                        add_non_overlapping_constraint(instance, c, j, s, plate_height, to_add=[True, True, False, True])
                    else:
                        add_non_overlapping_constraint(instance, c, j, s, plate_height)

                # Breaking symmetries for same-sized rectangles
                elif instance.get_circuit(c)[0] == instance.get_circuit(j)[0] and instance.get_circuit(c)[1] == instance.get_circuit(j)[1]:
                    add_non_overlapping_constraint(instance, c, j, s, plate_height, to_add=[True, False, True, False])

                # Large Rectangles (horizontal)
                elif instance.get_circuit(c)[0] + instance.get_circuit(j)[0] > plate_width:
                    add_non_overlapping_constraint(instance, c, j, s, plate_height, to_add=[False, False, True, True])

                # Large Rectangles (vertical)
                elif instance.get_circuit(c)[1] + instance.get_circuit(j)[1] > plate_height:
                    add_non_overlapping_constraint(instance, c, j, s, plate_height, to_add=[True, True, False, False])
                else:
                    add_non_overlapping_constraint(instance, c, j, s, plate_height)
    else:
        for c in range(instance.get_n_circuits()):
            for j in range(c+1, instance.get_n_circuits()):
                add_non_overlapping_constraint(instance, c, j, s, plate_height)