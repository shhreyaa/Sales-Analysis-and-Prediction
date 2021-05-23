import warnings
import pandas as pd
import dash
import dash_table
import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import datetime
import flask
import plotly.express as px
import plotly.graph_objs as go  # (need to pip install plotly==4.4.1)
import plotly
import dash_bootstrap_components as dbc

from server import app


warnings.filterwarnings("ignore")


df = pd.read_excel("data/sales_replaced.xlsx")
df['Ship Date'] = pd.to_datetime(df['Order Date'])
resampled = df.resample('M', on='Ship Date').sum().reset_index()
resampled['month'] = resampled['Ship Date'].apply(lambda x: x.strftime('%B'))
df['Order Date'] = pd.to_datetime(df['Order Date'])
future_forcast = pd.read_excel("data/future_work.xlsx")
future_forcast['Date'] = pd.to_datetime(future_forcast['Date']).dt.date
furniture_forcast=pd.read_excel("data/furniture_work.xlsx")
office_forcast=pd.read_excel("data/office_work.xlsx")
technology_forcast=pd.read_excel("data/technology_work.xlsx")
#df = pd.DataFrame()
#df['Ship ']
# app = dash.Dash(
#     external_stylesheets=[dbc.themes.BOOTSTRAP]
# )
# app.config.suppress_callback_exceptions = True

# Sale vs Profit
df1 = df.copy()
cols = ['Row ID', 'Customer ID', 'Segment', 'Category', 'Product ID',
        'Category', 'Sub-Category', 'Product Name', 'Quantity', 'Discount']
df1.drop(cols, axis=1, inplace=True)

df1 = df1.sort_values('Order Date')
df1.isnull().sum()
df1 = df.set_index('Order Date').resample('MS').sum()

#Total sale prediction 
sale_total = df.copy()

sale_total = pd.read_excel("data/sales_replaced.xlsx")
sale_total.head()
cols = ['Row ID', 'Customer ID', 'Segment', 'Product ID', 'Category', 'Sub-Category', 'Product Name', 'Quantity', 'Discount', 'Profit']
sale_total.drop(cols, axis=1, inplace=True)
sale_total = sale_total.sort_values('Order Date')


sale_total.isnull().sum()
sale_total= sale_total.groupby('Order Date')['Sales'].sum().reset_index()
sale_total = sale_total.set_index('Order Date')

sale_total=sale_total['Sales'].resample('MS').sum()

sale_total= sale_total.to_frame()


figSale = go.Figure([
    go.Scatter(
        name='Profit',
        x=df1.index,
        y=df1['Sales'].resample('MS').sum(),
        mode='lines',
        marker=dict(color='#EF553B', size=2),
        showlegend=True
    ),
    go.Scatter(
        name='Sale',
        x=df1.index,
        y=df1['Profit'].resample('MS').sum(),
        mode='markers+lines',
        marker=dict(color='#636EFA', size=2),
        showlegend=True
    )

])


figSale.update_layout(
    title="Sale VS Profit",
    xaxis_title="Time",
    yaxis_title="In Million",
    height=500
)


fig = go.Figure([
      go.Scatter(
        name='Predicted value',
        x=future_forcast['Date'],
        y=future_forcast['Prediction'],
        mode='markers+lines',
        marker=dict(color='red', size=5),
        showlegend=True
    ),
     go.Scatter(
        name='Actual sales',
        x=sale_total.index,
        y=sale_total['Sales'],
        mode='markers+lines',
        marker=dict(color='blue', size=5),
        showlegend=True
    )

])


