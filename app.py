import pickle as pickle

from dash import dcc, Input, html, Output, State
import dash_bootstrap_components as dbc
from dash_extensions.enrich import DashProxy, ServersideOutput, ServersideOutputTransform
import numpy as np

import plots


# Initialize app and server
app = DashProxy(
    external_stylesheets=[dbc.themes.SLATE],
    title='Unofficial F1 Viz',
    suppress_callback_exceptions=True,
    transforms=[ServersideOutputTransform()]
)

server = app.server

# Drop-down list info
with open('data/drop_down_data.pickle', 'rb') as handle:
    DROP_DOWN_DATA = pickle.load(handle)
DEFAULT_YEAR = list(DROP_DOWN_DATA.keys())[0]
DEFAULT_GPS = sorted(list(DROP_DOWN_DATA[DEFAULT_YEAR].keys()))
DEFAULT_GP = 'Azerbaijan'
TEL_PARAMS = ['Gear', 'Speed', 'Brake', 'Throttle']

# App layout
app.layout = dbc.Container(
    [
        dcc.Store(id='lap-data', storage_type='memory'),
        dcc.Store(id='tel-data', storage_type='memory'),
        html.Hr(),
        dcc.Markdown('''To get started, select a year and GP. Then navigate to one of the tabs below.'''),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id='year',
                            multi=False,
                            value=DEFAULT_YEAR,
                            options=[{'label': x, 'value': x} for x in [DEFAULT_YEAR]],
                            clearable=False
                        )
                    ], xs=6, sm=6, md=6, lg=3, xl=3
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id='grand-prix',
                            multi=False,
                            options=[{'label': x, 'value': x} for x in DEFAULT_GPS],
                            value=DEFAULT_GP,
                            clearable=False
                        )
                    ], xs=6, sm=6, md=6, lg=3, xl=3
                )
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Tabs(
                        [
                            dbc.Tab(label="Telemetry (All Sessions)", tab_id='tel-tab'),
                            dbc.Tab(label="Lap View (Race & Sprint Only)", tab_id='race-tab'),
                            dbc.Tab(label="Info", tab_id='welcome-tab')
                        ],
                        id='tabs',
                        active_tab='tel-tab'
                    )
                )
            ]
        ),
        html.Div(id='tab-content', className='p-4'),
    ]
)


def build_welcome_tab():
    """
    Builds the content for the welcome tab.
    """
    return html.Div(
        dcc.Markdown(
            children="""
                This site was developed to help fellow armchair analysts access Formula 1 data *regardless of their 
                coding ability*. Using data made available by the [Fast F1](https://github.com/theOehrly/Fast-F1) Python
                library ([MIT License](https://github.com/theOehrly/Fast-F1/blob/master/LICENSE) ), it provides users 
                with interactive visualizations that allow them to explore a race in detail. **To get started, select a
                year + GP at the top of  the page and click on the tab of interest.**
                
                If you want to tinker with the data in Python yourself, I found 
                [the examples](https://theoehrly.github.io/Fast-F1/examples_gallery/index.html) from the Fast F1 
                documentation to be helpful. 
                 
                Made with ❤   in Cambridge, MA.
                """
        )
    )


