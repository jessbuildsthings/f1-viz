import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Figure formatting
BG_COLOR = '#272b30'
FONT_COLOR = 'white'
GRID_COLOR = '#32383e'
GRID_WIDTH = 1

# Plot colors
REDS = ['white', 'darkred']
REDS_R = ['darkred', 'white']

COMPOUND_COLORS = [[0, 'red'], [0.5, 'yellow'], [1, 'white']]

GEAR_SHIFT_COLORS = [
    [0, '#8a1fdb'],
    [1.0 / 7, '#541fdb'],
    [2.0 / 7, '#1f25db'],
    [3.0 / 7, '#1fbcdb'],
    [4.0 / 7, '#1fdb4b'],
    [5.0 / 7, '#dbc51f'],
    [6.0 / 7, '#db7a1f'],
    [1, '#db1f1f']
]

DRIVER_COLORS = {
    '2023': {
        'HAM': 'rgba(0, 210, 190, 0.9)',
        'RUS': 'rgba(0, 210, 190, 0.9)',
        'LEC': 'rgba(220, 0, 0, 0.9)',
        'SAI': 'rgba(220, 0, 0, 0.9)',
        'VER': 'rgba(6, 0, 239, 0.9)',
        'PER': 'rgba(6, 0, 239, 0.9)',
        'GAS': 'rgba(0, 144, 255, 0.9)',
        'OCO': 'rgba(0, 144, 255, 0.9)',
        'HUL': 'rgba(255, 255, 255, 0.9)',
        'MAG': 'rgba(255, 255, 255, 0.9)',
        'ALO': 'rgba(0, 111, 98, 0.9)',
        'STR': 'rgba(0, 111, 98, 0.9)',
        'DEV': 'rgba(43, 69, 98, 0.9)',
        'TSU': 'rgba(43, 69, 98, 0.9)',
        'NOR': 'rgba(255, 135, 0, 0.9)',
        'PIA': 'rgba(255, 135, 0, 0.9)',
        'BOT': 'rgba(144, 0, 0, 0.9)',
        'ZHO': 'rgba(144, 0, 0, 0.9)',
        'SAR': 'rgba(0, 90, 255, 0.9)',
        'ALB': 'rgba(0, 90, 255, 0.9)',
        'DRU': 'rgba(0, 111, 98, 0.9)',
        'RIC': 'rgba(43, 69, 98, 0.9)',
        'LAW': 'rgba(43, 69, 98, 0.9)'
    }
}

TRACK_STATUS_COLORS = {
    'Red': 'rgba(238, 75, 43, 0.25)',
    'Yellow': 'rgba(255, 255, 0, 0.25)',
    'Safety': 'rgba(255, 255, 255, 0.25)',
    'Virtual': 'rgba(255, 255, 255, 0.25)'
}

TRACK_COLOR = 'white'
TURN_COLOR = '#8803fc'

# Other plot formatting
MIN_GAP = 180
MAX_GAP = -10
MIN_SPEED = 50
MAX_SPEED = 350
MARKER_SIZE = 4
LINE_WIDTH = 2

PARAM_FORMAT = {
    'Speed': {
        'name': 'Speed',
        'hovertemplate_prefix': 'Speed: ',
        'hovertemplate_suffix': 'kph',
        'colorscale': REDS_R,
        'cmin': MIN_SPEED,
        'cmax': MAX_SPEED,
        'colorbar_title': 'Speed (kph)',
        'ymin': MIN_SPEED,
        'ymax': MAX_SPEED + 85,
        'ytitle': 'Speed (kph)'
    },
    'Throttle': {
        'name': 'Throttle',
        'hovertemplate_prefix': 'Throttle: ',
        'hovertemplate_suffix': '%',
        'colorscale': REDS_R,
        'cmin': 0,
        'cmax': 100,
        'ymax': 100.25,
        'colorbar_title': 'Throttle (%)',
        'ymin': -.25,
        'ytitle': 'Throttle (%)'
    },
    'Brake': {
        'name': 'Brake',
        'hovertemplate_prefix': 'Brake: ',
        'hovertemplate_suffix': '%',
        'colorscale': REDS_R,
        'colorbar_title': 'Brake (%)',
        'cmin': 0,
        'cmax': 100,
        'ymin': -.25,
        'ymax': 100.25,
        'ytitle': 'Brake (%)'
    },
    'Gear': {
        'name': 'nGear',
        'hovertemplate_prefix': '<i>Gear</i>: ',
        'hovertemplate_suffix': '',
        'colorscale': GEAR_SHIFT_COLORS,
        'cmin': 1,
        'cmax': 8,
        'colorbar_title': 'Gear',
        'ymin': 0.5,
        'ymax': 8.5,
        'ytitle': 'Gear'
    }
}


