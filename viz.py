"""Simulator/Visualizer for outputs of RRT algorithm"""
from math import ceil
import numpy as np
import plotly.graph_objects as go
import dash
from dash import dcc, html
import plotly
from dash.dependencies import Input, Output, State

from occupany_grid import OccupanyGrid3d, Point3d


# CFLIB imports
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.utils import uri_helper

class viz_world:
    def __init__(self, omap: OccupanyGrid3d):
        self.omap = omap
        self.fig = go.Figure()
        self.fig["layout"]["uirevision"] = 42

    def add_omap_to_fig(self):
        obstacles = self.omap.obstacles_in_global()
        omap_plot = go.Scatter3d(
            x=obstacles[0],
            y=obstacles[1],
            z=obstacles[2],
            opacity=1,
            mode="markers",
            marker=dict(
                size=5,
                symbol="square",  # ['circle', 'circle-open', 'cross', 'diamond','diamond-open', 'square', 'square-open', 'x']
                # color=plots[0],                # set color to an array/list of desired values
                # colorscale='Viridis',   # choose a colorscale
                opacity=0.25,
            ),
            name="Obstacle Map",
        )
        self.fig.add_trace(omap_plot)

    def add_point(
        self,
        point: Point3d,
        marker: dict | None = None,
        name: str | None = None,
        show_legend=False,
    ):
        if marker is None:
            marker = dict(
                size=5,
                symbol="circle",
                color="black",
                opacity=0.25,
            )
        plotly_point = go.Scatter3d(
            x=[point.x],
            y=[point.y],
            z=[point.z],
            opacity=1,
            mode="markers",
            marker=marker,
            name=name,
            showlegend=show_legend,
        )
        self.fig.add_trace(plotly_point)

    def plot_trajectory(
        self,
        points: list,
        marker: dict | None = None,
        line: dict | None = None,
        text: list[int] = None,
        name: str = None,
    ) -> None:
        """Plots a list of nodes."""
        if marker is None:
            marker = dict(
                size=2,
                symbol="circle",
                color="black",
                opacity=0.25,
            )
        if text is None:
            nums = range(len(points))
            text = [str(n) for n in nums]
        if line is None:
            line = dict(
                color="black",
                width=1,
            )
        x = np.asarray(points).transpose()[0]
        y = np.asarray(points).transpose()[1]
        z = np.asarray(points).transpose()[2]
        trajectory = go.Scatter3d(
            x=x,
            y=y,
            z=z,
            opacity=1,
            marker=marker,
            mode="markers+text+lines",
            text=text,
            textposition="top center",
            line=line,
            showlegend=(name is not None),
            name=name,
        )
        self.fig.add_trace(trajectory)

    def update_figure(self):
        min, max = self.omap.min_max
        self.fig.update_layout(
            scene=dict(
                camera=dict(
                    eye=dict(x=0.0, y=-0.01, z=10000)
                ),  # Weirdly tuned for aspect ration, should consider a param of the omap
                xaxis=dict(
                    nticks=self.omap.map.shape[0],
                    range=[min[0], max[0]],
                ),
                yaxis=dict(
                    nticks=self.omap.map.shape[1],
                    range=[min[1], max[1]],
                ),
                zaxis=dict(
                    nticks=self.omap.map.shape[2],
                    range=[min[2], max[2]],
                ),
                aspectratio=dict(
                    x=self.omap.map.shape[0],
                    y=self.omap.map.shape[1],
                    z=self.omap.map.shape[2],
                ),
            ),
            margin=dict(r=5, l=5, b=5, t=5),
        )

    def show_figure(self):
        self.update_figure()
        self.fig.show()

    def save_figure(self):
        self.fig.write_html("plotly.html")

def build_robosys_world() -> viz_world:
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
    world.update_figure()
    return world
