import pandas as pd
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

app = dash.Dash()

# These columns in the csv-file will be needed
cols = [
    "iso_code",
    "location",
    "continent",
    "date",
    "total_cases",
    "new_cases_smoothed",
    "total_deaths",
    "new_deaths_smoothed",
    "total_cases_per_million",
    "new_cases_smoothed_per_million",
    "total_deaths_per_million",
    "new_deaths_smoothed_per_million",
    "icu_patients_per_million",
    "hosp_patients_per_million",
    "weekly_hosp_admissions_per_million",
    "reproduction_rate",
    "total_tests_per_thousand",
    "new_tests_smoothed",
    "new_tests_smoothed_per_thousand",
    "positive_rate",
    "tests_per_case",
    "total_vaccinations",
    "people_fully_vaccinated",
    "new_vaccinations_smoothed",
    "total_vaccinations_per_hundred",
    "people_vaccinated_per_hundred",
    "people_fully_vaccinated_per_hundred",
    "new_vaccinations_smoothed_per_million",
    "stringency_index",
    "excess_mortality",
    "population",
    "population_density",
    "median_age",
    "aged_65_older",
    "gdp_per_capita",
    "extreme_poverty",
    "handwashing_facilities",
    "hospital_beds_per_thousand",
    "life_expectancy",
    "human_development_index"
]

# Importing the data
url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
data = pd.read_csv(url, usecols=cols)
df = pd.DataFrame(data)

# "date" as object to "date" as datetime format
df["date"] = pd.to_datetime(df["date"], format='%Y-%m-%d')

# Deleting the only record for Bonaire Sint Eustatius and Saba
df.drop(df[df['location'] == 'Bonaire Sint Eustatius and Saba'].index, inplace=True)

# Shortening some country names
df.loc[df['iso_code'] == 'COD', 'location'] = 'Dem. Rep. of Congo'
df.loc[df['iso_code'] == 'VCT', 'location'] = 'St Vincent Grenadines'
df.loc[df['iso_code'] == 'SXM', 'location'] = 'Sint Maarten (Dutch)'
df.loc[df['iso_code'] == 'CAF', 'location'] = 'Central African Rep.'

# These aggregate iso country codes ("Europe", "Asia", "World"...) will not be needed:
df = df[~df['iso_code'].isin(["OWID_AFR",
                            "OWID_ASI",
                            "OWID_EUR",
                            "OWID_EUN",
                            "OWID_INT",
                            "OWID_NAM",
                            "OWID_OCE",
                            "OWID_SAM",
                            "OWID_WRL",
                                      ])]

# Filling NaNs in the column 'stringency_index' with the latest known value for each country
df[['stringency_index']] = df.groupby('location')[['stringency_index']].fillna(method='ffill')

# Defining the allowed time scope for the calender
min_date_allowed = df["date"].min()
max_date_allowed = df["date"].max()

# Creating the dictionaries as input values for the drop-down menu
countries = df["location"].unique()
country_options = []
for country in countries:
    country_options.append({'label': country, 'value': country})

# These parameters are dynamic and will be displayed along the timeline and on the map
parameters_for_timelines = df[[
    "total_cases",
    "new_cases_smoothed",
    "total_deaths",
    "new_deaths_smoothed",
    "total_cases_per_million",
    "new_cases_smoothed_per_million",
    "total_deaths_per_million",
    "new_deaths_smoothed_per_million",
    "icu_patients_per_million",
    "hosp_patients_per_million",
    "weekly_hosp_admissions_per_million",
    "reproduction_rate",
    "total_tests_per_thousand",
    "new_tests_smoothed",
    "new_tests_smoothed_per_thousand",
    "positive_rate",
    "tests_per_case",
    "total_vaccinations",
    "people_fully_vaccinated",
    "new_vaccinations_smoothed",
    "total_vaccinations_per_hundred",
    "people_vaccinated_per_hundred",
    "people_fully_vaccinated_per_hundred",
    "new_vaccinations_smoothed_per_million",
    "stringency_index",
    "excess_mortality"
]]

# These parameters are static and will be displayed on the bar chart
parameters_for_bars = df[[
    "population",
    "population_density",
    "median_age",
    "aged_65_older",
    "gdp_per_capita",
    "extreme_poverty",
    "handwashing_facilities",
    "hospital_beds_per_thousand",
    "life_expectancy",
    "human_development_index",
    "stringency_index",
]]

