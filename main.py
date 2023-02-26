
import pickle
from occupany_grid import Point3d
from viz import build_robosys_world, viz_world

if __name__ == "__main__":
    visualization = build_robosys_world()

    with open('track_actual.pkl', 'rb') as file:
        track_actual_pts = pickle.load(file)
    with open('track_desired.pkl', 'rb') as file:
        track_desiredl_pts = pickle.load(file)

    visualization.plot_trajectory(track_actual_pts, name="", text="", marker=dict(size=3, symbol="circle", color="red", opacity=0.4),
            line=dict(color="red", width=4),)
    
    visualization.plot_trajectory(track_desiredl_pts, name="", text="", marker=dict(size=3, symbol="circle", color="blue", opacity=0.4),
        line=dict(color="blue", width=4),)

    visualization.show_figure()
    visualization.save_figure()