import dash
from dash import html

dash.register_page(__name__, path='/')

layout = html.Div(className="home-header", children=[
    # html.H1([
    #     html.A(id='text-box', children='Data Mining Techniques Group 5', href="/")
    # ]),
    html.Div(className="text-box", children=[
        html.H2([
            html.A(id='text-box', children='Data Mining Techniques Group 5', href="/")
        ]),
        html.Div(className="home-links", children=[
            html.Ul([
                html.Li([
                    html.A(href="./flow", className="home-button", children="Traffic Flow Map")
                ]),
                html.Li([
                    html.A(href="./incidents", className="home-button", children="Traffic Incident Map")
                ])
            ])
        ]),

        html.P("Use any of the navigation links to continue.")
    ])
    
])