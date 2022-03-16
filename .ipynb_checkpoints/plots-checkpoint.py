#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff


def getGeoData():
	return gpd.read_file('states.shp')


def getNormalData():
	return pd.read_csv('https://raw.githubusercontent.com/s-lasch/CIS-280/main/police_fatalities.csv')


def validateState(df, year, state):

	if state == ['Overall']:
			dff = df[df['Year'] == year].reset_index(drop=True)
	else:
		# filter by Year AND State
		dff = df[(df['Year'] == year) & (df['State'].isin(state))].reset_index(drop=True)

	return dff


def RacePlot(df, year, state):
	# filter by year
	df = validateState(df, year, state)

	# create a dataframe of shootings per race
	dff = (df.value_counts(['Race'])
						 .to_frame()
						 .reset_index()
						 .rename(columns={0: 'Total Shootings'})
						 .reset_index(drop=True)
					  )

	range_color = [0, dff['Total Shootings'].sum()]

	# create the bar chart
	fig = px.bar(dff[~(dff['Race']=='Other')], 
				 title=f'<b>Likely Victims by Race</b>',
				 x='Total Shootings',
				 y='Race', 
				 orientation='h',
				 category_orders={'Race': ['White', 'Black', 'Hispanic', 'Asian', 'Native', 'Other']},
				 range_x=[0,1000],
				 custom_data=['Race', 'Total Shootings'],
				 text='Race',
				 color='Total Shootings',
				 color_continuous_scale=px.colors.sequential.Blues,
				 range_color=range_color
				)

	# update the data shown when the user hovers over each bar
	fig.update_traces(hovertemplate = '<br>'.join([
									  '<b>%{customdata[0]}</b>',
									  'Shootings: %{customdata[1]}'
								  ]),
					  textposition='outside'
					 )

	# update the tile font size
	fig.update_layout(title={'font':{'size':17}}, 
					  yaxis=dict(showticklabels=False, title=''), 
					  xaxis=dict(title='Total Shootings'),
					  paper_bgcolor='rgba(0,0,0,0)',
					  plot_bgcolor='rgba(0,0,0,0)',
					  title_x=0.5)

	return fig


def CitiesBarPlot(df, year, state):
	# filter by year
	df = validateState(df, year, state)

	# dataframe of top 10 cities in descending order of shootings
	states = (df.value_counts(['City','State'])
				.to_frame()
				.reset_index()
				.rename(columns={0:'Total Shootings'})
				.sort_values('Total Shootings', ascending=False)
				.head(10)
			 )

	range_color = [0, df['UID'].count()]

	# create the bar plot
	fig = px.bar(states.sort_values('Total Shootings'),
				 title=f'<b>Fatal Force by City</b><br><sub>Top 10 U.S. cities with highest shootings</sub></br>',
				 x='Total Shootings',
				 y='City',
				 text='City',
				 custom_data=['City', 'State', 'Total Shootings'],
				 color='Total Shootings',
				 color_continuous_scale=px.colors.sequential.Blues,
				 range_color=range_color
				)

	# update the data shown when the user hovers over each bar
	fig.update_traces(hovertemplate = '<br>'.join([
									  '<b>%{customdata[0]}, %{customdata[1]}</b>',
									  'Shootings: %{customdata[2]}'
								  ]),
					  textposition='outside'
					 )

	# update the title font size
	fig.update_layout(title=dict(font=dict(size=17)), 
					  xaxis={'range': [0,35], 'title': 'Total Shootings'}, 
					  yaxis={'showticklabels': False, 'title':''},
					  paper_bgcolor='rgba(0,0,0,0)',
					  plot_bgcolor='rgba(0,0,0,0)',
					  title_x=0.5)

	return fig


