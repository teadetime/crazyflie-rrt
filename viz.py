"""Simulator/Visualizer for outputs of RRT algorithm"""

from tkinter import Text
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import plotly.graph_objects as go

from occupany_grid import OccupanyGrid3d, Point3d


class viz_world():
    def __init__(self, omap: OccupanyGrid3d):
        self.omap = omap


if __name__ == "__main__":
    # The Robosys Environment
    origin = Point3d(
        200, 100, 0
    )  # Bottom Left corner of grid is 2 meters to the left (x) and 1m negative y
    grid_width = 100  # 5 meters wide (x)
    grid_depth = 60  # 3 meters tall (y)
    grid_height = 40  # 2 meters tall (z)
    robosys_grid = OccupanyGrid3d(
        grid_width, grid_depth, grid_height, origin, cell_size=5
    )
    robosys_grid.add_rectangles(
        Point3d(0, 20, 0), Point3d(200, 40, 60)
    )  # Measurements in CM relative to origin
    robosys_grid.add_rectangles(Point3d(-30,-60,0), Point3d(170, -20, 40))

    axes_shape = list(robosys_grid.map.shape)

    # Create Data
    data = robosys_grid.map

    # Convert Plot coorinates to world coordinates
    plots = np.array(data.nonzero()).transpose()
    adj = (plots*robosys_grid.cell_size - robosys_grid.origin).transpose()

    # Get max 
    min = -np.array(robosys_grid.origin)
    max = np.array(robosys_grid.map.shape) * robosys_grid.cell_size - robosys_grid.origin

    fig = go.Figure(
        data=[
            go.Scatter3d(
                x=adj[0],
                y=adj[1],
                z=adj[2],
                opacity=1,
                mode="markers",
                marker=dict(
                    size=5,
                    symbol="square",  # ['circle', 'circle-open', 'cross', 'diamond','diamond-open', 'square', 'square-open', 'x']
                    # color=plots[0],                # set color to an array/list of desired values
                    # colorscale='Viridis',   # choose a colorscale
                    opacity=0.25,
                ),
                name="Obstacle Map"
            ),
            go.Scatter3d(
                x=[0.],
                y=[0.],
                z=[0.],
                opacity=1,
                mode="markers",
                marker=dict(
                    size=5,
                    symbol="circle",  # ['circle', 'circle-open', 'cross', 'diamond','diamond-open', 'square', 'square-open', 'x']
                    color='black',                # set color to an array/list of desired values
                    # colorscale='Viridis',   # choose a colorscale
                ),
                name="Origin"
            ),
                        go.Scatter3d(
                x=[0.],
                y=[0.],
                z=[0.],
                opacity=1,
                mode="markers+text",
                text=["Origin"],
                textposition="top center",
                marker=dict(
                    size=5,
                    symbol="circle",  # ['circle', 'circle-open', 'cross', 'diamond','diamond-open', 'square', 'square-open', 'x']
                    color='black',                # set color to an array/list of desired values
                    # colorscale='Viridis',   # choose a colorscale
                ),
                showlegend=False
            ),
        ]
    )
    fig.update_layout(
        scene=dict(
            camera = dict(eye=dict(x=0., y=-0.01, z=1)),
            xaxis=dict(
                nticks=robosys_grid.map.shape[0],
                range=[min[0], max[0]],
            ),
            yaxis=dict(
                nticks=robosys_grid.map.shape[1],
                range=[min[1], max[1]],
            ),
            zaxis=dict(
                nticks=robosys_grid.map.shape[2],
                range=[min[2], max[2]],
            ),
        ),
        margin=dict(r=5, l=5, b=5, t=5),
    )
    fig.show()
    # More work here: https://plotly.com/python/3d-axes/