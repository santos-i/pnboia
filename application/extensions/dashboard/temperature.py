from dash import html, dcc
import dash_bootstrap_components as dbc


def temperatureContent(): 
    return html.Div(
                    [
                        dbc.Card(
                            [
                                dcc.Graph(
                                    id="a-graph",
                                    hoverData={},
                                )
                            ],
                            style={'border':'#ffffff'},
                        ),
                        dbc.Card(
                            [
                                dcc.Slider(
                                    id="wind-slicer",
                                    min=100,
                                    max=200,
                                    value=150,
                                    step=None,
                                    marks={'ano': [x for x in range(100,200,20)] },
                                )
                            ],
                            className="pt-2",
                            style={'width':'85%','border':'#ffffff'},
                        ),
                    ],
                    style={'flex': 0.8,'border':'#ffffff'},
                ),