def get_default_fig():
    """
    Returns a figure with app's default formatting.
    """
    fig = go.Figure()

    fig.update_layout(
        plot_bgcolor=BG_COLOR,
        paper_bgcolor=BG_COLOR,
        font_color=FONT_COLOR
    )

    return fig


def get_blank_fig():
    """
    Returns a completely blank figure; used as temporary figure while data loads.
    """
    fig = go.Figure()

    fig.update_layout(
        plot_bgcolor=BG_COLOR,
        paper_bgcolor=BG_COLOR,
        font_color=FONT_COLOR,
    )

    fig.update_xaxes(
        showgrid=False,
        showticklabels=False,
        zeroline=False
    )

    fig.update_yaxes(
        showgrid=False,
        showticklabels=False,
        zeroline=False
    )

    return fig


def get_no_race_data_fig():
    """
    Returns a message that race data is not yet available (as a  figure).
    """

    fig = {
        'layout': {
            'xaxis': {
                'visible': False
            },
            'yaxis': {
                'visible': False
            },
            'annotations': [
                {
                    'text': "No data; try another selection.",
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {
                        'size': 20
                    }
                }
            ],
            'plot_bgcolor': BG_COLOR,
            'paper_bgcolor': BG_COLOR
        }
    }

    return fig


def get_lap_time_heatmap(laps):
    """
    Creates a heatmap visualization of the grand prix's lap time by driver.
    """

    # Pivot raw data to get a dataframe of Driver x Lap x Lap Time
    lap_times_pivot = pd.pivot_table(
        laps[['Driver', 'LapNumber', 'LapTime']],
        values='LapTime',
        index=['Driver'],
        columns=['LapNumber'],
        aggfunc=np.max,
        dropna=False
    )
    lap_times_pivot.reset_index(inplace=True)

    # Order lap times and drivers by final position (for plotting purposes)
    position = laps[['Driver', 'Position']].drop_duplicates()
    lap_times_pivot = lap_times_pivot.merge(position, how='left', on='Driver')
    lap_times_pivot.sort_values(by='Position', ascending=False, inplace=True, ignore_index=True)
    drivers = lap_times_pivot['Driver'].unique()
    n_drivers = drivers.size

    # Remove columns not needed in plot
    lap_times_pivot = lap_times_pivot.drop(labels=['Driver', 'Position'], axis=1)

    # Convert to an array in second, with nan where data is missing.
    # Note: time_pivot is a timedelta64 in ns. NaT converts to a negative number, so we rewrite those as np.nan.
    lap_times_array = lap_times_pivot.to_numpy(dtype='float64') / 1000000000
    lap_times_array[lap_times_array < 0] = np.nan

    # Get the pit stops. Creates an n_driver x n_laps array with asterisks where there are pit stops. This is used to
    # layer text over the heatmap to represent pit stops.
    pit_stops = laps.loc[laps['PitStop'], ['LapNumber', 'Position']]
    pit_stops = pit_stops[pit_stops['LapNumber'].between(1, lap_times_array.shape[1])]
    pit_stops = pit_stops.astype({'Position': 'int8', 'LapNumber': 'int8'})
    pit_stops_array = np.empty(lap_times_array.shape, dtype='str')
    pit_stops_array[n_drivers - pit_stops['Position'].values, pit_stops['LapNumber'].values - 1] = '*'

    # Calculate the slowest time to include in the colorbar. This prevents outliers (e.g., safety car laps) from
    # dominating the colorbar and drowning out variation in lap time for other laps
    fastest_time = np.nanmin(lap_times_array)
    slowest_time = fastest_time * 1.1

    # Create the heatmap and update the layout
    lap_time_heatmap = get_default_fig()

    lap_time_heatmap.add_trace(
        go.Heatmap(
            x=np.arange(1, lap_times_array.shape[1] + 1),
            y=drivers,
            z=lap_times_array,
            text=pit_stops_array,
            texttemplate="%{text}",
            colorbar=dict(title="Lap Time (s)"),
            colorscale=REDS,
            zmax=slowest_time,
            zmin=fastest_time,
            hovertemplate='Lap: %{x}<br>Driver: %{y}<br>Lap Time: %{z}s<extra></extra>'
        )
    )

    lap_time_heatmap.update_layout(
        title_text="Lap Times",
        xaxis_title="Lap",
        yaxis_nticks=len(drivers),
        xaxis_showgrid=False,
        yaxis_showgrid=False,
        xaxis_zeroline=False,
        yaxis_zeroline=False,
        margin=dict(t=30, l=4, r=4, b=4)
    )

    return lap_time_heatmap


