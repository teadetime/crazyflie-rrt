"""Occupany Grid and Associated functions"""


from collections import namedtuple
from typing import Sequence
import numpy as np

# Point2d = namedtuple("Point", "x y")
Point3d = namedtuple("Point3", "x y z")

Pose2d = namedtuple("Pose2d", "x y h")


# class OccupanyGrid2d:
#     """Occupancy Grid written to use cm as units."""

#     def __init__(
#         self, grid_width: int, grid_height: int, origin: Point2d, cell_size=5
#     ) -> None:
#         if (
#             grid_width % 2 == 1
#             or grid_height % 2 == 1
#             or grid_height <= 1
#             or grid_height <= 1
#         ):
#             raise ValueError("Occupancy grid should be even shaped")
#         if origin.x >= cell_size * grid_width or origin.y >= cell_size * grid_height:
#             raise ValueError("Specify an origin within the Occupancy Grid")
#         self.origin = origin  # in CM not in cells
#         self.grid_width = grid_width
#         self.grid_height = grid_height

#         self.cell_size = cell_size

#         # map_width_cells = 1 + math.ceil((upper_right.x-cell_size)/self.cell_size) + math.ceil((bottom_left.x+cell_size)/self.cell_size)
#         # map_height_cells = 1 + math.ceil((upper_right.y-cell_size)/self.cell_size)
#         self.map = np.zeros((self.grid_width, grid_height), dtype=bool)

#     @staticmethod
#     def glbl_pt_to_cell(
#         origin: Point2d, cell_size: float, point: Point2d
#     ) -> tuple[int, int]:
#         return (
#             math.floor((point.x + origin.x) / cell_size),
#             math.floor((point.y + origin.y) / cell_size),
#         )

#     def add_points_global(self, points: Sequence[namedtuple]):
#         """Add points in the global frame (relative to origin) to the occupancy_grid."""
#         # TODO: Raise error on too big of query

#         cells = [self.glbl_pt_to_cell(self.origin, self.cell_size, pt) for pt in points]
#         for i in cells:
#             self.map[i] = True
#         # TODO: (COuldnt get this wokring vectorized :(

#     def get_points_global(self, points: Sequence[namedtuple]):
#         """Take Points in the global Mpa frame and return if they are occupied"""
#         return [
#             self.map[self.glbl_pt_to_cell(self.origin, self.cell_size, pt)]
#             for pt in points
#         ]

#     def get_points_rel(pose: Pose2d, points: Sequence[namedtuple]):
#         # TODO: Matrix multiplication for rotation and transformation and then query points
#         raise NotImplementedError

#     def set_points_rel(pose: Pose2d, points: Sequence[namedtuple]):
#         # TODO: Matrix multiplication for rotation and transformation and then set points
#         raise NotImplementedError

#     def add_rectangles(self, bottom_left_point: Point2d, top_right_point: Point2d):
#         """Helper to add rows in our environment. Positioned on our gloabl coordinate"""
#         bottom_left_cell = self.glbl_pt_to_cell(
#             self.origin, self.cell_size, bottom_left_point
#         )
#         top_right_cell = self.glbl_pt_to_cell(
#             self.origin, self.cell_size, top_right_point
#         )
#         for x in range(bottom_left_cell[0], top_right_cell[0] + 1):
#             for y in range(bottom_left_cell[1], top_right_cell[1] + 1):
#                 self.map[(x, y)] = True


