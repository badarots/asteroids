import math

# funcoes utilitarias
def constrain(x, min, max):
    if x > max:
        x = max
    elif x < min:
        x = min
    return x

def cycle(x, min, max):
    return (x - min) % (max - min) + min

def distance(p1=(0,0), p2=(0,0)):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