def build_lap_tab(year, grand_prix):
    """Builds the tab that shows lap summaries (delta, tyre strategy, lap times)."""

    # Get options and default values for dropdowns; exclude quali data if it exists
    sessions = list(DROP_DOWN_DATA[year][grand_prix].keys())
    if 'Qualifying' in sessions:
        sessions.remove('Qualifying')
    session = sessions[0]

    # delta_fig = plots.get_delta_viz(year, laps)
    delta_footer = """
        Use this visualization to see the delta between drivers and the winner over the race. 
        To add or remove a driver from the graph, tap/click their name in the legend once. To isolate a driver, 
        double tap/click their name in the legend.
        Circles represent pit stops. Background shading represents track status, tied to the winner's lap: yellow = 
        yellow flag, red = red flag, and white = (virtual) safety car.
    """

    # tyre_fig = plots.get_tyre_strategy_viz(laps)
    tyre_footer = """
        Use this visualization to see overall tyre strategy for the race
        (white = hard, yellow = medium, red = soft).
    """

    # lap_time_fig = plots.get_lap_time_heatmap(laps)
    lap_time_footer = """
        Use this visualization to get a bird's eye view of lap times over the race as a whole. 
        Hover to see a driver's lap time for a specific lap.
        
        A few notes:
        * Drivers are listed in order of final position
        * Color represents speed (red = slow, white = fast), pit stops are marked with an 
        asterisk, and missing lap time information is marked in charcoal
        * The colorscale is capped at a % of the fastest lap time. Any laps slower than that are 
        assigned the darkest shade of red."""

    content = [
        dbc.Row(
            dbc.Col(
                [
                    html.P("Select session:"),
                    dcc.Dropdown(
                        id='lap-tab-session',
                        multi=False,
                        value=session,
                        options=[{'label': x, 'value': x} for x in sessions],
                        clearable=False
                    ),
                ],
                xs=6, sm=12, md=12, lg=6, xl=6
            ),
        ),
        html.Br(),
        dbc.Row(
            dbc.Col(
                [
                    dcc.Loading(
                        children=[dcc.Graph(id='delta-viz', figure=plots.get_blank_fig())],
                        type='circle'
                    )
                ],
                width=12
            )
        ),
        dbc.Row(
            dbc.Col(dcc.Markdown(children=delta_footer))
        ),
        html.Br(),
        html.Hr(),
        html.Br(),
        dbc.Row(
            dbc.Col(
                [
                    dcc.Loading(
                        children=[dcc.Graph(id='tyre-strategy-viz', figure=plots.get_blank_fig())],
                        type='circle'
                    )
                ],
                width=12
            )
        ),
        dbc.Row(
            dbc.Col(dcc.Markdown(children=tyre_footer))
        ),
        html.Br(),
        html.Hr(),
        html.Br(),
        dbc.Row(
            dbc.Col(
                [
                    dcc.Loading(
                        children=[dcc.Graph(id='lap-time-viz', figure=plots.get_blank_fig())],
                        type='circle'
                    )
                ],
                width=12
            )
        ),
        dbc.Row(
            dbc.Col(dcc.Markdown(children=lap_time_footer))
        )
    ]

    return content


