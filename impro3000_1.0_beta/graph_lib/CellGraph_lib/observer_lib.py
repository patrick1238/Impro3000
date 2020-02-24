import numpy as np

def observe_for_doubled_entry(nodes,position,diameter):
    for node in nodes:
        if __calculate_distance(node,position) <= diameter:
            return False
    return True
        
def __calculate_distance(position1,position2):
    return (np.sqrt((position1[0]-position2[0])**2+(position1[1]-position2[1])**2))