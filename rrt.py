from occupany_grid import OccupanyGrid3d, Point3d
import numpy as np
import networkx as nx

class CrazyflieRRT:
    # Do we want to store points here as just np points, or use NetworkX?

    step_size           : float
    tree                : nx.DiGraph
    grid                : OccupanyGrid3d
    goal_bias           : float = 0.3
    
    rng                 : np.random.Generator
    
    def __init__(self, grid: OccupanyGrid3d, init_state: Point3d = Point3d(0, 0, 0), step_size = 10, goal_bias=0.25):
        # Store occupancy grid to reference dimensions of area, as well as checking for collisions!
        self.tree = nx.DiGraph()
        self.tree.add_node(init_state, id=0)
        self.grid = grid
        self.step_size = step_size
        self.goal_bias = goal_bias

        self.rng = np.random.default_rng(10)

    def generate(self, goal: Point3d = None, max_iter:int = 10):
        for i in range(max_iter):
            # 1. Sample a random point from the configuration space (Start with 2D and then 3D position space)
            posn_min = self.grid.min_max[0]
            posn_max = self.grid.min_max[1]
            posn_random = self.rng.uniform(posn_min, posn_max, (1, 3)).transpose() # Generate random position as column vector

            # With a goal_bias percent chance, choose the actual goal as the random point
            # Heuristically bias the graph towards the goal a little bit
            if goal is not None and self.rng.random() > 1 - self.goal_bias:
                posn_random = np.array(goal).reshape(3, 1)

            # 2. Find the point in existing graph closest to the random point
            current_posns = np.array([np.array(node) for node in self.tree.nodes]).transpose() # Fetch all current node positions
            distances = np.linalg.norm(current_posns - posn_random, axis=0)
            i_closest_node = np.argmin(distances)
            closest_posn = np.atleast_2d(current_posns[:, i_closest_node]).T # Extract the column that corresponds to the closest point - and keep it as column
            closest_node = Point3d(*closest_posn.flatten())

            # 3. Take a 1 step_size step towards the random point from the chosen closest point
            displacement_vector = posn_random - closest_posn
            step_vector = displacement_vector * self.step_size / np.linalg.norm(displacement_vector)
            new_posn = closest_posn + step_vector
            new_node = Point3d(*new_posn.flatten())

            # 4. Check if that step will encounter a collision. If yes, skip to the next loop
            clear = self.grid.check_line(closest_node, new_node, bounding_box=[(0, 0, 0)])
            if not clear:
                continue

            # 5. Add the node to the tree. 
            self.tree.add_node(new_node, id=i+1)
            self.tree.add_edges_from([(closest_node, new_node)])

    def get_final_traj():
        # Hypothesis: Working backwards, at each point, the preceding node should be the adjacent node with the lowest ID.
        pass
