"""Simulator/Visualizer for outputs of RRT algorithm"""
import plotly.graph_objects as go

from occupany_grid import OccupanyGrid3d, Point3d


class viz_world:
    def __init__(self, omap: OccupanyGrid3d):
        self.omap = omap
        self.fig = go.Figure()

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
        self, point: Point3d, name: str | None, show_legend=False, color="black"
    ):
        plotly_point = go.Scatter3d(
            x=[point.x],
            y=[point.y],
            z=[point.z],
            opacity=1,
            mode="markers",
            marker=dict(
                size=5,
                symbol="circle",  # ['circle', 'circle-open', 'cross', 'diamond','diamond-open', 'square', 'square-open', 'x']
                color=color,
                opacity=0.5,
            ),
            name=name,
            showlegend=show_legend,
        )
        self.fig.add_trace(plotly_point)

    def add_edge(self, start: Point3d, end: Point3d, start_name=None, end_name=None):
        plotly_edge = go.Scatter3d(
            x=[start.x, end.x],
            y=[start.y, end.y],
            z=[start.z, end.z],
            marker=dict(
                size=3,
                symbol="circle",  # ['circle', 'circle-open', 'cross', 'diamond','diamond-open', 'square', 'square-open', 'x']
                color="black",
                opacity=0.5,
            ),
            mode="markers+text+lines",
            text=[start_name, end_name],
            textposition="top center",
            line=dict(
                color="black",
                width=3,
            ),
            showlegend=False,
        )
        self.fig.add_trace(plotly_edge)

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