def build_tel_tab(year, grand_prix):
    """
    Builds the map view visualization tab.
    """

    # Get options and default values for dropdowns
    sessions = list(DROP_DOWN_DATA[year][grand_prix].keys())
    session = sessions[0]
    tel_param = TEL_PARAMS[0]

    summary_text = '''
        Use this visualization to compare the telemetry of various driver/session/lap combinations. 
        Please note that this data should not be used for precise calculations as it is a mix of 
        measured and interpolated values 
        ([more info](https://theoehrly.github.io/Fast-F1/howto_accurate_calculations.html?highlight=interpolation)).
        '''

    map_header = """
        To view a specific parameter on a map, select the parameter below. To see where a specific point on the map
        is on the graph above, click / tap the point on the map. This will create a vertical line on the graph above. 
        You can have 1 point selected per map at a time.
    """

    content = [
        dcc.Markdown(summary_text),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.P("Select session, driver, lap, and parameter:"),
                        dcc.Dropdown(
                            id='tel-session-1',
                            multi=False,
                            value=session,
                            options=[{'label': x, 'value': x} for x in sessions],
                            clearable=False
                        ),
                        html.Br(),
                        dcc.Dropdown(id='tel-driver-1', multi=False, clearable=False),
                        html.Br(),
                        dcc.Dropdown(id='tel-lap-1', multi=False, clearable=False)
                    ],
                    xs=12, sm=12, md=12, lg=6, xl=6
                ),
                dbc.Col(
                    [
                        html.P("Select session, driver, lap, and parameter:"),
                        dcc.Dropdown(
                            id='tel-session-2',
                            multi=False,
                            value=session,
                            options=[{'label': x, 'value': x} for x in sessions],
                            clearable=False
                        ),
                        html.Br(),
                        dcc.Dropdown(id='tel-driver-2', multi=False, clearable=False),
                        html.Br(),
                        dcc.Dropdown(id='tel-lap-2', multi=False, clearable=False)
                    ],
                    xs=12, sm=12, md=12, lg=6, xl=6
                )
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Loading(
                            children=[dcc.Graph(id='tel-line-graph', figure=plots.get_blank_fig())],
                            type='circle'
                        )
                    ],
                    width=12
                )
            ]
        ),
        html.Br(),
        html.Hr(),
        html.Br(),
        dcc.Markdown(map_header),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.P("Select parameter to view on map:"),
                        dcc.Dropdown(
                            id='tel-param-1',
                            multi=False,
                            value=tel_param,
                            options=[{'label': x, 'value': x} for x in TEL_PARAMS],
                            clearable=False
                        ),
                        dcc.Loading(children=[dcc.Graph(id='tel-map-1', figure=plots.get_blank_fig())], type='circle')
                    ],
                    xs=12, sm=12, md=12, lg=6, xl=6
                ),
                dbc.Col(
                    [
                        html.P("Select parameter to view on map:"),
                        dcc.Dropdown(
                            id='tel-param-2',
                            multi=False,
                            value=tel_param,
                            options=[{'label': x, 'value': x} for x in TEL_PARAMS],
                            clearable=False
                        ),
                        dcc.Loading(children=[dcc.Graph(id='tel-map-2', figure=plots.get_blank_fig())], type='circle')
                    ],
                    xs=12, sm=12, md=12, lg=6, xl=6
                )
            ]
        )
    ]

    return content


def get_driver_list(session, year, grand_prix, driver):
    """
    Gets the driver list for the selected year, Grand Prix, driver, and session.
    """

    drivers = list(DROP_DOWN_DATA[year][grand_prix][session.capitalize()].keys())
    if driver not in drivers:
        driver_val = drivers[0]
    else:
        driver_val = driver

    return [{'label': x, 'value': x} for x in drivers], driver_val


def get_laps_list(driver, year, grand_prix, session, lap):
    """
    Gets the lap options for the selected year, Grand Prix, driver, and session.
    """

    # Error handling checks that there is data for the user's selections (just in case....)
    try:
        laps = DROP_DOWN_DATA[year][grand_prix][session.capitalize()][driver]
    except Exception as err:
        lap_options = [{'label': 'No Lap Data', 'value': 'No Lap Data'}]
        lap_value = lap_options[0]['value']
        print(f"Map view 1 has unexpected {err=}, {type(err)=}")
    else:
        lap_options = [{'label': x, 'value': x} for x in laps]
        if lap in laps:
            lap_value = lap
        else:
            lap_value = np.nanmin(laps)

    return lap_options, lap_value


@app.callback(
    Output('grand-prix', 'options'),
    Output('grand-prix', 'value'),
    Input('year', 'value'),
    State('grand-prix', 'value')
)
def update_gp_options(year, grand_prix):
    """
    Updates the Grand Prix options for a selected year.
    """

    # Error handling checks that there is data for the user's selections (just in case....)
    try:
        gps = list(DROP_DOWN_DATA[year].keys())
    except Exception as err:
        gp_options = [{'label': 'No GP Data', 'value': 'No GP Data'}]
        gp_value = gp_options[0]['value']
        print(f"Map view 1 has unexpected {err=}, {type(err)=}")
    else:
        gp_options = [{'label': x, 'value': x} for x in gps]
        if grand_prix in gps:
            gp_value = grand_prix
        else:
            gp_value = gps[0]

    return gp_options, gp_value


