from dash import Dash, html, dcc
import dash
import dash_bootstrap_components as dbc

external_stylesheets = [dbc.themes.FLATLY]

app = Dash(__name__, external_stylesheets=external_stylesheets, use_pages=True)

# pages = dash.page_registry.values()

# print(pages)

app.layout = html.Div([
	
    dbc.NavbarSimple(brand='LUMY PROTOTYPING / Topic Modeling'),
    html.Br(),
	dash.page_container
])

if __name__ == '__main__':
	app.run_server(debug=True)