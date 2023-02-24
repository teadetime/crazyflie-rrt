import numpy as np
import sys

from occupany_grid import OccupanyGrid3d, Point3d
from viz import viz_world


import logging
import time
from threading import Timer

import crazyflie.cflib.crtp
from crazyflie.cflib.crazyflie import Crazyflie
from crazyflie.cflib.crazyflie.log import LogConfig
from crazyflie.cflib.utils import uri_helper


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
        Point3d(0, 20, 0), Point3d(60, 40, 5)
    )  # Measurements in CM relative to origin
    robosys_grid.add_rectangles(Point3d(-30, -60, 0), Point3d(190, -20, 34))

    world = viz_world(robosys_grid)

    world.add_omap_to_fig()
    world.add_edge(Point3d(0, 0, 0), Point3d(30, 10, 60), end_name="Some point")
    world.add_point(Point3d(0, 0, 0), "Origin", True, "red")
    world.show_figure()
