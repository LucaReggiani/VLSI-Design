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

### CP and IMP
For those who want to compute the CP and IMP solutions themselves, there's one more requirement:

 - ``minizinc``

To install it:
```
pip install minizinc
```

Additionally, you'll need a local installation of Minizinc.

For IMP solutions, ensure you have both the ``guroby`` and ``CPLEX`` solvers integrated into your Minizinc setup.

## Getting Results

### SAT and SMT
To compute SAT and SMT solutions, open your terminal and run ``main.py``, optionally providing input parameters such as:

- rotation;
- simmetry_breaking;
- folder_name.

For a detailed explanation of these parameters, consult our report.

### CP and IMP
[Details about how to compute CP and IMP solutions go here.]

## Visualization
You can explore the results in the out and outRot folders. The img directory houses visual representations, while textual solutions reside in the txt folder.
