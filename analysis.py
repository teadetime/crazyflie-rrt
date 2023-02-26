from math import ceil
from threading import Thread
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

from viz import build_robosys_world, viz_world
visualization = build_robosys_world()


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div(
        [
            html.H4("TERRA Satellite Live Feed"),
            html.Div(id="live-update-text"),
            html.Button(id="start-stop-button", title="Start/Stop"),
            dcc.Input(
                id="input_speed",
                type="number",
                min=100,
                max=1000,
                placeholder="Hertz",
                value=1000,
            ),
            dcc.Graph(id="live-update-graph"),
            dcc.Interval(
                id="interval-component",
                # interval="hertz", # in milliseconds
                n_intervals=0,
            ),
        ]
    )
)


@app.callback(
    Output("interval-component", "interval"),
    [Input("input_speed", "value")],
    [State("interval-component", "interval")],
)
def callback_func_set_interval(value, interval):
    return value


@app.callback(
    Output("live-update-text", "children"), Input("interval-component", "n_intervals")
)
def update_metrics(n):
    lon, lat, alt = ("40", "30", "20")
    style = {"padding": "5px", "fontSize": "16px"}
    return [
        html.Span(f"{n}", style=style),
        html.Span("Latitude: ", style=style),
        html.Span("Altitude: ", style=style),
    ]


@app.callback(
    Output("interval-component", "disabled"),
    [Input("start-stop-button", "n_clicks")],
    [State("interval-component", "disabled")],
)
def callback_func_start_stop_interval(button_clicks, disabled_state):
    if button_clicks is not None and button_clicks > 0:
        return not disabled_state
    else:
        return disabled_state


# Multiple components can update everytime interval gets fired.
@app.callback(
    Output("live-update-graph", "figure"), Input("interval-component", "n_intervals")
)
def update_graph_live(n):
    return visualization.fig


# URI to the Crazyflie to connect to
uri = uri_helper.uri_from_env(default='radio://0/70/2M/E7E7E7E7E7')

# Change the sequence according to your setup
#             x    y    z  YAW
sequence = [
    (0.0, 0.0, 0.4, 0),
    (0.0, 0.0, 1.2, 0),
    (0.5, -0.5, 1.2, 0),
    (0.5, 0.5, 1.2, 0),
    (-0.5, 0.5, 1.2, 0),
    (-0.5, -0.5, 1.2, 0),
    (0.0, 0.0, 1.2, 0),
    (0.0, 0.0, 0.4, 0),
]

def wait_for_position_estimator(scf):
    print('Waiting for estimator to find position...')

    log_config = LogConfig(name='Kalman Variance', period_in_ms=500)
    log_config.add_variable('kalman.varPX', 'float')
    log_config.add_variable('kalman.varPY', 'float')
    log_config.add_variable('kalman.varPZ', 'float')

    var_y_history = [1000] * 10
    var_x_history = [1000] * 10
    var_z_history = [1000] * 10

    threshold = 0.001

    with SyncLogger(scf, log_config) as logger:
        for log_entry in logger:
            data = log_entry[1]

            var_x_history.append(data['kalman.varPX'])
            var_x_history.pop(0)
            var_y_history.append(data['kalman.varPY'])
            var_y_history.pop(0)
            var_z_history.append(data['kalman.varPZ'])
            var_z_history.pop(0)

            min_x = min(var_x_history)
            max_x = max(var_x_history)
            min_y = min(var_y_history)
            max_y = max(var_y_history)
            min_z = min(var_z_history)
            max_z = max(var_z_history)

            # print("{} {} {}".
            #       format(max_x - min_x, max_y - min_y, max_z - min_z))

            if (max_x - min_x) < threshold and (
                    max_y - min_y) < threshold and (
                    max_z - min_z) < threshold:
                break


def reset_estimator(scf):
    cf = scf.cf
    cf.param.set_value('kalman.resetEstimation', '1')
    time.sleep(0.1)
    cf.param.set_value('kalman.resetEstimation', '0')

    wait_for_position_estimator(cf)


def position_callback(timestamp, data, logconf):
    x = data['kalman.stateX']
    y = data['kalman.stateY']
    z = data['kalman.stateZ']
    print('pos: ({}, {}, {})'.format(x, y, z))
    visualization.add_point(Point3d(x*100,y*100,z*100), show_legend=True)


def start_position_printing(scf):
    log_conf = LogConfig(name='Position', period_in_ms=500)
    log_conf.add_variable('kalman.stateX', 'float')
    log_conf.add_variable('kalman.stateY', 'float')
    log_conf.add_variable('kalman.stateZ', 'float')

    scf.cf.log.add_config(log_conf)
    log_conf.data_received_cb.add_callback(position_callback)
    log_conf.start()


def run_sequence(scf, sequence):
    cf = scf.cf

    for position in sequence:
        print('Setting position {}'.format(position))
        for i in range(50):
            cf.commander.send_position_setpoint(position[0],
                                                position[1],
                                                position[2],
                                                position[3])
            time.sleep(0.1)

    cf.commander.send_stop_setpoint()
    # Make sure that the last packet leaves before the link is closed
    # since the message queue is not flushed before closing
    time.sleep(0.1)



def async_main_wrapper():
    """Not async Wrapper around async_main to run it as target function of Thread"""
    cflib.crtp.init_drivers()

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        reset_estimator(scf)
        start_position_printing(scf)
        run_sequence(scf, sequence)

if __name__ == "__main__":
    # run all async stuff in another thread
    th = Thread(target=async_main_wrapper)
    th.start()
    app.run_server(debug=True)
    th.join()
    