import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/')


select_existing = dbc.Col(
    html.Div(
        [
            html.H2("Select existing dataset"),
            html.Hr(className="my-2"),
            html.P(
                "Use a previously onboarded dataset to run the topic modeling pipeline."
            ),
            dbc.Button("Go", color="dark", outline=True, href='/tm_data_selection'),
        ],
        className="h-100 p-4 m-1 border rounded-3",
    ),
    md=6,
)

onboard_new = dbc.Col(
    html.Div(
        [
            html.H2("Onboard new data"),
            html.Hr(className="my-2"),
            html.P(
                "Add a new corpus to the data registry."
            ),
            dbc.Button("Go", color="dark", outline=True, href='/')
            
        ],
        className="h-100 p-4 m-1 border rounded-3",
    ),
    md=6,
)

home_selection = dbc.Row(
    [select_existing, onboard_new],
    className="align-items-md-stretch",
    style={"margin-left":"3%","margin-right":"3%" }
)

layout = html.Div(children=[
    home_selection
])

