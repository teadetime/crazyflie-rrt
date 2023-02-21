from .occupany_grid import OccupanyGrid3d
import numpy as np

class CrazyflieRRT:
    # Do we want to store points here as just np points, or use NetworkX?

    step_size           : float
    random_points       : np.ndarray # Random points that are generated at each step
    tree_points         : np.ndarray # Points actually added to the tree
    
    def __init__(self, grid: OccupanyGrid3d):
        # Store occupancy grid to reference dimensions of area, as well as checking for collisions!
        pass

    def step():
        # 1. Sample a random point from the configuration space
        # 2. Take a 1 step_size step towards the random point
        # 3. Check if that step will encounter a collision. If yes, try again. If not, continue
        # 4. Add the node to the tree. 
        pass

    def get_final_traj():
        # Hypothesis: Working backwards, at each point, the preceding node should be the adjacent node with the lowest ID.
        pass
