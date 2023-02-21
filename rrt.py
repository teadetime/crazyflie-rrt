from .occupany_grid import OccupanyGrid3d, Point3d
import numpy as np
import networkx as nx

class CrazyflieRRT:
    # Do we want to store points here as just np points, or use NetworkX?

    step_size           : float
    tree                : nx.DiGraph
    
    rng                 : np.random.Generator
    
    def __init__(self, grid: OccupanyGrid3d, init_state: Point3d = (0, 0, 0)):
        # Store occupancy grid to reference dimensions of area, as well as checking for collisions!
        self.tree = nx.DiGraph()
        self.tree.add_node(init_state)

        self.rng = np.random.default_rng(10)
        pass

    def step(self):
        # 1. Sample a random point from the configuration space (Start with 2D and then 3D position space)
        posn_min = self.grid.min_max[0]
        posn_max = self.grid.min_max[1]
        posn_random = self.rng.uniform(posn_min, posn_max, (3, 1)).flatten()

        # 2. Find the point in existing graph closest to the random point

        # 3. Take a 1 step_size step towards the random point from the chosen closest point
        # 4. Check if that step will encounter a collision. If yes, skip to the next loop
        # 5. Add the node to the tree. 
        pass

    def get_final_traj():
        # Hypothesis: Working backwards, at each point, the preceding node should be the adjacent node with the lowest ID.
        pass
