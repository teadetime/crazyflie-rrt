"""Simulator/Visualizer for outputs of RRT algorithm"""
import plotly.graph_objects as go
import dash
from dash import dcc, html
import plotly
from dash.dependencies import Input, Output, State

from occupany_grid import OccupanyGrid3d, Point3d


class viz_world:
    def __init__(self, omap: OccupanyGrid3d):
        self.omap = omap
        self.fig = go.Figure()
        self.fig['layout']['uirevision'] = 42

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

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div([
        html.H4('TERRA Satellite Live Feed'),
        html.Div(id='live-update-text'),
        html.Button(id='start-stop-button', title='Start/Stop'),
        dcc.Input(
            id="input_speed",
            type="number",
            min=100,
            max=1000,
            placeholder="Hertz",
            value=1000
        ),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            #interval="hertz", # in milliseconds
            n_intervals=0
        )
    ])
)

@app.callback(
    Output('interval-component', 'interval'),
    [Input("input_speed", "value")],
    [State('interval-component', 'interval')],
)
def callback_func_set_interval(value, interval):
    return value

@app.callback(Output('live-update-text', 'children'),
              Input('interval-component', 'n_intervals'))
def update_metrics(n):
    lon, lat, alt = ("40", "30", "20")
    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.Span(f'{n}', style=style),
        html.Span('Latitude: ', style=style),
        html.Span('Altitude: ', style=style)
    ]


@app.callback(
    Output('interval-component', 'disabled'),
    [Input('start-stop-button', 'n_clicks')],
    [State('interval-component', 'disabled')],
)
def callback_func_start_stop_interval(button_clicks, disabled_state):
    if button_clicks is not None and button_clicks > 0:
        return not disabled_state
    else:
        return disabled_state


# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
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
    world.add_point(Point3d(0, 0, n*1), "Origin", True, "red")
    return world.fig


if __name__ == '__main__':

    app.run_server(debug=True)