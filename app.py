import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Load data
df = pd.read_csv("shots.csv")
df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'], format='%Y%m%d')
df['GAME_DATE_STR'] = df['GAME_DATE'].dt.strftime('%m/%d/%Y')

# Dash app setup
app = dash.Dash(__name__)
server = app.server

# Get unique player names
players = sorted(df['PLAYER_NAME'].dropna().unique())

def draw_plotly_court(fig, fig_width=600, margins=10):
    def ellipse_arc(x_center=0.0, y_center=0.0, a=10.5, b=10.5, start_angle=0.0, end_angle=2 * np.pi, N=200, closed=False):
        t = np.linspace(start_angle, end_angle, N)
        x = x_center + a * np.cos(t)
        y = y_center + b * np.sin(t)
        path = f'M {x[0]}, {y[0]}'
        for k in range(1, len(t)):
            path += f'L{x[k]}, {y[k]}'
        if closed:
            path += ' Z'
        return path

    fig_height = fig_width * (470 + 2 * margins) / (500 + 2 * margins)
    fig.update_layout(width=fig_width, height=fig_height)

    fig.update_xaxes(range=[-250 - margins, 250 + margins])
    fig.update_yaxes(range=[-52.5 - margins, 417.5 + margins])

    threept_break_y = 89.47765084
    three_line_col = "#000000"
    main_line_col = "#000000"

    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        yaxis=dict(
            scaleanchor="x",
            scaleratio=1,
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=False,
            fixedrange=True,
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=False,
            fixedrange=True,
        ),
        shapes=[
            dict(
                type="rect", x0=-250, y0=-52.5, x1=250, y1=417.5,
                line=dict(color=main_line_col, width=1),
                layer='below'
            ),
            # Outer paint box
            dict(
                type="rect", x0=-80, y0=-52.5, x1=80, y1=137.5,
                line=dict(color=main_line_col, width=1),
                layer='below'
            ),
            dict(
                type="circle", x0=-60, y0=77.5, x1=60, y1=197.5, xref="x", yref="y",
                line=dict(color=main_line_col, width=1),
                layer='below'
            ),

            # Removed the horizontal line inside paint at y=137.5

            dict(
                type="rect", x0=-2, y0=-7.25, x1=2, y1=-12.5,
                line=dict(color=main_line_col, width=1),
                fillcolor=main_line_col,
            ),
            dict(
                type="circle", x0=-7.5, y0=-7.5, x1=7.5, y1=7.5, xref="x", yref="y",
                line=dict(color=main_line_col, width=1),
            ),
            dict(
                type="line", x0=-30, y0=-12.5, x1=30, y1=-12.5,
                line=dict(color=main_line_col, width=1),
            ),

            dict(type="path",
                 path=ellipse_arc(a=40, b=40, start_angle=0, end_angle=np.pi),
                 line=dict(color=main_line_col, width=1), layer='below'),
            dict(type="path",
                 path=ellipse_arc(a=237.5, b=237.5, start_angle=0.386283101, end_angle=np.pi - 0.386283101),
                 line=dict(color=main_line_col, width=1), layer='below'),
            dict(
                type="line", x0=-220, y0=-52.5, x1=-220, y1=threept_break_y,
                line=dict(color=three_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=220, y0=-52.5, x1=220, y1=threept_break_y,
                line=dict(color=three_line_col, width=1), layer='below'
            ),

            dict(
                type="line", x0=-250, y0=227.5, x1=-220, y1=227.5,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=250, y0=227.5, x1=220, y1=227.5,
                line=dict(color=main_line_col, width=1), layer='below'
            ),

            dict(type="path",
                 path=ellipse_arc(y_center=417.5, a=60, b=60, start_angle=-0, end_angle=-np.pi),
                 line=dict(color=main_line_col, width=1), layer='below'),
        ]
    )
    return True

def ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[((n//10%10!=1)*(n%10<4)*n%10)::4])


app.layout = html.Div([
    html.H1("NBA Shot Chart"),
    dcc.Dropdown(
    id='player-dropdown',
    options=[{'label': name, 'value': name} for name in players],
    value=players[0],  # <- Set default
    placeholder="Select a player"
    ),
    html.Div(id='player-stats', style={'marginTop': '20px'}),
    html.Div([
        dcc.Graph(id='shot-chart', style={'flex': '2'}),
        html.Img(id='player-headshot', style={'height': '300px', 'marginLeft': '40px'})
    ], style={'display': 'flex', 'alignItems': 'center'})
])

@app.callback(
    Output('shot-chart', 'figure'),
    Output('player-headshot', 'src'),
    Output('player-stats', 'children'),  # New Output
    Input('player-dropdown', 'value')
)

def update_chart(player):
    fig = go.Figure()
    draw_plotly_court(fig)
    fig.update_layout(showlegend=False)

    if player is None:
        return fig, ""

    player_data = df[df['PLAYER_NAME'] == player]
    if player_data.empty:
        return fig, ""
    
    period_ordinal = player_data['PERIOD'].apply(ordinal)
    seconds_padded = player_data['SECONDS_REMAINING'].apply(lambda x: f"{int(x):02d}")

    fig.add_trace(go.Scatter(
    x=player_data['LOC_X'],
    y=player_data['LOC_Y'],
    mode='markers',
    marker=dict(
        color=np.where(player_data['SHOT_MADE_FLAG'] == 1, 'green', 'red'),
        size=6,
        opacity=0.7
    ), customdata=np.stack([
        player_data['GAME_DATE_STR'],    # 0
        player_data['HTM'],              # 1
        player_data['VTM'],              # 2
        period_ordinal,                   # 3 (local variable)
        player_data['MINUTES_REMAINING'],  # 4
        seconds_padded,                   # 5 (local variable)
    ], axis=-1),
    hovertemplate=(
        "%{customdata[1]} vs %{customdata[2]} on %{customdata[0]}<br>" +
        "%{customdata[3]} Qtr, %{customdata[4]}:%{customdata[5]} remaining<br>" +
        "<extra></extra>"
    )
    ))

    fig.update_layout(
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_color="black",
            font_family="Arial"
        )
    )

    # Calculate stats:
    total_shots = len(player_data)
    made_shots = player_data['SHOT_MADE_FLAG'].sum()
    fg_percent = made_shots / total_shots if total_shots > 0 else 0

    # Three pointers
    three_pt_shots = player_data[player_data['SHOT_TYPE'].str.contains('3PT')]
    made_3pt = three_pt_shots['SHOT_MADE_FLAG'].sum()
    three_pt_percent = made_3pt / len(three_pt_shots) if len(three_pt_shots) > 0 else 0

    # Effective FG%: (FGM + 0.5*3PM) / FGA
    efg = (made_shots + 0.5 * made_3pt) / total_shots if total_shots > 0 else 0

    stats_text = (
        f"Field Goal %: {fg_percent:.1%} | "
        f"3PT %: {three_pt_percent:.1%} | "
        f"eFG%: {efg:.1%}"
    )

    player_id = player_data['PLAYER_ID'].iloc[0]
    img_url = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png"

    return fig, img_url, stats_text

def display_selection_stats(selectedData, player):
    if not selectedData or not player:
        return "Select an area to see shooting percentages."

    points = selectedData.get('points', [])
    if len(points) == 0:
        return "No shots selected."

    # Extract indices of selected points from 'pointIndex' or from x/y coordinates
    selected_points = []
    for pt in points:
        # 'pointIndex' is the index of the point in the trace
        selected_points.append(pt['pointIndex'])

    # Filter player data again to match the points
    player_data = df[df['PLAYER_NAME'] == player].reset_index(drop=True)
    selected_shots = player_data.iloc[selected_points]

    if selected_shots.empty:
        return "No shots selected."

    total_shots = len(selected_shots)
    made_shots = selected_shots['SHOT_MADE_FLAG'].sum()

    # Three pointers?
    three_point_shots = selected_shots[selected_shots['SHOT_TYPE'].str.contains('3PT')]
    three_point_made = three_point_shots['SHOT_MADE_FLAG'].sum()

    fg_pct = made_shots / total_shots * 100 if total_shots > 0 else 0
    three_pt_pct = (three_point_made / len(three_point_shots) * 100) if len(three_point_shots) > 0 else None

    # eFG% = (FGM + 0.5 * 3PM) / FGA
    efg = (made_shots + 0.5 * three_point_made) / total_shots * 100 if total_shots > 0 else 0

    three_pt_text = f"{three_pt_pct:.1f}%" if three_pt_pct is not None else "N/A"

    return html.Div([
        html.Strong(f"Shots selected: {total_shots}"),
        html.Br(),
        f"Field Goal %: {fg_pct:.1f}%",
        html.Br(),
        f"3PT %: {three_pt_text}",
        html.Br(),
        f"eFG %: {efg:.1f}%",
    ])

if __name__ == '__main__':
    app.run(debug=False, dev_tools_ui=False, dev_tools_props_check=False)