# Creating the Layout of a dashboard
app.layout = html.Div([

# Headers
    html.Div([

        html.H2('Corona Dash: Visualization of the database from',
            style={'margin': 0, 'textAlign': 'left', 'padding': '10px', 'font-family': 'arial', 'display': 'inline-block'}),

        html.Label([html.A('Our World in Data', href='https://github.com/owid/covid-19-data/tree/master/public/data')],
            style={'margin': 0, 'textAlign': 'left', 'padding': '10px', 'fontSize': 25, 'font-family': 'arial', 'display': 'inline-block'}),
            ],
        ),

# The upper part of the dashboard - country selector and everything related to the timeline
    html.Div([
        html.Div([html.H4("""Select the main parameter to explore:""",
                            style={'margin': 0, 'padding':'10px', 'textAlign': 'left', 'font-weight': 'bold', 'margin-left': '0em', 'margin-right': '2em', 'display': 'inline-block', 'width': '30%', 'font-family': 'arial'})
                    ],
                    ),
        html.Div([dcc.Dropdown(id='parameter-picker-timelines',
                         options=[{'label': i.replace("_", " "), 'value': i} for i in parameters_for_timelines],
                         value='people_fully_vaccinated_per_hundred')],
             style={'padding':'10px', 'width': '25%', 'display': 'inline-block', 'vertical-align': 'top', 'fontSize': 15, 'font-family': 'arial'}
             ),
            ]),

    html.Div([
        html.Div([
            html.Div(html.H4("""Select some countries to compare in the timeline:""",
                        style={'margin': 1,'padding':'10px', 'textAlign': 'left', 'font-weight':'bold', 'margin-left': '0em', 'margin-right': '2em', 'display': 'inline-block', 'width': '40%', 'font-family': 'arial'}),
                        ),
            html.Div([dcc.Dropdown(id='country-picker',
                   options=[{'label': i, 'value': i} for i in df["location"].unique()],
                   value=['Germany', 'United States', 'Russia', 'Israel', 'India'],
                   multi=True)],
                         style={'padding':'10px', 'width': '47.2%', 'height': '50px', 'display': 'inline-block', 'fontSize': 15, 'font-family': 'arial'}
                     ),

        html.Div([dcc.Graph(id='graph-timeline')],
                 style={'margin-bottom': 10})],

        style={'margin': 10, 'border': '0.5px lightgrey dashed', 'border-radius': 15})]),

# The lower part of the dashboard: the map and the bar chart
    html.Div([
        html.Div([
            # Map and everything that belongs to it
            html.Div([
                html.Div([html.H4("""Main parameter: the global distribution""",
                                    style={'margin': 0, 'padding':'10px', 'textAlign': 'left', 'font-weight': 'bold', 'width': '50%', 'font-family': 'arial'})
                                ],
                                ),

                html.Div([
                    html.Div([html.H4("""Please choose the date: """,
                                        style={'padding':'10px', 'margin': 0, 'textAlign': 'left', 'width': '50%', 'font-family': 'arial', 'display': 'inline-block'})
                                    ],
                                    ),
                    html.Div([dcc.DatePickerSingle(
                        id='date-picker-single',
                        min_date_allowed=min_date_allowed.date(),
                        max_date_allowed=max_date_allowed.date(),
                        initial_visible_month=max_date_allowed.date(),
                        date=max_date_allowed,
                        first_day_of_week=1,
                        number_of_months_shown=3,
                        display_format="DD MMM YYYY",
                        with_portal=True,
                        day_size=50,
                                        ),
                              ],
                             style={'padding':'10px', 'margin': 0, 'display': 'inline-block'}
                             ),
                        ]
                    ),

                html.Div([dcc.Graph(id='graph-map')])
            ],

                style={'width': '48%', 'margin': 0, 'padding': '10px', 'display': 'inline-block'}),

            # Bar chart and everything that belongs to it
            html.Div([
                html.Div([html.H4("""Select an additional parameter of your interest (x-axis):""",
                                    style={'margin': {'l': 0, 'b': 0, 't': 5, 'r': 0}, 'padding':'10px', 'textAlign': 'left', 'font-weight': 'bold', 'font-family': 'arial'})
                                ],
                                ),
                html.Div([dcc.Dropdown(id='parameter-picker-bars',
                             options=[{'label': i.replace("_", " "), 'value': i} for i in
                                              parameters_for_bars],
                             value='human_development_index')],
                         style={'margin': 0, 'padding':'10px', 'width': '50%', 'fontSize': 15, 'font-family': 'arial'}
                         ),

                html.Div([dcc.Graph(id='graph-scatter')], style={'margin': {'l': 0, 'b': 0, 't': 5, 'r': 0}}),
            ],

                style={'width': '48%', 'margin': 0, 'display': 'inline-block', 'vertical-align': 'top'}),
        ],

    style={'margin': 10, 'border': '0.5px lightgrey dashed', 'border-radius': 15, 'width': '98.9%'})
    ]),

html.Div(html.H4(["""Sources:""", html.Br(),
"""Mathieu, E., Ritchie, H., Ortiz-Ospina, E. et al. A global database of COVID-19 vaccinations. Nat Hum Behav (2021). https://doi.org/10.1038/s41562-021-01122-8""", html.Br(),
"""Hasell, J., Mathieu, E., Beltekian, D. et al. A cross-country database of COVID-19 testing. Sci Data 7, 345 (2020). https://doi.org/10.1038/s41597-020-00688-8""", html.Br(),
"""This data has been collected, aggregated, and documented by Cameron Appel, Diana Beltekian, Daniel Gavrilov, Charlie Giattino, Joe Hasell, Bobbie Macdonald, Edouard Mathieu, Esteban Ortiz-Ospina, Hannah Ritchie, Lucas Rodés-Guirao, Max Roser.""", html.Br()],

    style={'margin': 1, 'padding':'5px', 'font-size': '12px', 'textAlign': 'left', 'margin-left': '0em', 'margin-right': '2em', 'font-family': 'arial'}),
    ),
])

