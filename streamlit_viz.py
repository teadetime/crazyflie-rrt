from math import ceil
import numpy as np
import sys

from occupany_grid import OccupanyGrid3d, Point3d
from viz import viz_world
from rrt import CrazyflieRRT

import streamlit as st

import networkx as nx

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    glbl_origin = Point3d(
            90.8, 90.8, 0
        )  # Bottom Left corner of grid is 35.75 inches in from corner (x) and y
    init_state = Point3d(0, 0, 0) # Starting spot of the drone
    cell_size = 5
    grid_width = int(ceil(300.4 / cell_size))  # 118.25 inches meters wide (x)
    grid_depth = int(ceil(211 / cell_size))  # 83 inches meters deep (y)
    grid_height = int(ceil(200 / cell_size))  # 2 meters tall (z)

    if grid_width % 2 == 1:
        grid_width += 1
    if grid_depth % 2 == 1:
        grid_depth += 1
    if grid_height % 2 == 1:
        grid_height += 1

    robosys_grid = OccupanyGrid3d(
        grid_width, grid_depth, grid_height, glbl_origin, cell_size=cell_size
    )

    robosys_grid.add_rectangles(Point3d(0, 30, 0), Point3d(122, 60.5, 62.3))
    robosys_grid.add_rectangles(Point3d(0, -60.5, 0), Point3d(122, -30, 62.3))
    robosys_grid.add_rectangles(Point3d(0, -60.5, 62.3), Point3d(35, -35, 90))


    world = viz_world(robosys_grid)

    world.add_omap_to_fig()

    with st.form("sim_params"):
        step_size = st.slider("Step size (cm)", 1, 50, 10)
        iterations = st.slider("Iterations", 10, 10000, 2000)
        plot_entire_rrt = st.checkbox("Plot entire RRT", False)

        goal_posn = [100.0, -90.0, 25.0]
        coord_name = ["X", "Y", "Z"]
        min_max = robosys_grid.min_max
        for i, col in enumerate(st.columns(3)):
            with col:
                goal_posn[i] = st.number_input(
                    coord_name[i],
                    float(min_max[0][i]),
                    float(min_max[1][i]),
                    float(goal_posn[i]),
                )
        goal_posn = Point3d(*goal_posn)

        goal_bias = st.slider("Goal bias", 0.0, 1.0, 0.25)

        st.form_submit_button("Generate")

    rrt = CrazyflieRRT(robosys_grid, init_state, step_size=step_size, goal_bias=0.25)
    generated_path = rrt.generate(goal=goal_posn, max_iter=iterations)
    relaxed = rrt.relax_path(generated_path)
    print(relaxed)
    # Plot Results
    world.add_point(
        goal_posn,
        marker=dict(size=4, symbol="x", color="red", opacity=0.6),
        name="Goal",
        show_legend=True,
    )
    world.plot_trajectory(
        generated_path,
        marker=dict(size=3, symbol="circle", color="red", opacity=0.4),
        line=dict(color="red", width=4),
        text=[],
        name="RRT Raw Trajectory",
    )
    world.plot_trajectory(
        relaxed,
        marker=dict(
            size=4,
            symbol="circle",
            color="blue",
            opacity=0.7,
        ),
        line=dict(color="blue", width=7),
        name="Relaxed Trajectory",
    )

    if plot_entire_rrt:
        # Printing the entire graph
        for node in rrt.tree.nodes:
            world.add_point(
                Point3d(*node),
                marker=dict(size=2, symbol="circle", color="black", opacity=0.15),
            )  # , name=rrt.tree.nodes[node]["id"])
        for edge in rrt.tree.edges:
            world.plot_trajectory(
                edge,
                marker=dict(size=2, symbol="circle", color="black", opacity=0.2),
                line=dict(color="black", width=1),
                text=[],
            )

    world.update_figure()

    st.title("RRT Viz")
    st.plotly_chart(world.fig)
