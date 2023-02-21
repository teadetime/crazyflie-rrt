from .occupany_grid import OccupanyGrid3d
import numpy as np
import networkx as nx

class CrazyflieRRT:
    # Do we want to store points here as just np points, or use NetworkX?

    step_size           : float
    random_points       : np.ndarray # Random points that are generated at each step
    tree_points         : np.ndarray # Points actually added to the tree
    
    def __init__(self, grid: OccupanyGrid3d):
        # Store occupancy grid to reference dimensions of area, as well as checking for collisions!
        pass

    def step():
        # 1. Sample a random point from the configuration space (Start with 2D and then 3D position space)
        # 2. Find the point in existing graph closest to the random point
        # 3. Take a 1 step_size step towards the random point from the chosen closest point
        # 4. Check if that step will encounter a collision. If yes, skip to the next loop
        # 5. Add the node to the tree. 
        pass

    def get_final_traj():
        # Hypothesis: Working backwards, at each point, the preceding node should be the adjacent node with the lowest ID.
        pass
