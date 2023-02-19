import numpy as np
import sys

from occupany_grid import Point2d, OccupanyGrid2d


if __name__ == "__main__":
    # The Robosys Environment
    origin = Point2d(
        200, 100
    )  # Bottom Left corner of grid is 2 meters to the left (x) and 1m negative y
    grid_width = 100  # 5 meters wide (x)
    grid_height = 60  # 3 meters tall (y)
    robosys_grid = OccupanyGrid2d(grid_width, grid_height, origin, cell_size=5)
    robosys_grid.add_rectangles(
        Point2d(0, 20), Point2d(200, 40)
    )  # Measurements in CM relative to origin
    robosys_grid.add_rectangles(Point2d(-30, -60), Point2d(170, -20))

    # COnfirmed that Objects have been added!
    np.set_printoptions(threshold=sys.maxsize)
    print(robosys_grid.map)
