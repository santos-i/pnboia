from dash import html, dcc
import dash_bootstrap_components as dbc





def windContent():
        # PARA EXEMPLO DA WINDROSE
    import plotly.graph_objects as go
    import plotly.express as px
    df = px.data.wind()
    fig = go.Figure()
    fig = px.bar_polar(
                df, 
                # r=0, 
                theta="direction",
                color="strength",
                color_discrete_sequence= px.colors.sequential.Plasma_r,
                title='oi'
            )

    return html.Div(
            [
                # PLOT LINHA
                html.Div(
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
                            style={'padding-left':50,'width':'95%','border':'#ffffff'},
                        ),
                    ], style={'flex': 2,'border':'#ffffff'},
                ),
                # WINDROSE PLOT
                html.Div(
                    [
                        dbc.Card(
                            [
                                dcc.Graph(figure=fig,)
                            ],
                            style={'padding-top': 30,'border':'#ffffff'}
                        ),
                    ],
                    style={'flex': 1, 'padding-right':10,'border':'#ffffff'}
                ),
            ], style={'display': 'flex', 'flex-direction': 'row', 'border':'#ffffff'},
        )