"""Simulator/Visualizer for outputs of RRT algorithm"""

from tkinter import Text
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

from occupany_grid import OccupanyGrid2d, OccupanyGrid3d, Point3d
 
def plot_omap3d(Omap: OccupanyGrid2d):
    axes = omap.size



if __name__ == "__main__":
    # The Robosys Environment
    origin = Point3d(200,100, 0) # Bottom Left corner of grid is 2 meters to the left (x) and 1m negative y
    grid_width = 100 # 5 meters wide (x)
    grid_depth = 60 # 3 meters tall (y)
    grid_height = 40 # 2 meters tall (z)
    robosys_grid = OccupanyGrid3d(grid_width, grid_depth, grid_height, origin, cell_size=5)
    robosys_grid.add_rectangles(Point3d(0,20,0), Point3d(200, 40, 60)) # Measurements in CM relative to origin
    robosys_grid.add_rectangles(Point3d(-30,-60,0), Point3d(170, -20, 40))

    axes_shape = list(robosys_grid.map.shape)
    
    # Create Data
    data = robosys_grid.map
    
    # Control Transparency
    alpha = 0.2
    
    # Control colour
    colors = np.empty(axes_shape + [4], dtype=np.float32)
    
    colors[:] = [1, 0, 0, alpha]  # red
    
    # Plot figure
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_box_aspect(axes_shape)  # aspect ratio is 1:1:1 in data space
    ax.set_xlabel('X', fontsize=20)
    ax.set_ylabel('Y')
    
    # Voxels is used to customizations of the
    # sizes, positions and colors.
    origin_cell = robosys_grid.glbl_pt_to_cell(Point3d(0,0,0), robosys_grid.cell_size, Point3d(robosys_grid.origin.x, robosys_grid.origin.y, robosys_grid.origin.z))

    ax.scatter(origin_cell[0], origin_cell[1], origin_cell[2], s=8, marker='^')

    filled = np.transpose(data.nonzero())
    print(filled)
    ax.voxels(data, facecolors=colors)


    # Adjust axes to work witht he grid
    x_labels = (ax.get_xticks()*robosys_grid.cell_size-robosys_grid.origin.x)/100
    y_labels = (ax.get_yticks()*robosys_grid.cell_size-robosys_grid.origin.y)/100
    z_labels = (ax.get_zticks()*robosys_grid.cell_size-robosys_grid.origin.z)/100
    ax.set_xticklabels(x_labels)
    ax.set_yticklabels(y_labels)
    ax.set_zticklabels(z_labels)
    
    plt.show()


    # ## Uncomment below for plotly
    # import plotly.graph_objects as go
    # plots = data.nonzero()

    # fig = go.Figure(data=[go.Scatter3d(x=plots[0], y=plots[1], z=plots[2], opacity=.05,
    #                                 mode='markers')])
    # fig.update_layout(
    #     scene = dict(
    #         xaxis = dict(nticks=4, range=[0,data.shape[0]],),
    #                     yaxis = dict(nticks=4, range=[0,data.shape[1]],),
    #                     zaxis = dict(nticks=4, range=[0,data.shape[2]],),),
    #     margin=dict(r=20, l=10, b=10, t=10))
    # # fig.update_layout(scene_aspectmode='cube')
    # fig.show()
    # # More work here: https://plotly.com/python/3d-axes/