import math

def distance(first_coord, second_coord):
    orthogonal_x = first_coord[0] - second_coord[0]
    orthogonal_y = first_coord[1] - second_coord[1]
    return (orthogonal_x**2 + orthogonal_y**2)**0.5

def angle(first_coord, second_coord):
    # Output range from -math.pi to math.pi
    theta = math.atan2(first_coord[0] - second_coord[0], first_coord[1] - second_coord[1])
    return theta

def sign(val):
    if val > 0:
        return 1
    elif val < 0: 
        return -1
    else:
        return 0

def line(first_coord, second_coord):
    if first_coord == second_coord: # If start and end is the same, line is just the coord
        return [second_coord]

    line_steps = []

    # If line is vertical
    if first_coord[0] == second_coord[0]:
        x = first_coord[0]
        offset = sign(second_coord[1] - first_coord[1])

        for y in range(first_coord[1] + offset, second_coord[1] + offset, offset):
            line_steps.append((x,y))
        return line_steps

    # Get linear line via point slope formula
    m = float(first_coord[1] - second_coord[1]) / float(first_coord[0] - second_coord[0])
    b = float(first_coord[1]) - m*float(first_coord[0])

    def linear(x):
        return m*float(x) + b
    def inverse_linear(y):
        return (float(y) - b) / m

    # Get coordinates in line
    if (m >= -1 and m <= 1):
        offset = sign(second_coord[0] - first_coord[0])
        for x in range(first_coord[0] + offset, second_coord[0] + offset, offset):
            line_steps.append((x, round(linear(x))))
    else:
        offset = sign(second_coord[1] - first_coord[1])
        for y in range(first_coord[1] + offset, second_coord[1] + offset, offset):
            line_steps.append((round(inverse_linear(y)), y))

    return line_steps
