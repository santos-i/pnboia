from .dash_class import Dash
from dash import html, dcc
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc

from .position import positionContent
from .wind import windContent
from .wave import waveContent
from .temperature import temperatureContent


app_layout = dbc.Container(
    [
        html.Div([
        html.H1('Alcatrazes'),
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
        routes_pathname_prefix="/alcatrazes/",
        external_stylesheets=[dbc.themes.BOOTSTRAP],
    )
    dash_app.layout = app_layout
    

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