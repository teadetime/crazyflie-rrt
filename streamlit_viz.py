import numpy as np
import sys

from occupany_grid import OccupanyGrid3d, Point3d
from viz import viz_world
from rrt import CrazyflieRRT

import streamlit as st

import networkx as nx

if __name__ == "__main__":
    # The Robosys Environment
    origin = Point3d(
        200, 100, 0
    )  # Bottom Left corner of grid is 2 meters to the left (x) and 1m negative y
    grid_width = 100  # 5 meters wide (x)
    grid_depth = 60  # 3 meters tall (y)
    grid_height = 20  # 2 meters tall (z)
    robosys_grid = OccupanyGrid3d(
        grid_width, grid_depth, grid_height, origin, cell_size=5
    )
    robosys_grid.add_rectangles(
        Point3d(0, 20, 0), Point3d(60, 40, 5)
    )  # Measurements in CM relative to origin
    robosys_grid.add_rectangles(Point3d(-30, -60, 0), Point3d(190, -20, 34))

    world = viz_world(robosys_grid)

    world.add_omap_to_fig()
    # mid_point_posn_y = st.slider("Mid point position", -10, 10, 0)
    # mid_point = Point3d(30, mid_point_posn_y, 60)
    # world.add_edge(Point3d(0, 0, 0), mid_point, end_name="Some point")
    # world.add_edge(mid_point, Point3d(60, 10, 60), end_name="Test")
    # world.add_point(Point3d(0, 0, 0), "Origin", True, "red")

    with st.form("sim_params"):
        step_size = st.slider("Step size (cm)", 1, 50, 20)
        iterations = st.slider("Iterations", 10, 1000, 500)
        use_goal = st.checkbox("Use goal", True)
        
        goal_posn = [150., -90., 0.]
        coord_name = ["X", "Y", "Z"]
        min_max = robosys_grid.min_max
        for i, col in enumerate(st.columns(3)):
            with col:
                goal_posn[i] = st.number_input(coord_name[i], float(min_max[0][i]), float(min_max[1][i]), float(goal_posn[i]))
        goal_posn = Point3d(*goal_posn)

        goal_bias = st.slider("Goal bias", 0., 1., 0.25)

        st.form_submit_button("Generate")

    rrt = CrazyflieRRT(robosys_grid, step_size=step_size, goal_bias = 0.25)

    if use_goal:
        output = rrt.generate(goal=goal_posn, max_iter=iterations)
        print(output)
    else:
        rrt.generate(max_iter=iterations)

    for node in rrt.tree.nodes:
        world.add_point(Point3d(*node), rrt.tree.nodes[node]["id"])

    for edge in rrt.tree.edges:
        world.add_edge(edge[0], edge[1])

    if use_goal:
        world.add_point(goal_posn, "Goal", True, color="red")

    world.update_figure()
    
    st.title("RRT Viz")
    st.plotly_chart(world.fig)