def get_delta_viz(year, laps):
    """
    Creates a line graph that shows each driver's delta to the winner of the race, by lap.
    """

    # Get track status relative to winner's lap number
    laps_winner = laps[laps['Position'] == 1]
    track_status = laps_winner[~laps_winner['Nominal']]

    # Create default figure
    delta_view = get_default_fig()

    # Add background shading for track status
    for status, color in TRACK_STATUS_COLORS.items():
        active_laps = track_status[track_status[status]]
        delta_view.add_trace(
            go.Bar(
                x=active_laps.LapNumber,
                y=[laps['DeltaWinner'].max()] * active_laps.shape[0],
                width=[1] * active_laps.shape[0],
                marker_color=color,
                marker_line_width=0,
                showlegend=False,
                hoverinfo='skip'
            )
        )

    # Add a line for each driver and markers for their pit stops
    colors_used = []
    for driver in sorted(laps['Driver'].unique(), reverse=True):
        # Use a dashed line if driver's teammate already appears on graph
        color = DRIVER_COLORS[year][driver]
        if color in colors_used:
            dash_style = 'dash'
        else:
            dash_style = None
        colors_used.append(color)

        # Get driver's data
        laps_driver = laps[laps['Driver'] == driver]

        # Add the line
        delta_view.add_trace(
            go.Scatter(
                legendgroup=driver,
                name=driver,
                x=laps_driver['LapNumber'],
                y=laps_driver['DeltaWinner'],
                meta=laps_driver.Driver,
                hovertemplate="Driver: %{meta} <br /br>Lap: %{x} <br />Delta: %{y}s<extra></extra>",
                line=dict(color=color, dash=dash_style)
            )
        )

        # Add markers for pit stops
        pit_driver = laps_driver[laps_driver['PitStop']]
        delta_view.add_trace(
            go.Scatter(
                legendgroup=driver,
                name=driver,
                x=pit_driver['LapNumber'],
                y=pit_driver['DeltaWinner'],
                meta=pit_driver.Driver,
                hovertemplate="Driver: %{meta} <br /br>Lap: %{x} <br />Delta to Winner: %{y}<extra></extra> <br />Pit",
                mode='markers',
                marker=dict(color=color, size=MARKER_SIZE * 1.5),
                showlegend=False
            )
        )

    # Update formatting
    delta_view.update_xaxes(
        range=[0, laps['LapNumber'].max() + 1],
        gridwidth=GRID_WIDTH,
        gridcolor=GRID_COLOR,
        title_text='Lap'
    )

    delta_view.update_yaxes(
        range=[min(MIN_GAP, laps['DeltaWinner'].max()), max(MAX_GAP, laps['DeltaWinner'].min() - 5)],
        gridwidth=GRID_WIDTH,
        gridcolor=GRID_COLOR,
        showline=False,
        zeroline=False,
        title_text="Delta (s)"
    )

    delta_view.update_layout(
        title_text="Delta by Lap",
        legend_traceorder="reversed",
        margin=dict(t=30, l=4, r=4, b=4)
    )

    return delta_view