def MapOfShootings(gdf, year, state):
	gdf = validateState(gdf, year, state).rename(columns={'Shootings': 'Total Shootings'})

	# create the choropleth map
	fig = px.choropleth(gdf,
						title=f'<b>U.S. Fatal Force</b>',
						geojson=gdf.geometry, locations=gdf.index, projection='albers usa',
						color='Total Shootings', color_continuous_scale=px.colors.sequential.Blues,
						range_color=[0,300],
						custom_data=['State', 'Total Shootings']
					   )

	# update the title font size
	fig.update_layout(title=dict(font=dict(size=17)),
					  geo=dict(bgcolor='#f3f3f3'),
					  paper_bgcolor='rgba(0,0,0,0)',
					  plot_bgcolor='rgba(0,0,0,0)',
					  title_x=0.5)

	# update the data shown when the user hovers over each State
	fig.update_traces(hovertemplate = '<br>'.join([
									  '<b>%{customdata[0]}</b>',
									  'Shootings: %{customdata[1]}'
								  ]))

	return fig


def GenderPieChart(df):
	# filter by gender and get the value_counts
	gender_counts = (df[(df['Gender']=='Male') | (df['Gender']=='Female')]['Gender']
					 .value_counts()
					 .to_frame()
					 .reset_index()
					 .rename(columns={'index': 'Gender', 'Gender': 'Count'})
					)

	# create the pie chart
	fig = go.Figure(data=[go.Pie(labels=gender_counts['Gender'], 
								 values=gender_counts['Count'], 
								 customdata=[gender_counts['Gender'], gender_counts['Count']], 
								 hovertemplate='<br>'.join([
									 '<extra></extra>',
									 '<b>%{label}</b>',
									 'Shootings: %{value}',
								 ]),
								 # hoverinfo='skip'
								)])

	# set the colors for male and female
	fig.update_traces(marker={'colors':px.colors.qualitative.D3})

	# update the title font size
	fig.update_layout(title='<b>Fatal Force Gender Disparity</b><br><sub>Percentage of victims by their gender</sub></br>',
					  title_font=dict(size=17),
					  paper_bgcolor='rgba(0,0,0,0)',
					  plot_bgcolor='rgba(0,0,0,0)',
					  title_x=0.5)

	return fig


def GenderKDEChart(df, gender, method='Mean'):
	# assign specific color depending on the gender
	if gender=='Male':
		color = px.colors.qualitative.D3[0]
	else:
		color = px.colors.qualitative.D3[1]

	overall_color = '#D3D3D3'

	# create the distplot
	fig = ff.create_distplot([df[df['Gender']==gender]['Age'], df['Age']], 
							 group_labels=[gender, 'All Victims'], 
							 show_rug=False, 
							 show_hist=False, 
							 colors=[color, overall_color], 
							 histnorm='probability',
							 bin_size=6
							)

	# update the title font size and the x and y axis labels
	fig.update_layout(title={'text':f'<b>Distribution of {gender} Victims</b><br><sub>Vertical lines represent the {method.lower()} of their ages</sub></br>',
							 'font':{'size':17}}, 
							  xaxis={'title':'Age'},
							  yaxis={'title':'Percentages'},
							  hovermode='x unified',
							  paper_bgcolor='rgba(0,0,0,0)',
							  plot_bgcolor='rgba(0,0,0,0)',
							  title_x=0.5
					 )

	# change the method for the vertical dashed line
	if method == 'Mean':
		# add a horizontal line that represents the overall median
		fig.add_vline(x = df['Age'].mean(),
					  line_dash='dash',
					  line=dict(color=overall_color))

		# add another horizontal line that represents the gender's median
		fig.add_vline(x = df[df['Gender']==gender]['Age'].mean(),
					  line_dash='dash',
					  line=dict(color=color))

	elif method == 'Median':
		# add a horizontal line that represents the overall median
		fig.add_vline(x = df['Age'].median(),
					  line_dash='dash',
					  line=dict(color=overall_color))

		# add another horizontal line that represents the gender's median
		fig.add_vline(x = df[df['Gender']==gender]['Age'].median(),
					  line_dash='dash',
					  line=dict(color=color))

	elif method == 'Mode':
		# add a horizontal line that represents the overall median
		fig.add_vline(x = df['Age'].mode()[0],
					  line_dash='dash',
					  line=dict(color=overall_color))

		# add another horizontal line that represents the gender's median
		fig.add_vline(x = df[df['Gender']==gender]['Age'].mode()[0],
					  line_dash='dash',
					  line=dict(color=color))

	return fig

