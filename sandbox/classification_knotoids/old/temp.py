import matplotlib.pyplot as plt

def parse_list(line, par_type):
    line = line.strip()
    if par_type == 'square':
        # for the case of []
        line = line.strip('[]')
        return [int(x) for x in line.split(', ')]
    else:
        # for the case of ()
        line = line.strip('()')
        return [1 if x == "True" else 0 for x in line.split(', ')]


# read txt
file_path = 'intersections_a_b_values.txt'  # Modifica con il percorso del tuo file
with open(file_path, 'r') as f:
    lines = f.readlines()

# extract the 3 lists
intersections = parse_list(lines[0], 'square')  # Prima lista con parentesi quadre
boolean_1 = parse_list(lines[1], 'round')  # Seconda lista con parentesi tonde
boolean_2 = parse_list(lines[2], 'round')  # Terza lista con parentesi tonde
print(intersections, "\n")
print(boolean_1, "\n")
print(boolean_2)

# print all
plt.figure(figsize=(10, 6))
plt.plot(range(len(intersections)), intersections, label='Intersections', color='green', alpha=.4)
plt.plot(range(len(boolean_1)), boolean_1, label='First method', color='blue', alpha=.4)
plt.plot(range(len(boolean_2)), boolean_2, label='Second method', color='red', alpha=.4)

#plt.scatter(range(len(intersections)), intersections, label='Intersections', color='green', alpha=.4)
#plt.scatter(range(len(boolean_1)), boolean_1, label='First method', color='blue', alpha=.4)
#plt.scatter(range(len(boolean_2)), boolean_2, label='Second method', color='red', alpha=.4)

plt.title('Is supercoiled?')
plt.legend()
plt.show()