fig.update_layout(
    title="Total Sales",
    xaxis_title="Time",
    yaxis_title="Sales(In Million)",
    height=750
   
)
#All of the analysis Parts--------------------------------------------------
analysis = html.Div(
    id = 'analysis-portion',
    children = [
        html.Div([
            html.H4("Number of sales"),
        ],
        style={'width': '49%', 'display': 'inline-block',
               
               'opacity': '0.6',
               'color': '#000000',
               
         }),
       
        html.Div([
            dcc.Tabs(
                id='my_Tab',
                value='Category',
                children=[
                    dcc.Tab(label='Category', value='Category'),
                    dcc.Tab(label='Sub-Category', value='Sub-Category')
                ], 
            style= {'width': '49%', 'display': 'inline-block',
                     'margin-top':'0.5%',
                     'font-size':'20px'}
            ),
        ]),
        # PieChart--------------------------------------------------
        html.Div([
            dcc.Graph(id='the_graph'),
        ],
            style={'width': '49%', 'display': 'inline-block',
               'backgroundColor': '#22C1AD'
            }
        ),
        #Drop Down For Data table----------------------------------------------
        html.Div([
            html.Div([
                html.H5(["Total Sales Vs Profit Graph"],style={'text-align': 'center','margin-top':'30px','padding':'10px','font-size':'30px','letter-spacing':'3px','background-color':'#345678','color':'#fff'}),
                dcc.Graph(id='sale_and_profit', figure=figSale,style={'margin':'2%'})
            ]
            ),
        ],
        style={'width': '50%', 'display': 'inline-block',
                'float':'right',
            }   
        ),
        # Bar Graph--------------------------------------------
        html.Div([
            html.H3(["Comparison Of Sales between different categories"],style={'text-align': 'center','margin-top':'30px','padding':'10px','font-size':'30px','letter-spacing':'3px','background-color':'#345678','color':'#fff'}),
            html.Br(),
            dcc.Graph(
                id='graph-with-slider'),
            dcc.Slider(
                id='year-slider',
                min=df['year'].min(),
                max=df['year'].max(),
                value=df['year'].min(),
                # color=df['Category'],
                marks={str(year): str(year) for year in df['year'].unique()},
                step=None
            )
        ],
            style={
            'backgroundColor':  '#f3f3f3',
            'padding': '20px',
            'color': '#ffffff',
            'margin':'200px',
            'height':'500px'
            },
        ),
    # individual selection------------------------------------------------
   html.Div([
        html.H3(["Individual Sales Growth"],style={'text-align': 'center','margin-top':'40px','padding':'7px','font-size':'30px','letter-spacing':'3px','background-color':'#345678','color':'#fff'}),   
        html.H3(["Please choose a category"],style={'text-align': 'center'}),
        dcc.RadioItems(
            options=[
                {'label': 'Furniture', 'value': 'Furniture'},
                {'label': 'Office Supplies', 'value': 'Office Supplies'},
                {'label': 'Technology', 'value': 'Technology'}
            ],
            id= 'radio-items',
            value='Furniture',
            labelStyle={'display': 'inline-block','padding':'10px','font-size':'25px'},
            inputStyle={"margin-right": "5px"},
            style= {'display':'flex','align-items':'center','justify-content':'center'}
        ),
        html.Div(id='output_container', children=[],style={'text-align': 'center','font-size':'30px','font-weight':'bold'}),
        html.Br(),
    
        dcc.Graph(
            id='individual_pred',style={'font-size': '20px'}),
            html.Div([
                html.H1(
                id='expected_growth', children=[],style={'text-align': 'center'})    
            ],
            style={'width': '35%', 'display': 'inline-block', 'padding':'50px','background' :'linear-gradient(150deg, #153F7F, #297DFD 100%)','border-radius':'25px','border-shadow':'5px 5px 10px','color':'white','margin-left':'100px'
            })
           
    ]),
    #footerrr
    html.Div([
        html.H3()
    ],
    style={'padding':'20px','background color':'blue','height':'100px'})
    ],
    style={'color':'#656565'}
)


#All of the prediction part-------------------------------------------
prediction = html.Div([
     html.H5("Total Sales Vs Profit Graph",style={'text-align': 'center','margin-top':'30px','padding':'10px','font-size':'30px','letter-spacing':'3px','background-color':'#345678','color':'#fff'}),
   html.Div([

   
    dcc.Graph(id='my_line', figure=fig,style={'margin':'2%'})

],
 style={'width': '70%', 'display': 'inline-block'
               }),
    html.Div([
         html.Div([
         html.H1("17.6%", style={'text-align': 'center','font-size':'100px'}),
         html.H2("Estimated growth for the upcoming year")
         ],style={'width': '80%', 'display': 'inline-block', 'padding':'5%','background' :'linear-gradient(150deg, #153F7F, #297DFD 100%)','border-radius':'25px','border-shadow':'5px 5px 10px','color':'white'
               }
                  ),
           html.Br(),
             html.Br(),
               html.Br(),
    dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in future_forcast.columns],
  
    data=future_forcast.to_dict('records'),
    style_table={'height': '400px', 'overflowY': 'auto'},
      fixed_rows={'headers': True},
      style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': '#B0C4DE'
        }
    ],
        style_cell_conditional=[
        {
           
            'textAlign': 'center'
        }],
    style_header={
        'backgroundColor': '#00416A',
        'textAlign':'Center',
        'fontWeight': 'bold',
        'height':'60px',
          'color':'#fff',
          'font-size':'20px'
    },
    
)
],
              style={'width': '29%', 'display': 'inline-block',
                     'align':'right','position':'absolute','margin':'50px 0px','border-shadow':'5px 5px 10px'
               }),
    

