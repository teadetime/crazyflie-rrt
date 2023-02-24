from math import ceil
import numpy as np
import sys

from occupany_grid import OccupanyGrid3d, Point3d
from viz import viz_world


import logging
import time
from threading import Timer

sys.path.append("crazyflie")
import crazyflie.cflib.crtp
from crazyflie.cflib.crazyflie import Crazyflie
from crazyflie.cflib.crazyflie.log import LogConfig
from crazyflie.cflib.utils import uri_helper


if __name__ == "__main__":
    # The Robosys Environment
    origin = Point3d(
        90.8, 90.8, 0
    )  # Bottom Left corner of grid is 35.75 inches in from corner (x) and y
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
        grid_width, grid_depth, grid_height, origin, cell_size=cell_size
    )

    robosys_grid.add_rectangles(Point3d(0, 30, 0), Point3d(122, 60.5, 62.3))
    robosys_grid.add_rectangles(Point3d(0, -60.5, 0), Point3d(122, -30, 62.3))
    robosys_grid.add_rectangles(Point3d(0, -60.5, 62.3), Point3d(35, -35, 90))

    world = viz_world(robosys_grid)
    world.add_omap_to_fig()

    world.add_point(
        Point3d(0, 0, 0),
        marker=dict(size=4, symbol="x", color="red", opacity=0.6),
        name="Origin",
        show_legend=True,
    )
    world.show_figure()
