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
                    html.A(href="./map", className="home-button", children="Map")
                ])
            ])
        ]),

        html.P("Use any of the navigation link(s) to continue.")
    ])
    
])