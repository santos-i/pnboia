
from .dash_class import Dash
from dash import html, dcc
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc

from flask_login import login_required
from flask import session

from .position import positionContent
from .wind import windContent
from .wave import waveContent
from .temperature import temperatureContent


app_layout = dbc.Container(
    [
        html.Div([
        html.H1('Alcatrazes'),
        html.H1(id='userdiv'),
        html.H1(id='userdiv2', children='xxxx'),
        html.A("Logout", href='logout', target="_blank", style={'position':'absolute', 'right':30, 'top':20}),
        ]),
                html.Div(
                    [
                        dbc.Tabs(
                            [
                                dbc.Tab(tab_id='position', label="Position"),
                                dbc.Tab(tab_id='wind', label="Wind"),
                                dbc.Tab(tab_id='wave', label="Wave"),
                                dbc.Tab(tab_id='temperature', label="Temperature"),
                            ],
                            id ='tabs',
                            active_tab='wind',
                        ),   
                        html.Div(id='content'),
                    ],
                ),
    ],
    fluid=True,
)


def init_app(server): #server = app Flask
    dash_app = Dash(
        server=server,
        routes_pathname_prefix='/dash_boia/',
        external_stylesheets=[dbc.themes.BOOTSTRAP],
    )
    dash_app.layout = app_layout
    

    @dash_app.callback(
    Output('user-div', 'children'),
    [Input('user-div2', 'children')])
    def update_intervalCurrentTime(children):
        return session.get('username', None)
    
    for view_func in dash_app.server.view_functions:
        if view_func.startswith('/dash_boia/'):
            dash_app.server.view_functions[view_func] = login_required(dash_app.server.view_functions[view_func])

    @dash_app.callback(Output("content", "children"), [Input("tabs", "active_tab")])
    def render_content(tab):
        if tab == 'position':
            position = positionContent()
            return position

        elif tab == 'wind':
            wind = windContent()
            return wind

        elif tab == 'wave':
            wave = waveContent()
            return wave
                
        elif tab == 'temperature':
            temperature = temperatureContent()
            return temperature


        return dash_app.server


if __name__ == "__main__":
    app = Dash(__name__)
    app.run_server(debug=True)