#side component
#For individual prediction
html.Div([
   html.H1(["Individual Sales Prediction"],style={'text-align': 'center','margin-top':'30px','font-size':'40px','letter-spacing':'3px','padding':'10px','background-color':'#345678','color':'#fff'}),
   html.Br(),
   html.Br(),
   html.H3(["Please choose a category"],style={'text-align': 'center'}),
   
    dcc.RadioItems(
    options=[
        {'label': 'Furniture', 'value': 'Furniture'},
        {'label': 'Office Supplies', 'value': 'Office Supplies'},
        {'label': 'Technology', 'value': 'Technology'}
    ],
    id= 'radio-items-pred',
    value='Furniture',
    labelStyle={'display': 'inline-block','padding':'10px','font-size':'25px'},
    inputStyle={"margin-right": "5px"},
    style= {'display':'flex','align-items':'center','justify-content':'center'}
),
   
    html.Div(id='output_container_pred', children=[],style={'text-align': 'center','font-size':'30px','font-weight':'bold'}),
    html.Br(),
    
    dcc.Graph(
    id='individual_pred_pred',style={'font-size': '20px'}),
    html.Div([
    html.H1(
    id='expected_growth_pred', children=[],style={'text-align': 'center'})
    
    ],
             style={'width': '35%', 'display': 'inline-block', 'padding':'50px','background' :'linear-gradient(150deg, #0e4d79, #297DFD 100%)','border-radius':'25px','border-shadow':'5px 5px 10px','color':'white','margin-left':'100px'
               }),
     html.Div([
    html.H2(
    "Technology will Sale the highest in the upcoming years")
    
    ],
             style={'width': '35%', 'display': 'inline-block', 'padding':'60px','background' :'linear-gradient(150deg, #153F7F, #297DFD 100%)','border-radius':'25px','border-shadow':'5px 5px 10px','color':'white','margin-left':'90px'
               })
    
    
]) 
],style={'margin':'30px'}
)






#Application layout---------------------------------------------------
layout = html.Div([

    #The title ---------------------------------------------------
    html.Div([
        html.Div("SUPERMARKET SALES ANALYSIS AND PREDICTION"),
    ],
        style={'padding': '80px',
               'backgroundColor': '#073857',
               'font-size':'60px',
                'color': '#ffffff',
               'textAlign': 'center',
               'opacity': '0.9'
               }
    ),
    #Tabs for separating analysis and prediction----------------------
    html.Div([
        dcc.Tabs(
            id='analysis-and-prediction',
            value='Analysis',
            children = [
                dcc.Tab(label='Analysis', value='Analysis'),
                dcc.Tab(label='Prediction', value='Prediction')
            ]
        )
    ],
    style={
        'width': '51%', 'display': 'inline-block',
        'font-size':'40px',
        'left-padding': '3em',
        'backgroundColor': 'red',
        'opacity': '0.6',
        'color': '#000000',
    }),

    html.Div([html.Div(id = 'analysis-or-prediction')],
    style={
       
    }
        
    )

])


# ---------------------------------------------------------------
#Analysis and Prediction Tabs-----------------------------------------
@app.callback(
    Output(component_id='analysis-or-prediction',component_property='children'),
    [Input(component_id='analysis-and-prediction',component_property='value')]
)
def update_section(This_Tab):
    if This_Tab == 'Analysis':
        return analysis
    else:
        return prediction

#Analysis CallBack functions-----------------------------------------
# Pie Chart---------------------------
@app.callback(
    Output(component_id='the_graph', component_property='figure'),
    [Input(component_id='my_Tab', component_property='value')]
)
def update_graph(my_Tab):
    dff = df
    piechart = px.pie(
        data_frame=dff,
        names=my_Tab,
        #values = 'Sub-Category',
        hole=.3,  
    )
    return (piechart)

# Bar Graph---------------------------------


