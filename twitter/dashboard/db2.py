import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)

app = Dash(__name__)

# App layout
app.layout = html.Div([

    html.H1("CDFW Dashboard", style={'text-align': 'center'}),

    dcc.Dropdown(id="slct_month",
                 options=[
                     {"label": "2015", "value": 2015},
                     {"label": "2016", "value": 2016},
                     {"label": "2017", "value": 2017},
                     {"label": "2018", "value": 2018}],
                 multi=False,
                 value=2015,
                 style={'width': "40%"}
                 ),

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='sent_analysis', figure={})

])

@app.callback(
    [Output(component_id='sent_analysis', component_property='figure')],
    [Input(component_id='slct_month', component_property='value')]
)
def update_graph(month):

    file = '/Users/chandannayak/Projects/CDFW/CDFW/twitter/coyotes/data/all_queries_01.csv'
    df = pd.read_csv(file)
    sent = df.groupby(['date']).mean()
    sent = sent.reset_index()

    # Plotly Express
    fig = px.line(sent, x="date",
                        y="compound_sent_score",
                        title='Sentiment Score over time')
    
    return [fig]

if __name__ == '__main__':
    app.run_server(debug=True,host = '127.0.0.1')