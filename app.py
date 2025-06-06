# NOTES
# bootstrap-grid.css needed for card view
# 

from dash import Dash, dash_table, dcc, html, Input, Output, callback, State
from dash.exceptions import PreventUpdate
import numpy as np
import pandas as pd
from collections import OrderedDict
import dash_bootstrap_components as dbc
from dash import html
import plotly.graph_objs as go
import plotly.express as px
import os
import dash_bootstrap_templates 

data = pd.read_csv('./data/data.csv', keep_default_na=False)
df = pd.DataFrame(data)
df.drop(df.columns[df.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)
df = df.replace('', np.NaN)


app = Dash(__name__,
           external_stylesheets=[dbc.themes.BOOTSTRAP],
        #    assets_url_path='http://127.0.0.1:8050/assets',
           assets_folder='/Users/ewood/Documents/GitHub/HighlandDanceResults.github.io/assets/',
           title="Highland Dance Results",
           prevent_initial_callbacks=True)

def table_style_data_conditional(df_chosen):
    styles = [
        {"if": {"column_id": "Overall"}, "backgroundColor": "#f9f9f9"},
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': "#f9f9f9",
        },
        {
            'if': {'column_id': 'Name'},
            'textAlign': 'left'
        }
    ]

    return styles




DATA_TABLE_STYLE = {
    "style_data_conditional": table_style_data_conditional(dcc.Store(id='df_chosen', data=[])),
    "style_header": {
        "color": "black",
        "backgroundColor": "#E6E6E6",
        "fontWeight": "bold",
    }
}


### --- PAGE LAYOUT --- ###
navbar = html.Div(dbc.Card([
    dbc.CardHeader(
        html.Center(dcc.Markdown('''# Unofficial Highland Dance Results'''))
        ),
    ]),
                  style = {"margin-bottom": "0.3em"})


dropdown_labels = list(df['Year'].unique())

top_card = [
    dbc.CardHeader(html.B("Select Data")),
    dbc.CardBody([
        dcc.Markdown('''            
            Checkout [scotdance.app] (https://scotdance.app/#/competitions/), which also has a mobile app! My website originated as a passion project because some comps do not use the app.
            ''')
    ]),
    dbc.CardBody([
        dbc.Col([
            dbc.Row([
                dcc.Markdown('''**1) Choose Year**'''),
                dcc.Dropdown(dropdown_labels,
                             id= 'year_dropdown',
                             searchable=False,
                             optionHeight=50,
                             placeholder= 'Select Year'
                             )

            ]),
        ])]),
    dbc.CardBody([
        dbc.Col([
            dbc.Row([
                dcc.Markdown('''**2) Choose Competition**'''),
                dcc.Dropdown('',
                             id= 'comp_dropdown',
                             searchable=False,
                             optionHeight=50,
                             style = {'white-space': 'nowrap', 'position': 'initial'},
                            placeholder= 'Select Competition'
                ),
            ]),
        ])]),
    dbc.CardBody([
        dbc.Col([
            dbc.Row([
                dcc.Markdown('''**3) Choose Age Group**'''),
                dcc.Dropdown('',
                             id= 'age_dropdown',
                             searchable=False,
                             optionHeight=50,
                            placeholder= 'Select Age Group'
                ),
            ])
        ]),
        dbc.Row([
            dbc.CardBody([
                dbc.Button('Submit', id = 'submit_btn', outline=True, color = 'dark', className="me-1",
                            style = {"backgroundColor": "#e1eaf2"}
                ),
                dbc.Button('Reset', id = 'reset-btn', outline=True, color = 'dark', className="me-1",
                            style = {"backgroundColor": "#e1eaf2", "color":"red"}
                ),
            ], style={'textAlign': 'center'})
        ])
    ])
]

cards = dbc.Container(
    dbc.Col([
        dbc.Row(dbc.Card(top_card, style= {"padding": "0px"})
                , style = {"margin-bottom": "0.5em"}),
        dbc.Row(
            dbc.Card([
                dbc.CardHeader(html.B("Results")),
                dbc.CardBody([
                    dcc.Markdown('''Please select year, competition, and age group first.''', id = 'data-markdown'),
                    html.Center([
                        dcc.Markdown('', id = 'table_title'),
                        dash_table.DataTable(id = 'table',
                            style_as_list_view=True,
                            sort_action = 'native',
                            style_data_conditional = DATA_TABLE_STYLE.get("style_data_conditional"),
                            style_header=DATA_TABLE_STYLE.get("style_header"),
                            style_cell = {'textAlign': 'center',
                                          'font-family':'sans-serif'},
                            style_table={'overflowX': 'auto',
                                'minWidth': '90vw', 'width': '90vw', 'maxWidth': '90vw'
                                        },
                            fixed_columns={'headers': True, 'data': 1},
                    )]),
                ]),
                dbc.CardBody([
                    html.Center(dcc.Markdown('', id = 'graph_title')),
                    dcc.Graph(id = 'graph',
                        figure={
                            'data': [],
                            'layout': go.Layout(                                
                                xaxis =  {'showgrid': False, 'zeroline': False, 'ticks':'', 'showticklabels':False},
                                yaxis = {'showgrid': False, 'zeroline': False, 'ticks':'', 'showticklabels':False}                                                               
                                )
                            })
                    # dbc.Row(table_card),
                    # dbc.Row(plot_card)
                ])
            ], style= {"padding": "0px", "margin-bottom": "0.5em"})
        ),
        dbc.Row(
            dbc.Card([
                dbc.CardHeader("Contact Us :)"),
                dbc.CardBody([
                    'Email me with results or corrections at highlanddanceresults@gmail.com'
                ],id = 'contact_card')
            ], style= {"padding": "0px", "margin-bottom": "0.5em"}),
        )
    ])
, fluid=True, style= {"height": "80vh"})
                