@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('year-slider', 'value')])
def update_figure(selected_year):
    filtered_df = df[df.year == selected_year]
    filtered_df = filtered_df.sort_values('Order Date')
    traces = []
    for i in filtered_df.Category.unique():
        df_by_Category = filtered_df[filtered_df['Category'] == i]
        traces.append(dict(
            x=df_by_Category['month'],
            y=df_by_Category['Sales'],
            type='bar',
            opacity=0.7,
            marker={
                'size': 00,
                'line': {'width': 0, 'color': 'white'}
            },
            name=i
        ))

    return {
        'data': traces,
        'layout': dict(
            xaxis={'type': 'bar', 'title': 'Months',
                   },
            yaxis={'title': 'Sales(in Million)'},
            x_label=df_by_Category['month'],
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest',
            transition={'duration': 500},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'

        )
    }

@app.callback([Output('individual_pred', 'figure'),
               Output('output_container', 'children'),
               Output('expected_growth', 'children')
               ],
              
    [Input('radio-items', 'value')])
def make_line_chart(value):
    container = "Sales Graph for {} ".format(value)
    individual_category = df.loc[df["Category"] == "{}".format(value)]
    cols = ['Row ID', 'Customer ID', 'Segment', 'Product ID', 'Category', 'Sub-Category', 'Product Name', 'Quantity', 'Discount']
    individual_category.drop(cols, axis=1, inplace=True)
    individual_category = individual_category.sort_values('Order Date')

    individual_category.isnull().sum()
    
    individual_category = individual_category.set_index('Order Date').resample('MS').sum()
    # individual_category=individual_category['Sales'].resample('MS').sum()
    # individual_category= individual_category.to_frame()
    if (value == "Furniture"):
        
        expected_growth = "Sales is 6.87% for {} in 2019 ".format(value)
        
    elif (value =="Office Supplies"):
        
        expected_growth = "Sales is 5.49% for {} in 2019 ".format(value)
    else:
        
        expected_growth = "Sales is 10.24% for {} in 2019 ".format(value)
        
    figure = go.Figure([
      go.Scatter(
        name='Sales',
        x=individual_category.index,
        y=individual_category['Sales'].resample('MS').sum(),
        mode='markers+lines',
        marker=dict(color='#EF553B', size=5),
        showlegend=True
    ),
     go.Scatter(
        name='Profit',
        x=individual_category.index,
        y=individual_category['Profit'].resample('MS').sum(),
        mode='markers+lines',
        marker=dict(color='#636EFA', size=2),
        showlegend=True
    )
     


    ])
    figure.update_layout(
    title="Total Sales",
    
    xaxis_title="Time",
    yaxis_title="Sales(In Million)",
    height=800
   
)
    return figure,container,expected_growth

#Prediction Callback functions---------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback([Output('individual_pred_pred', 'figure'),
               Output('output_container_pred', 'children'),
               Output('expected_growth_pred', 'children')
               ],
              
    [Input('radio-items-pred', 'value')])
def make_line_chart(value):
    container = "Time Series Prediction Graph for {} ".format(value)
    sale_category = df.loc[df["Category"] == "{}".format(value)]
    cols = ['Row ID', 'Customer ID', 'Segment', 'Product ID', 'Category', 'Sub-Category', 'Product Name', 'Quantity', 'Discount', 'Profit']
    sale_category.drop(cols, axis=1, inplace=True)
    sale_category = sale_category.sort_values('Order Date')

    sale_category.isnull().sum()
    sale_category= sale_category.groupby('Order Date')['Sales'].sum().reset_index()
    sale_category = sale_category.set_index('Order Date')
    sale_category=sale_category['Sales'].resample('MS').sum()
    sale_category= sale_category.to_frame()
    if (value == "Furniture"):
        dff = furniture_forcast
        expected_growth = "Expected Growth for {} is 9.87% ".format(value)
        
    elif (value =="Office Supplies"):
        dff =office_forcast
        expected_growth = "Expected Growth for {} is 10.46% ".format(value)
    else:
        dff= technology_forcast
        expected_growth = "Expected Growth for {} is 16.45% ".format(value)
        
    
    
    
    figure = go.Figure([
      go.Scatter(
        name='Predicted value',
        x=dff['Date'],
        y=dff['Prediction'],
        mode='markers+lines',
        marker=dict(color='red', size=5),
        showlegend=True
    ),
     go.Scatter(
        name='Actual sales',
        x=sale_category.index,
        y=sale_category['Sales'],
        mode='markers+lines',
        marker=dict(color='blue', size=5),
        showlegend=True
    )
    ])
    figure.update_layout(
    title="Total Sales",
    
    xaxis_title="Time",
    yaxis_title="Sales(In Million)",
    height=800
   )
    return figure,container,expected_growth








