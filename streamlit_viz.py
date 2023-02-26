from math import ceil
import pickle
import numpy as np
import sys

from occupany_grid import OccupanyGrid3d, Point3d
from viz import build_robosys_world, viz_world
from rrt import CrazyflieRRT

import streamlit as st
import networkx as nx

if __name__ == "__main__":
    default_goal_posn = [100.0, -80.0, 0.0]
    default_step_size = 20

    st.set_page_config(layout="wide")
    starting_pos = Point3d(0,0,0) # TODO: Make this a default, and add number boxes for defining startpoint in the form
    default_start_posn = [0, 0, 0]

    viz = build_robosys_world()
    viz.omap.add_floor_is_lava(Point3d(*default_start_posn), Point3d(*default_goal_posn), box=20)
    viz.add_omap_to_fig()
    rrt = CrazyflieRRT(viz.omap, step_size=default_step_size, goal_bias=0.25)

    with st.form("sim_params"):
        step_size = st.slider("Step size (cm)", 1, 50, 10)
        iterations = st.slider("Iterations", 10, 10000, 100)

        goal_posn = default_goal_posn
        start_posn = default_start_posn
        coord_name = ["X", "Y", "Z"]
        min_max = viz.omap.min_max
        for i, col in enumerate(st.columns(3)):
            with col:
                start_posn[i] = st.number_input(
                    f"Start: {coord_name[i]}",
                    float(min_max[0][i]),
                    float(min_max[1][i]),
                    float(start_posn[i]),
                )
                goal_posn[i] = st.number_input(
                    f"Goal: {coord_name[i]}",
                    float(min_max[0][i]),
                    float(min_max[1][i]),
                    float(goal_posn[i]),
                )
                
        start_posn = Point3d(*start_posn)
        goal_posn = Point3d(*goal_posn)
        goal_bias = st.slider("Goal bias", 0.0, 1.0, 0.25)

        generate_rrt = st.form_submit_button("Generate")

        if generate_rrt:
            with st.spinner("Generating path"):
                viz = build_robosys_world()
                viz.omap.add_floor_is_lava(start_posn, goal_posn, box=20)
                viz.add_omap_to_fig()
                rrt = CrazyflieRRT(viz.omap, step_size=default_step_size, goal_bias=0.25)
                generated_path = rrt.generate(start=start_posn, goal=goal_posn, max_iter=iterations)
        else:
            generated_path = []
    
    plot_entire_rrt = st.checkbox("Plot entire RRT", False)

    if generated_path == []:
        st.write("Path not yet generated")
    else:
        relaxed = rrt.relax_path(generated_path)
        
        with open(f'path_x_{start_posn.x}_y_{start_posn.y}_y_{start_posn.z}_to_x_{goal_posn.x}_y_{goal_posn.y}_y_{goal_posn.z}.pkl', 'wb') as file:
            pickle.dump(relaxed, file)

        # Plot Results
        viz.add_point(
            goal_posn,
            marker=dict(size=4, symbol="x", color="red", opacity=0.6),
            name="Goal",
            show_legend=True,
        )
        viz.plot_trajectory(
            generated_path,
            marker=dict(size=3, symbol="circle", color="red", opacity=0.4),
            line=dict(color="red", width=4),
            text=[],
            name="RRT Raw Trajectory",
        )
        viz.plot_trajectory(
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
            viz.add_point(
                Point3d(*node),
                marker=dict(size=2, symbol="circle", color="black", opacity=0.15),
            )  # , name=rrt.tree.nodes[node]["id"])
        for edge in rrt.tree.edges:
            viz.plot_trajectory(
                edge,
                marker=dict(size=2, symbol="circle", color="black", opacity=0.2),
                line=dict(color="black", width=1),
                text=[],
            )

    viz.update_figure()

    st.title("RRT Viz")
    viz.fig.update_layout(height=700)
    st.plotly_chart(viz.fig, use_container_width=True)
