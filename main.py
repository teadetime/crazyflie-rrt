
import pickle
from occupany_grid import Point3d
from viz import build_robosys_world, viz_world

if __name__ == "__main__":
    visualization = build_robosys_world()

    with open('run.pkl', 'rb') as file:
        glbl_points = pickle.load(file)

    visualization.plot_trajectory(glbl_points, name="", text="")

    visualization.show_figure()
    visualization.save_figure()