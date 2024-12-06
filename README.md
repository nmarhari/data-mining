# data-mining
GitHub repository for the Data Mining Techniques group project (Group #5).

This uses [HERE Technolgies Traffic API V7](https://www.here.com/docs/bundle/traffic-api-v7-api-reference/page/index.html) to gather traffic data and [scikit-learn](https://scikit-learn.org/stable/) to apply clustering. Once data is gathered and clustered, [folium](https://pypi.org/project/folium/) and [Dash](https://dash.plotly.com/) are used to display results to the user.

## Requirements:
- HERE Technologies API Key [Obtain Here](https://www.here.com/docs/bundle/identity-and-access-management-developer-guide/page/README.html)
- Python 3.0 +

## To Run:
Note that some commands may differ based on operating system or version of software.
In the `/functions` directory of the project:
- Create a file `.env` and populate with `HERE_API_KEY='your-key'`

In root directory of the project:
- Run command: `py -m pip install -r requirements.txt`
- Run command: `py app.py`