# Generating the timeline
@app.callback(Output('graph-timeline', 'figure'),
              [Input('parameter-picker-timelines', 'value'),
               Input('country-picker', 'value'),
               ])
def update_figure(parameter_timelines, country_name):
    filtered_df = df[df['location'].isin(country_name) & df[parameter_timelines].notnull()][['location', parameter_timelines, 'date']]
    figure = px.line(filtered_df,
                     x=filtered_df["date"],
                     y=filtered_df[parameter_timelines],
                     color=filtered_df["location"],
                     color_discrete_sequence=px.colors.qualitative.G10,
                     labels={'date': 'timeline', f'{parameter_timelines}': f'{parameter_timelines.replace("_", " ")}'}
                     )
    figure.update_traces(
        mode="lines", hovertemplate=None,
        line=dict(width=3),
        connectgaps=True
    )

    figure.update_layout(
        hovermode="x",
        legend=dict(
            font=dict(
                family="Arial",
                size=15
            )
        ),
        hoverlabel=dict(
            font_size=13,
            font_family="Verdana"
        ),
    )
    return figure

# Generating the map
@app.callback(Output('graph-map', 'figure'),
              [Input('parameter-picker-timelines', 'value'),
              Input('date-picker-single', 'date'),
              ])
def update_figure(main_parameter, date):
    df2 = df.groupby('location')[['iso_code', 'location', 'date', main_parameter]].fillna(method='ffill')
    filtered_df = df2.loc[df2['date'] == date][['iso_code', 'location', 'date', main_parameter]]
    figure = go.Figure(px.choropleth(filtered_df,
                                     locations=filtered_df["iso_code"],
                                     color=filtered_df[main_parameter],
                                     hover_name=filtered_df['location'],
                                     hover_data={main_parameter: True, 'iso_code': False},
                                     projection='robinson',
                                     title=f'{main_parameter.replace("_", " ")}',
                                     color_continuous_scale=px.colors.sequential.Blues,
                                     labels={
                                         main_parameter: f'{main_parameter.replace("_", " ")}',
                                             },
                                     ))
    figure.update_traces(

    )

    # This is important for the colour scheme to adjust each time the parameter or the date is changed
    figure.update_coloraxes(cmin=(filtered_df[main_parameter].min())),
    figure.update_coloraxes(cmax=(filtered_df[main_parameter].max())),

    figure.update_layout(
        coloraxis_colorbar=dict(
            title=main_parameter.replace("_", " ")),
        hoverlabel=dict(
            font_size=13,
            font_family="Verdana"
        ),
            )
    return figure

# Generating the scatterplot
@app.callback(Output('graph-scatter', 'figure'),
              [
                  Input('date-picker-single', 'date'),
                  Input('parameter-picker-timelines', 'value'),
                  Input('parameter-picker-bars', 'value')
              ])
def update_figure(date, main_parameter, parameter_bars):
    df3 = df.groupby('location')[['continent', 'location', 'date', main_parameter, parameter_bars]].fillna(method='ffill')
    filtered_df = df3.loc[df3['date'] == date][['continent', 'location', main_parameter, parameter_bars]]
    filtered_df = filtered_df[filtered_df[main_parameter].notnull() & filtered_df[parameter_bars].notnull()][['continent', 'location', main_parameter, parameter_bars]]
    figure = px.scatter(filtered_df,
                    x=filtered_df[parameter_bars],
                    y=filtered_df[main_parameter],
                    color_discrete_sequence=px.colors.qualitative.G10,
                    color=filtered_df["continent"],
                    hover_name='location',
                    log_x=True,
                    log_y=True,
                    labels={parameter_bars:f'{parameter_bars.replace("_", " ")}', main_parameter:f'{main_parameter.replace("_", " ")}'},
                    opacity=0.5,

                    )
    figure.update_traces(
        hoverinfo='skip',
        textfont_size=25,
        marker={'size': 10}
    )
    figure.update_layout(
        legend=dict(font=dict(family="Arial",size=15)),
        hoverlabel=dict(
            font_size=13,
            font_family="Verdana"
        ),
                         )
    return figure


if __name__ == '__main__':
    app.run_server()