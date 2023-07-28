## convert instances into dz

path_init = "./instances/txt/"
path_final = "./instances/dzn/"

for i in range(40):
    
    # read from .txt file
    input_file = path_init + 'ins-' + str(i+1) + '.txt'
    
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
        
    # write the new .dzn file
    output_file = path_final + 'ins-'+str(i+1)+'.dzn'
    
    file2 = open(output_file, 'w')
    
    file2.write(f'w = {w};\n')
    file2.write(f'n = {n};\n')

    file2.write(f'widths = {x};\n')
    file2.write(f'heights = {y};\n')
    
    file1.close()
    file2.close()
    