@app.callback(
    ServersideOutput('tel-data', 'data', session_check=False),
    ServersideOutput('lap-data', 'data', session_check=False),
    Input('grand-prix', 'value'),
    State('year', 'value'),
    memoize=True
)
def store_gp_data(grand_prix, year):
    """
    Loads and stores (w/ serverside caching) the relevant grand prix's data.
    """

    filename = 'data/' + year + '/' + grand_prix.replace(' ', '_') + '.pickle'

    with open(filename, 'rb') as handle:
        gp_data = pickle.load(handle)

    return gp_data['telemetry_data'], gp_data['lap_data']


@app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'active_tab'),
    Input('lap-data', 'data'),
    State('year', 'value'),
    State('grand-prix', 'value')
)
def render_tab_content(active_tab, laps, year, grand_prix):
    """
    Renders the tab selected by the user.
    """

    # Default if user's selections are invalid
    content = "No data; try another selection."

    # Get content for user's selections
    if active_tab:
        if active_tab == 'welcome-tab':
            content = build_welcome_tab()
        elif year in DROP_DOWN_DATA.keys():
            if grand_prix in DROP_DOWN_DATA[year].keys():
                if active_tab == 'tel-tab':
                    content = build_tel_tab(year, grand_prix)
                elif (('Race' in laps.keys()) or ('Sprint' in laps.keys())) and (active_tab == 'race-tab'):
                    content = build_lap_tab(year, grand_prix)

    return content


@app.callback(
    Output('tel-driver-1', 'options'),
    Output('tel-driver-1', 'value'),
    Input('tel-session-1', 'value'),
    State('year', 'value'),
    State('grand-prix', 'value'),
    State('tel-driver-1', 'value')
)
def update_drivers_1(session, year, grand_prix, driver):
    """
    Updates the driver list for the selected year, Grand Prix, driver, and session (map view graph 1).
    """

    driver_list, driver_val = get_driver_list(session, year, grand_prix, driver)

    return driver_list, driver_val


@app.callback(
    Output('tel-lap-1', 'options'),
    Output('tel-lap-1', 'value'),
    Input('tel-driver-1', 'value'),
    State('year', 'value'),
    State('grand-prix', 'value'),
    State('tel-session-1', 'value'),
    State('tel-lap-1', 'value')
)
def update_laps_1(driver, year, grand_prix, session, lap):
    """
    Updates the lap options for the selected year, Grand Prix, driver, and session (map view graph 1).
    """

    lap_options, lap_value = get_laps_list(driver, year, grand_prix, session, lap)

    return lap_options, lap_value


@app.callback(
    Output('tel-map-1', 'figure'),
    Input('tel-lap-1', 'value', ),
    Input('tel-param-1', 'value'),
    Input('tel-map-1', 'clickData'),
    State('tel-session-1', 'value'),
    State('tel-driver-1', 'value'),
    State('lap-data', 'data'),
    State('tel-data', 'data')
)
def render_map_1(lap, param, click_data, session, driver, laps, telemetry):
    """
    Renders the first map view graph based on the user's selections.
    """

    if click_data:
        distance = click_data['points'][0]['meta']
    else:
        distance = None

    fig = plots.get_map_view(driver, param, lap, laps[session], telemetry[session], session, distance)

    return fig


@app.callback(
    Output('tel-driver-2', 'options'),
    Output('tel-driver-2', 'value'),
    Input('tel-session-2', 'value'),
    State('year', 'value'),
    State('grand-prix', 'value'),
    State('tel-driver-2', 'value')
)
def update_drivers_2(session, year, grand_prix, driver):
    """
    Updates the driver list for the selected year, Grand Prix, driver, and session (map view graph 2).
    """

    driver_list, driver_val = get_driver_list(session, year, grand_prix, driver)

    return driver_list, driver_val


@app.callback(
    Output('tel-lap-2', 'options'),
    Output('tel-lap-2', 'value'),
    Input('tel-driver-2', 'value'),
    State('year', 'value'),
    State('grand-prix', 'value'),
    State('tel-session-2', 'value'),
    State('tel-lap-2', 'value')
)
def update_laps_2(driver, year, grand_prix, session, lap):
    """
    Updates the lap options for the selected year, Grand Prix, driver, and session (map view graph 2).
    """

    lap_options, lap_value = get_laps_list(driver, year, grand_prix, session, lap)

    return lap_options, lap_value