def get_tyre_strategy_viz(laps):
    """
    Returns a horizontal stacked bar chart showing the tyres used by each driver over the course of the race.
    """

    # Get the stints and their length for each driver in order of final position
    laps = laps[['Driver', 'Stint', 'Position', 'LapNumber', 'Compound']]
    agg_funcs = {
        'LapNumber': ['max', 'min'],
        'Compound': ['first']
    }
    stints = laps.groupby(by=['Driver', 'Stint', 'Position'], as_index=False).agg(agg_funcs)
    stints.columns = ['_'.join(col).rstrip('_') for col in stints.columns.values]
    stints.rename(
        columns={
            'Compound_first': 'Compound',
            'LapNumber_min': 'StintStart',
            'LapNumber_max': 'StintEnd'
        },
        inplace=True
    )
    stints['StintLength'] = stints['StintEnd'] - stints['StintStart'] + 1
    stints['Compound'] = stints['Compound'].str.lower()
    stints.sort_values(by=['Position', 'Stint'], ascending=[False, True], inplace=True)

    # Map compound to a colormap for plotting. Note: Random numbers added to avoid having the stacked bar chart group
    # all compounds of the same type.
    stints['PlotColor'] = 0
    stints.loc[stints['Compound'] == 'medium', 'PlotColor'] = 0.5
    stints.loc[stints['Compound'] == 'hard', 'PlotColor'] = 1
    stints['PlotColor'] = stints['PlotColor'] + np.random.rand(stints.shape[0]) / 100

    # Build the graph and adjust layout
    tyre_strategy_view = get_default_fig()

    tyre_strategy_view.add_trace(
        go.Bar(
            x=stints.StintLength,
            y=stints.Driver,
            meta=stints.Compound,
            marker_color=stints.PlotColor,
            marker_colorscale=COMPOUND_COLORS,
            marker_line_color=BG_COLOR,
            marker_colorbar_title="Tyre",
            marker_colorbar_tickmode='array',
            marker_colorbar_tickvals=[0.01, 0.5, 1],
            marker_colorbar_ticktext=["Soft", "Medium", "Hard"],
            orientation='h',
            hoverinfo='skip'
        )
    )

    tyre_strategy_view.update_xaxes(
        range=[1, stints.StintEnd.max() + 1],
        gridcolor=GRID_COLOR,
        gridwidth=GRID_WIDTH,
        title_text="Lap"
    )

    tyre_strategy_view.update_layout(
        title_text="Tyre Strategy",
        margin=dict(t=50, b=50, l=4, r=4),
    )

    return tyre_strategy_view


def get_map_view(driver, map_view_param, lap_num, laps, telemetry, session, distance):
    """
    Returns telemetry data on a map view for on the user's selections
    """

    # Create map view; return "no race data graph" if there is no data for user's selections (just in case)
    try:
        telemetry_driver = telemetry[telemetry['Driver'] == driver]
        laps_driver = laps[laps['Driver'] == driver]
    except Exception as err:
        map_view = get_no_race_data_fig()
        print(f"Map view 1 has unexpected {err=}, {type(err)=}")
    else:
        if telemetry_driver[telemetry_driver['LapNumber'] == lap_num].shape[0] == 0:
            map_view = get_no_race_data_fig()
        else:
            fastest_lap_num = int(laps_driver.loc[laps_driver['LapTime'].idxmin()]['LapNumber'])
            telemetry_driver_lap = telemetry_driver[telemetry_driver['LapNumber'] == lap_num]

            map_view = get_default_fig()

            map_view.add_scatter(
                x=telemetry_driver_lap.X,
                y=telemetry_driver_lap.Y,
                meta=telemetry_driver_lap.Distance,
                mode='markers',
                marker_color=telemetry_driver_lap[PARAM_FORMAT[map_view_param]['name']],
                marker_colorscale=PARAM_FORMAT[map_view_param]['colorscale'],
                marker_cmax=PARAM_FORMAT[map_view_param]['cmax'],
                marker_cmin=PARAM_FORMAT[map_view_param]['cmin'],
                marker_colorbar_title=PARAM_FORMAT[map_view_param]['colorbar_title'],
                marker_showscale=True,
                marker_size=MARKER_SIZE,
                hovertemplate=PARAM_FORMAT[map_view_param]['hovertemplate_prefix'] + '%{marker.color}<extra></extra>' +
                              PARAM_FORMAT[map_view_param]['hovertemplate_suffix'],
                showlegend=False
            )

            # If the user selects a point on the map (or there is a pre-existing selection), make it white.
            # Note: This searches for the closest point in the current driver's telemetry because the selection may
            #   carry over from a different configuration for this map (e.g., a different lap than the current one).
            if distance:
                closest_point = np.argmin(np.abs(telemetry_driver_lap.Distance.values - distance))

                map_view.add_scatter(
                    x=[telemetry_driver_lap.iloc[closest_point]['X']],
                    y=[telemetry_driver_lap.iloc[closest_point]['Y']],
                    meta=[telemetry_driver_lap.iloc[closest_point]['Distance']],
                    mode='markers',
                    marker_color=TRACK_COLOR,
                    marker_size=MARKER_SIZE * 2,
                    showlegend=False,
                    hoverinfo='skip'
                )

            map_view.update_xaxes(
                showgrid=False,
                showline=False,
                zeroline=False,
                showticklabels=False
            )

            map_view.update_yaxes(
                scaleanchor="x",
                scaleratio=1,
                showgrid=False,
                showline=False,
                zeroline=False,
                showticklabels=False
            )

            map_view.update_layout(
                title_text=driver + " " + session + " Lap " + str(lap_num) + " (Fastest Lap = " + str(
                    fastest_lap_num) + ")"
            )

    return map_view