class OccupanyGrid3d:
    """Occupancy Grid written to use cm as units."""

    def __init__(
        self,
        grid_width: int,
        grid_depth: int,
        grid_height: int,
        origin: Point3d,
        cell_size=5,
    ) -> None:
        if (
            grid_width % 2 == 1
            or grid_depth % 2 == 1
            or grid_height % 2 == 1
            or grid_depth <= 1
            or grid_depth <= 1
            or grid_height <= 1
        ):
            raise ValueError("Occupancy grid should be even shaped")
        if (
            origin.x >= cell_size * grid_width
            or origin.y >= cell_size * grid_depth
            or origin.z >= cell_size * grid_height
        ):
            raise ValueError("Specify an origin within the Occupancy Grid")
        self.origin = origin  # in CM not in cells

        self.cell_size = cell_size
        self.map = np.zeros((grid_width, grid_depth, grid_height), dtype=bool)

    @staticmethod
    def cells_to_glbl_pts(cells: np.array, cell_size: float, origin: Point3d):
        """Takes a 3 by X array of cell indicies."""
        return (cells * cell_size - origin).transpose()

    @staticmethod
    def glbl_pts_to_cells(
        origin: Point3d, cell_size: float, points: np.ndarray
    ) -> np.ndarray:
        transformed = points + np.array(origin)
        scaled = np.floor(transformed / cell_size).astype("int")
        return scaled

    @property
    def min_max(self):
        return (
            -np.array(self.origin),
            np.array(self.map.shape) * self.cell_size - self.origin,
        )

    def obstacles_in_global(self) -> np.array:
        """Return Obstacle map in Global Coordinates (cms)"""
        obstacles = np.array(self.map.nonzero()).transpose()
        return OccupanyGrid3d.cells_to_glbl_pts(obstacles, self.cell_size, self.origin)

    def add_points_global(self, points: Sequence[namedtuple]):
        """Add points in the global frame (relative to origin) to the occupancy_grid."""
        # TODO: Raise error on too big of query
        cells = OccupanyGrid3d.glbl_pts_to_cells(self.origin, self.cell_size, points)
        transposed = cells.transpose()
        self.map[(transposed[0], transposed[1], transposed[2])] = True

    def get_points_global(self, points: np.ndarray):
        """Take Points in the global Mpa frame and return if they are occupied"""
        cells = OccupanyGrid3d.glbl_pts_to_cells(self.origin, self.cell_size, points)
        cells = np.clip(cells, [0, 0, 0], np.array(self.map.shape) - 1)
        transposed = cells.transpose()
        return self.map[(transposed[0], transposed[1], transposed[2])]

    def get_points_rel(pose: Pose2d, points: Sequence[namedtuple]):
        # TODO: Matrix multiplication for rotation and transformation and then query points
        raise NotImplementedError

    def set_points_rel(pose: Pose2d, points: Sequence[namedtuple]):
        # TODO: Matrix multiplication for rotation and transformation and then set points
        raise NotImplementedError

    def add_rectangles(self, bottom_left_point: Point3d, top_right_point: Point3d):
        """Helper to add rows in our environment. Positioned on our gloabl coordinate"""
        # TODO: Refactor to use linspace to then use numpy indexing
        # self.map[(range(bottom_left_cell[0], top_right_cell[0] + 1), range(bottom_left_cell[1], top_right_cell[1] + 1), range(bottom_left_cell[2], top_right_cell[2] + 1))]

        bottom_left_cell = OccupanyGrid3d.glbl_pts_to_cells(
            self.origin, self.cell_size, bottom_left_point
        )
        top_right_cell = OccupanyGrid3d.glbl_pts_to_cells(
            self.origin, self.cell_size, top_right_point
        )
        xs = range(bottom_left_cell[0], top_right_cell[0] + 1)
        ys = range(bottom_left_cell[1], top_right_cell[1] + 1)
        zs = range(bottom_left_cell[2], top_right_cell[2] + 1)

        for x in xs:
            for y in ys:
                for z in zs:
                    self.map[(x, y, z)] = True

    def check_line(
        self, start_pt: Point3d, end_pt: Point3d, bounding_box: list[Point3d]
    ):
        """Take in points in the global frame (ie. 0,0 is the origin)

        Args:
            start_pt (Point3d): _description_
            end_pt (Point3d): _description_

        Returns: True if there is no obstacle map collision
        """
        start_vec = np.array(start_pt)
        end_vec = np.array(end_pt)
        length = np.linalg.norm(end_vec - start_vec)
        num_pts = int(length / (self.cell_size / 4))
        if num_pts < 2:
            num_pts = 2

        points = np.linspace(start_vec, end_vec, num=num_pts, endpoint=True)
        points_list = np.concatenate([points + np.array(c) for c in bounding_box])
        return not np.any(self.get_points_global(points_list))

    def project(self, point: Point3d):
        yaw, pitch, roll = 0, 0, -30 * np.pi / 180
        r_yaw = np.array(
            [[np.cos(yaw), -np.sin(yaw), 0], [np.sin(yaw), np.cos(yaw), 0], [0, 0, 1]]
        )  # Rotation around z
        r_pitch = np.array(
            [
                [np.cos(pitch), 0, np.sin(pitch)],
                [0, 1, 0],
                [-np.sin(pitch), 0, np.cos(pitch)],
            ]
        )  # Rotation around y
        r_roll = np.array(
            [
                [1, 0, 0],
                [0, np.cos(roll), -np.sin(roll)],
                [0, np.sin(roll), np.cos(roll)],
            ]
        )  # Rotation around x

        R = np.matmul(r_yaw, np.matmul(r_pitch, r_roll))

        pt = np.array(point)

        print(f"Rotaion: {R.shape}, POint: {pt.shape}")
        print(np.matmul(R, point))


if __name__ == "__main__":
    omap3d = OccupanyGrid3d(4, 6, 2, Point3d(15, 10, 0), 10)
    omap3d.add_rectangles(Point3d(0, 0, 0), Point3d(10, 10, 19))

    quad_corners = [
        Point3d(0, 0, 0),
        Point3d(5, 5, 0),
        Point3d(-5, 5, 0),
        Point3d(5, -5, 0),
        Point3d(-5, -5, 0),
    ]
    valid_line = omap3d.check_line(Point3d(0, 0, 0), Point3d(11, 21, 0), quad_corners)
    # print(valid_line)
    # omap3d.project((1,2,0))

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
    valid_line = robosys_grid.check_line(
        Point3d(0, 0, 0),
        Point3d(x=103.00174191628984, y=-91.5617546731021, z=2.259940872447486),
        quad_corners,
    )
    print(valid_line)

    # Some gut checks here:
    # print(omap.map)
    # omap.add_points_global([Point2d(10,10), Point2d(0,0) ])
    # print(omap.map)
    # query = omap.get_points_global([Point2d(10,10), Point2d(0,0) ])
    # print(query)

    # omap.add_rectangles(Point2d(0,0), Point2d(10,10))
    # print(omap.map)