@app.callback(
    Output('tel-map-2', 'figure'),
    Input('tel-lap-2', 'value', ),
    Input('tel-param-2', 'value'),
    Input('tel-map-2', 'clickData'),
    State('tel-session-2', 'value'),
    State('tel-driver-2', 'value'),
    State('lap-data', 'data'),
    State('tel-data', 'data')
)
def render_map_2(lap, param, click_data, session, driver, laps, telemetry):
    """
    Renders the second map view graph based on the user's selections.
    """

    if click_data:
        distance = click_data['points'][0]['meta']
    else:
        distance = None

    fig = plots.get_map_view(driver, param, lap, laps[session], telemetry[session], session, distance)

    return fig


@app.callback(
    Output('tel-line-graph', 'figure'),
    Input('tel-lap-1', 'value'),
    Input('tel-lap-2', 'value'),
    Input('tel-map-1', 'clickData'),
    Input('tel-map-2', 'clickData'),
    State('year', 'value'),
    State('tel-session-1', 'value'),
    State('tel-driver-1', 'value'),
    State('tel-session-2', 'value'),
    State('tel-driver-2', 'value'),
    State('lap-data', 'data'),
    State('tel-data', 'data')
)
def render_tel_line_graph(lap_1, lap_2, click_data_1, click_data_2, year, session_1, driver_1, session_2, driver_2,
                          laps, telemetry):
    """
    Renders the telemetry visualization based on the user's selections.
    """

    if click_data_1:
        distance_1 = click_data_1['points'][0]['meta']
    else:
        distance_1 = None
    if click_data_2:
        distance_2 = click_data_2['points'][0]['meta']
    else:
        distance_2 = None

    try:
        telemetry_1 = telemetry[session_1][
            (telemetry[session_1]['Driver'] == driver_1)
            & (telemetry[session_1]['LapNumber'] == lap_1)
        ]
        telemetry_2 = telemetry[session_2][
            (telemetry[session_2]['Driver'] == driver_2)
            & (telemetry[session_2]['LapNumber'] == lap_2)
        ]
        laps_1 = laps[session_1][laps[session_1]['Driver'] == driver_1]
        laps_2 = laps[session_2][laps[session_2]['Driver'] == driver_2]
    except Exception as err:
        fig = plots.get_no_race_data_fig()
        print(f"Tel view has unexpected {err=}, {type(err)=}")
    else:
        if (telemetry_1.shape[0] == 0) or (telemetry_2.shape[0] == 0):
            fig = plots.get_no_race_data_fig()
        else:
            fastest_lap_1 = int(laps_1.loc[laps_1['LapTime'].idxmin()]['LapNumber'])
            fastest_lap_2 = int(laps_2.loc[laps_2['LapTime'].idxmin()]['LapNumber'])
            fig = plots.get_tel_view(year, driver_1, driver_2, session_1, session_2, lap_1, lap_2, telemetry_1,
                                     telemetry_2, fastest_lap_1, fastest_lap_2, distance_1, distance_2)

    return fig


@app.callback(
    Output('delta-viz', 'figure'),
    Output('tyre-strategy-viz', 'figure'),
    Output('lap-time-viz', 'figure'),
    Input('lap-tab-session', 'value'),
    State('year', 'value'),
    State('lap-data', 'data')
)
def render_lap_tab(session, year, laps):
    """
    Renders visualizations for lap tab.
    """

    laps_session = laps[session]
    delta_fig = plots.get_delta_viz(year, laps_session)
    tyre_fig = plots.get_tyre_strategy_viz(laps_session)
    lap_time_fig = plots.get_lap_time_heatmap(laps_session)

    return delta_fig, tyre_fig, lap_time_fig

if __name__ == "__main__":
    app.run_server(debug=True)
