# -*- coding: utf-8 -*-
# dash/plotly core functions
from dash import html, dcc, Dash
from dash.dependencies import Input, Output, State # for callback functions
import plotly.express as px # plotting functions

# style control
import dash_bootstrap_components as dbc # webpage styles/themes
from dash_bootstrap_templates import load_figure_template # style of figure

# other libraries
import pandas as pd
import utilfuncs # customized functions for dataframe manipulation
from time import perf_counter

# %% 


# %% defining elements

# some static elements
header1 = html.H1(id = 'H1', 
    children = 'Popular hashtags of the year', 
    style = {'textAlign':'center','marginTop':50,'marginBottom':40})
header2 = html.H1(id = 'H2', 
    children = 'Co-occuring hashtags', 
    style = {'textAlign':'center','marginTop':50,'marginBottom':40})

# input for the first bar plot
dropdown1 =  dcc.Dropdown( id = 'dropdown',
     options = [ {'label': '2017', 'value':2017 },
                {'label': '2018', 'value':2018 },
                {'label': '2019', 'value':2019 },
                {'label': '2020', 'value':2020 },
                {'label': '2021', 'value':2021 },
                {'label': '2022', 'value':2022 }], value = 2022)

barplot1 = dcc.Graph(id = 'bar_plot1')


# inputs for the second bar plot, as well as the two line plots
radiobtn1 = dcc.RadioItems(id = 'rbtn1',options = ['hashtag', 'text'], 
                           value = 'hashtag')
filterinput1 = dcc.Input(id='filter_hashtag',type='text',value='#python')
btn1 = html.Button(id='btn1', n_clicks=0, children='Update',
                   style={'float': 'center','margin': 'auto'})

barplot2 = dcc.Graph(id = 'bar_plot2')
lineplot1 = dcc.Graph(id = 'line_plot1')
lineplot2 = dcc.Graph(id = 'line_plot2')

# %% defining layout
app = Dash(external_stylesheets=[dbc.themes.SLATE])
load_figure_template('SLATE') 
app.layout = html.Div( 
    [
        header1,
        dbc.Row(
            [dbc.Col([html.H3('Select year'),
                      html.Hr(),
                      dropdown1,
                      html.Hr(),
                      dcc.Loading(id="loading-1",type="default",children=html.Div(id='total_tweets')),
                      html.Hr()], align = 'center'),
             dbc.Col(barplot1, width = 8)],
             style = {'margin-left':'50px', 'margin-top':'50px', 'margin-right':'50px'}
            ),
        
        html.Hr(),
        
        header2,
        dbc.Row(
            [dbc.Col([html.H3('Search hashtag'),
                      html.Hr(),
                      html.P(['Enter your search term:']), 
                      filterinput1,
                      html.Hr(),
                      html.P(['Search scope:']),
                      radiobtn1,
                      html.Hr(),
                      btn1,
                      html.Hr(),
                      dcc.Loading(id="loading-2",type="default",children=html.Div(id='update_loading_time'))
                      ], align = 'end'),
             dbc.Col(barplot2,width = 8)
                ], 
            style = {'margin-left':'50px', 'margin-top':'50px', 'margin-right':'50px'}),
        dbc.Row(
            [dbc.Col( html.Div(lineplot1),width = 4),
             dbc.Col( html.Div(lineplot2),width = 4)],justify='end',
            style = {'margin-left':'50px', 'margin-top':'50px', 'margin-right':'50px'})
        
    ])
# %%

# %% data and callback functions


layout_test = False
if not layout_test: # skip callback when tweaking layout

    # load dataset
    df = pd.read_csv('dataset_sampled.csv') # the original dataset is too large to upload
    
    # fig 1
    @app.callback([Output(component_id='bar_plot1', component_property= 'figure'),
                   Output(component_id='total_tweets', component_property= 'children')],
                  [Input(component_id='dropdown', component_property= 'value')])
    def hashcount_update(dropdown_value):
        print(dropdown_value)
        subdf = df[df['year']==dropdown_value].copy()
        
        tic = perf_counter()
        dfhashtag = utilfuncs.counthashtag(subdf,n_rows = 30) # a helper function that returns hashtag counts
        
        fig = px.bar(dfhashtag, x = 'hashtag',y = 'count')
        fig.update_traces(marker_color='indianred')
        fig.update_layout(title = 'most popular hashtags of year ' + str(dropdown_value),
                          xaxis_title = 'hashtags',
                          yaxis_title = 'number')
        toc = perf_counter()
        text_out = ('Total number of tweets in ' + 
                    str(dropdown_value) + 
                    ': ' + str(subdf.shape[0]) + 
                    '. Elapsed time: ' + str(toc-tic)[0:5] + 's')
        return fig, text_out
    
    
    # figs 2,3,4
    @app.callback([Output(component_id='bar_plot2', component_property= 'figure'),
                   Output(component_id='line_plot1', component_property= 'figure'),
                   Output(component_id='line_plot2', component_property= 'figure'),
                   Output(component_id='update_loading_time', component_property= 'children')],
                  [Input(component_id='btn1', component_property= 'n_clicks'),
                   State(component_id='filter_hashtag', component_property= 'value'),
                   State(component_id='rbtn1', component_property= 'value')])
    def bloc2_update(n_clicks,filter_hashtag,search_scope):
        
        tic = perf_counter()
        
        subdf = df.copy() # when using the original dataset, it is recommended to sample a fraction to speed up response
        alltweet_yearcount = (subdf.groupby('year').count().reset_index()).copy()
        
        subdf = utilfuncs.contains_hashtag(subdf, filter_hashtag)
        if search_scope == 'hashtag':
            dfhashtag = utilfuncs.counthashtag(subdf, 31)
        if search_scope == 'text':
            dfhashtag = utilfuncs.countwords(subdf, 31)
        
        filtered_tweetnum = subdf.shape[0]
        dfhashtag = dfhashtag[dfhashtag['hashtag']!=filter_hashtag]
        dfhashtag['count'] = (dfhashtag['count']/filtered_tweetnum)*100
        fig1 = px.bar(dfhashtag, x = 'hashtag',y = 'count')
        fig1.update_traces(marker_color='lightsalmon')
        fig1.update_layout(title = 'most frequent co-occuring ' + search_scope + ' of ' + filter_hashtag,
                          xaxis_title = 'words/hashtags',
                          yaxis_title = 'percentage')
        
        tag_yearcount = subdf.groupby('year').count().reset_index()
        tag_yearcount['day'] = (tag_yearcount['day']/alltweet_yearcount['day'])*100
        fig2 = px.line(tag_yearcount, x = 'year',y = 'day')
        fig2.update_traces(line_color="#558832")
        fig2.update_layout(title = 'percentage of appearance over time',
                          xaxis_title = 'year',
                          yaxis_title = 'percentage')
        
        mean_interaction = subdf.groupby('year').mean().reset_index()
        mean_interaction['total_interaction'] = (mean_interaction['likes'] +
                                                 mean_interaction['replies'] +
                                                 mean_interaction['retweets'] +
                                                 mean_interaction['quote'])
        fig3 = px.line(mean_interaction, x = 'year',y = 'total_interaction')
        fig3.update_traces(line_color="#553399")
        fig3.update_layout(title = 'average interactions per tweet',
                          xaxis_title = 'year',
                          yaxis_title = 'number of interactions')
        
        toc = perf_counter()
        text_out = 'Elapsed time: ' + str(toc-tic)[0:5] + 's'
        return fig1, fig2, fig3, text_out

# %% run the app

if __name__ == '__main__': 
    app.run_server()
