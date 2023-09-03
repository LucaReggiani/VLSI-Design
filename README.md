# VLSI-Design
VLSI (Very Large Scale Integration) refers to the trend of integrating circuits into silicon chips. The goal is to design the VLSI of the circuits defining their electrical device: given a fixed-width plate and a list of rectangular circuits, decide how to place them on the plate so that the length of the final device is minimized.


## Prerequisites
To manipulate and analyze the data we produced, the following packages are sufficient:
 - ``numpy``
 - ``matplotlib``
 - ``pandas``

### SAT and SMT
If you wish to compute the SAT and SMT solutions independently, you'll need an additional Python package on top of the essentials:
 - ``z3-solver``

To install it:
```
pip install z3-solver
```

### CP 
For those who want to compute the CP  solutions themselves, there's one more requirement:

 - ``minizinc``

To install it:
```
pip install minizinc
```

Additionally, you'll need a local installation of Minizinc.

### MIP
To compute MIP, you'll additionally need gurobi and gurobipy, which require a license.

## Getting Results

### CP, SAT and SMT
To compute CP, SAT and SMT solutions, open your terminal and run ``main.py``, optionally providing input parameters such as:

- rotation;
- simmetry_breaking;
- folder_name.

For a detailed explanation of these parameters, consult our report.

### MIP
To compute MIP solutions you can run ``main.py`` or ``main_rot.py`` depending on if you want the standard or rotation model, optionally providing input parameters such as:

- simmetry_breaking;
- folder_name.

For a detailed explanation of these parameters, consult our report.

## Visualization
You can explore the results in the out and outRot folders. The img directory houses visual representations, while textual solutions reside in the txt folder.
