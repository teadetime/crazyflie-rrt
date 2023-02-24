import numpy as np
import sys

from occupany_grid import OccupanyGrid3d, Point3d
from viz import viz_world
from rrt import CrazyflieRRT

import streamlit as st

import networkx as nx

if __name__ == "__main__":
    st.set_page_config(layout="wide")

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
        Point3d(0, 20, 0), Point3d(60, 40, 60)
    )  # Measurements in CM relative to origin
    robosys_grid.add_rectangles(Point3d(-30, -60, 0), Point3d(0, -20, 90))
    robosys_grid.add_rectangles(Point3d(0, -60, 40), Point3d(240, -20, 90))
    robosys_grid.add_rectangles(Point3d(60, -60, 0), Point3d(240, -20, 90))

    world = viz_world(robosys_grid)

    world.add_omap_to_fig()

    with st.form("sim_params"):
        step_size = st.slider("Step size (cm)", 1, 50, 10)
        iterations = st.slider("Iterations", 10, 10000, 10000)
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

    init_state = Point3d(20, 60, 10)
    rrt = CrazyflieRRT(robosys_grid, init_state, step_size=step_size, goal_bias=0.25)
    generated_path = rrt.generate(goal=goal_posn, max_iter=iterations)
    relaxed = rrt.relax_path(generated_path)

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
