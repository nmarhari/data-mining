import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc

# pip install -r requirements.txt

app = Dash(__name__, use_pages=True)

external_stylesheets = [
    'https://use.fontawesome.com/releases/v5.7.1/css/all.css'
]

app.layout = html.Div([

    # html.H1([
    #     html.A(id='top-text', children='Data Mining Techniques Group 5', href="/")
    # ]),
    dash.page_container
])

if __name__ == '__main__':
    app.run()