app.layout = html.Div([
    dcc.Store(id='df_store', data=df.to_dict('records')),
    dcc.Store(id='df_chosen', data=[]),
    navbar,
    cards
])

### --- POPULATING DROP DOWNS --- ###
# Populate Competition based on Year
app.clientside_callback(
    """
    function(year, df) {
        if (!year || !df) return [];
        const comps = [...new Set(df.filter(row => row.Year == year).map(row => row.Competition))];
        return comps.map(comp => ({ label: comp, value: comp }));
    }
    """,
    Output('comp_dropdown', 'options', allow_duplicate=True),
    Input('year_dropdown', 'value'),
    State('df_store', 'data'),
    prevent_initial_call=True
)

# Populate Age Group based on Competition and Year
app.clientside_callback(
    """
    function(comp, year, df) {
        if (!comp || !year || !df) return [];
        const ages = [...new Set(df.filter(row => row.Year == year && row.Competition == comp).map(row => row["Age Group"]))];
        return ages.map(age => ({ label: age, value: age }));
    }
    """,
    Output('age_dropdown', 'options', allow_duplicate=True),
    Input('comp_dropdown', 'value'),
    State('year_dropdown', 'value'),
    State('df_store', 'data'),
    prevent_initial_call=True
)


# table card
app.clientside_callback(
    """
    function(n_clicks, year, comp, age, df) {
        if (n_clicks < 1) return [];

        const drop_list = ["Competition", "Year", "Age Group", "Number"];
        const drop_list_for_table = ["Competition", "Year", "Age Group"];

        const df_chosen = df.filter(row => row.Year == year && row.Competition == comp && row["Age Group"] == age);

        var dance_to_placings = df_chosen.map(function(row) {
            const newRow = {};
            for (const key in row) {
                if (!drop_list.includes(key)) {
                    newRow[key] = row[key];
                }
            }
            return newRow;
        });

        var table_data = df_chosen.map(function(row) {
            const newRow = {};
            for (const key in row) {
                if (!drop_list_for_table.includes(key)) {
                    newRow[key] = row[key];
                }
            }
            return newRow;
        });

        const chosen_dances = Array.from(new Set(dance_to_placings.flatMap(obj => Object.keys(obj))));
        const placings = dance_to_placings.map(obj => chosen_dances.map(key => obj[key]));

        var figure_data = [];
        for (let i = 0; i < df_chosen.length; i++) {
            figure_data.push(
                {'name': placings[i][0],
                'x': chosen_dances.slice(1),
                'y': placings[i].slice(1),
                'marker': {'symbol':'cirlce',
                    'size':12},
                'type': 'scatter'}
            );

        };

        const graph_data = {
            'data': figure_data,
            'layout': {
                'yaxis': {autorange: 'reversed',
                    'side':'left',
                    'fixedrange':true},
                'xaxis': {'side': 'top',
                    'fixedrange':true},
                'legend': {'orientation': 'h',
                    'y':0,
                    'yanchor': "bottom",
                    'yref': "container"},
                'margin': {l:15, r:0, t:0},
                'hovermode':'x',
                //'title' : {'text':'Results for Dancers For Each Dance'}
            }
        };

        var selected_data = 'Results for ' + year + ' '+ comp + ' ' +age+':';

        tips = `  
            **Viewing Tips:**     
            * Turn phone sideways
            * Table Tip - Scroll left/right
            * Table Tip - Sort by clicking up/down arrows on column titles
            * Graph Tip - Click on graph points for more info
            * Graph Tip - Double click on dancer name in legend to view individual results
            `

        var table_title = '**'+ 'Table ' + selected_data +'**'
        var graph_title = '**'+ 'Plotted ' + selected_data +'**'
        
        return [graph_data,
            table_data,
            df_chosen,
            tips,
            table_title,
            graph_title];
    }
    """,
    Output('graph', 'figure', allow_duplicate=True),
    Output('table', 'data', allow_duplicate=True),
    Output('df_chosen', 'data', allow_duplicate=True),
    Output('data-markdown', 'children', allow_duplicate=True),
    Output('table_title', 'children'),
    Output('graph_title', 'children'),

    Input('submit_btn', 'n_clicks'),
    State('year_dropdown', 'value'),
    State('comp_dropdown', 'value'),
    State('age_dropdown', 'value'),
    State('df_store', 'data'),
    prevent_initial_call=True
)


# resetting graph and table
app.clientside_callback(
    """
    function(n_clicks) {

        const empty_graph = {
            'data': [],
            'layout': {'xaxis': {'showgrid': false,
                'showticklabels': false,
                'ticks': '',
                'zeroline': false},
                'yaxis': {'showgrid': false,
                'showticklabels': false,
                'ticks': '',
                'zeroline': false}}};

        return [[], empty_graph, [], [], [], [], [], []];
    }
    """,
    Output('table', 'data', allow_duplicate=True),
    Output('graph', 'figure', allow_duplicate=True),
    Output('data-markdown', 'children', allow_duplicate=True),
    Output('year_dropdown', 'value', allow_duplicate=True),
    Output('comp_dropdown', 'value', allow_duplicate=True),
    Output('age_dropdown', 'value', allow_duplicate=True),
    Output('table_title', 'children', allow_duplicate=True),
    Output('graph_title', 'children', allow_duplicate=True),

    Input('reset-btn', 'n_clicks'),
    prevent_initial_call=True
)




# Run the app
if __name__ == '__main__':
    app.run(debug=False)