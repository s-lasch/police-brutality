#!/usr/bin/env python
# coding: utf-8

# dash server library
from jupyter_dash import JupyterDash

# dash standard library and the components
from dash import Dash, callback, html, dcc, Input, Output
import plots

df = plots.getNormalData()
gdf = plots.getGeoData()

# Race pot - Displays the number of shootings by race for each state
# User can choose the year and state
# make a default plot
race = plots.RacePlot(df, 2015, ['Overall'])

# Cities pot - Displays the top 10 cities within each state. If multiple states are passed, it will
# display the top 10 cities within the list of desired states.
# User can choose the year and state
# make a default plot
cities = plots.CitiesBarPlot(df, 2015, ['Overall'])

# Choropleth - Displays total shootings for each U.S. state
# User can choose the year and state
# make a default plot
choropleth = plots.MapOfShootings(gdf, 2015, ['Overall'])

# Gender pie chart - displays the percentage of male and female victims
# No user input for this chart
# make and display a default plot
pie = plots.GenderPieChart(df)

# Gender KDE chart - Displays likelihood of each gender becoming a victim as a percentage
# User can choose the gender, as well as the method
# - method can be one of 'Mean', 'Median', or 'Mode', and the default value is 'Mean'
# make a default plot
kde = plots.GenderKDEChart(df, 'Male', 'Mean')

# create a div for the html header and caption
header = html.Div(id='header', children=[
    html.H1('Fatal Force in the U.S.'),
    html.P('''
    Over the past two decades, there has been a steady increase in fatal U.S. police shootings. 
    Whether these incidents make national news or not, data shows that the trend is sloped upward for 
    fatal police shootings all across the country. The data used in this project spans from the years 
    2000-2021, and includes over 10,000 records of individuals of all races and ages that have been 
    fatally shot by police.
    '''),
    html.Hr(),
])

# create a list of 50 states and add an 'Overall' option to the beginning of the list of items
state_options = [{'label': i, 'value':i} for i in df['State'].sort_values().unique()]
state_options.append({'label':'Overall', 'value':'Overall'})
state_options.insert(0, state_options.pop())

# div for the core component options to select data
options_div = html.Div(id='options-div', children=[
    dcc.Dropdown(id='year', options=[{'label':i, 'value':i} for i in range(2000, 2022)], value=year, clearable=False),
    dcc.Dropdown(id='state', options=state_options, value=['Overall'], multi=True),
    html.Br(),
    html.Br()
])

# div for both bar plots
bar_div = html.Div(id='bar-div', children=[
    dcc.Graph(id='race-plot', figure=race),
    dcc.Graph(id='cities-plot', figure=cities)    
])

# div for the choropleth
map_div = html.Div(id='map-div', children=[
    html.Label('Viewing data for:'),
    options_div,
    dcc.Graph(id='map', figure=choropleth)
])

# div for the pie chart and the KDE chart for gender
gender_data_div = html.Div(id='gender-data-div', children=[
    html.Hr(),
    html.Br(),
    # insert the pie chart
    dcc.Graph(id='pie', figure=pie),
    
    # insert radio buttons for gender
    dcc.RadioItems(
        id='gender',
        options=[{'label': i, 'value': i} for i in ['Male', 'Female']],
        value='Male'
    ),
    
    # insert ratio buttons to view the mean, median or mode of the data
    dcc.RadioItems(
        id='method',
        options=[{'label': i, 'value': i} for i in ['Mean', 'Median', 'Mode']],
        value='Mean'
    ),
    
    # insert the density plot for genders
    dcc.Graph(id='kde', figure=kde),
])

# Create the dash application
app = Dash(__name__) 

# Create server variable 
server = app.server

# create the layout below
app.layout = html.Div(id='content', children=[
    # HTML header
    header,
    html.Br(),
    
    # bar chart div and the choropleth div
    bar_div,
    map_div,
    html.Br(),
    
    # pie chart and KDE div
    gender_data_div
])

# callback function to update bar charts and choropleth
@app.callback(
    Output('race-plot', 'figure'),
    Output('cities-plot', 'figure'),
    Output('map', 'figure'),
    Input('year', 'value'),
    Input('state', 'value')
)
def updateYearlyPlots(year, state):   
    # create plots from the year and State
    race_plot = plots.RacePlot(df, year, state)
    cities_plot = plots.CitiesBarPlot(df, year, state)
    map_plot = plots.MapOfShootings(gdf, year, state)
    
    # return each plot
    return race_plot, cities_plot, map_plot

# update the kde plot
@app.callback(
    Output('kde', 'figure'),
    Input('gender', 'value'),
    Input('method', 'value')
)
def updateKDE(gender, method):
    # return an updated KDE chart from the gender and method
    return plots.GenderKDEChart(df, gender, method)

# run the app as a webpage
if __name__ == '__main__':
    app.run_server(debug=True)