def get_tel_view(year, driver_1, driver_2, session_1, session_2, lap_num_1, lap_num_2, telemetry_1, telemetry_2,
                 fastest_lap_1, fastest_lap_2, distance_1, distance_2):
    """
    Creates line graphs to compare two drivers' telemetry data (speed, brake, throttle, gear) over their fastest laps
    """

    # Putting selection data into a dictionary to make plotting easier
    selections = {
        'Driver 1': {
            'Driver': driver_1,
            'Session': session_1,
            'Lap': lap_num_1,
            'Color': DRIVER_COLORS[year][driver_1],
            'Telemetry': telemetry_1,
            'Fastest Lap': fastest_lap_1,
            'Distance': distance_1
        },
        'Driver 2': {
            'Driver': driver_2,
            'Session': session_2,
            'Lap': lap_num_2,
            'Color': DRIVER_COLORS[year][driver_2],
            'Telemetry': telemetry_2,
            'Fastest Lap': fastest_lap_2,
            'Distance': distance_2
        }
    }

    # If both drivers are on the same team, change second's color to a non-team color to avoid confusion
    if selections['Driver 1']['Color'] == selections['Driver 2']['Color']:
        selections['Driver 2']['Color'] = 'rgba(204, 136, 153, 0.9)'

    # Add a 4x1 subplot region
    tel_view = get_default_fig()

    tel_view.set_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_width=[0.2, 0.15, 0.15, .35]
    )

    # Add each driver's data
    for selection in selections.values():
        i = 0
        for param, form in PARAM_FORMAT.items():
            i += 1
            if i == 1:
                showlegend = True
            else:
                showlegend = False
            tel_view.add_trace(
                go.Scatter(
                    name=selection['Driver'] + " " + selection['Session'] + " Lap " + str(
                        selection['Lap']) + " (Fastest Lap = " + str(selection['Fastest Lap']) + ")",
                    x=selection['Telemetry']['Distance'],
                    y=selection['Telemetry'][form['name']],
                    hovertemplate="Driver: " + selection['Driver'] + "<br /br>Session: " + selection[
                        'Session'] + "<br /br/>Distance: %{x}m <br />" + param + ": %{y} " + form[
                                      'hovertemplate_suffix'] + "<extra></extra>",
                    line_color=selection['Color'],
                    line_width=LINE_WIDTH,
                    showlegend=showlegend
                ),
                row=i,
                col=1
            )

            # Add vertical line for distance selected on this driver's map (if applicable)
            if selection['Distance']:
                tel_view.add_trace(
                    go.Scatter(
                        x=[selection['Distance'], selection['Distance']],
                        y=[-1000, 1000],
                        mode='lines',
                        hovertemplate='None',
                        showlegend=False,
                        line_color=selection['Color'],
                        line_width=LINE_WIDTH,
                        line_dash='dash'
                    ),
                    row=i,
                    col=1
                )

            tel_view.update_yaxes(
                range=[form['ymin'], form['ymax']],
                title_text=form['ytitle'],
                row=i,
                col=1
            )

    # Format the figure, grids, and axes
    tel_view.update_layout(
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            orientation="h",
            bgcolor="rgba(0,0,0,0)"
        ),
        height=600,
        xaxis_showticklabels=True,
        xaxis_title_text="Distance (m)",
        xaxis_side="top",
        xaxis4_title_text="Distance (m)",
        margin=dict(t=4, l=4, r=16, b=4)
    )

    tel_view.update_yaxes(
        gridwidth=GRID_WIDTH,
        gridcolor=GRID_COLOR,
        showline=False,
        zeroline=False
    )

    tel_view.update_xaxes(
        gridwidth=GRID_WIDTH,
        gridcolor=GRID_COLOR,
    )

    tel_view.update_traces(xaxis="x4")

    return tel_view
