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
        placeholder="Select a player"
    ),
    dcc.Graph(id='shot-chart')
])

@app.callback(
    Output('shot-chart', 'figure'),
    Input('player-dropdown', 'value')
)
def update_chart(player):
    fig = go.Figure()
    draw_plotly_court(fig)
    if player is None:
        return fig

    player_shots = df[df['PLAYER_NAME'] == player]
    made = player_shots[player_shots['SHOT_MADE_FLAG'] == 1]
    missed = player_shots[player_shots['SHOT_MADE_FLAG'] == 0]

    # Create a new column in your DataFrame for ordinal quarter string
    player_shots['PERIOD_ORDINAL'] = player_shots['PERIOD'].apply(ordinal)

    # Create a zero-padded seconds string column
    player_shots['SECONDS_PADDED'] = player_shots['SECONDS_REMAINING'].apply(lambda x: f"{int(x):02d}")

    fig.add_trace(go.Scatter(
    x=player_shots['LOC_X'],
    y=player_shots['LOC_Y'],
    mode='markers',
    marker=dict(
        color=np.where(player_shots['SHOT_MADE_FLAG'] == 1, 'green', 'red'),
        size=6,
        opacity=0.7
    ),
    customdata=np.stack([
        player_shots['GAME_DATE_STR'],       # 0
        player_shots['HTM'],                 # 1
        player_shots['VTM'],                 # 2
        player_shots['PERIOD_ORDINAL'],     # 3
        player_shots['MINUTES_REMAINING'],  # 4
        player_shots['SECONDS_PADDED'],     # 5
    ], axis=-1),
    hovertemplate=(
        "%{customdata[1]} vs %{customdata[2]} on %{customdata[0]}<br>" +
        "%{customdata[3]} Qtr, %{customdata[4]}:%{customdata[5]} remaining<br>" +
        "<extra></extra>"
    )
    ))

    fig.update_layout(
        hoverlabel=dict(
            bgcolor="white",  # hover background color
            font_size=12,
            font_color="black",
            font_family="Arial"
        )
    )

    return fig

if __name__ == '__main__':
    app.run(debug=False, dev_tools_ui=False, dev_tools_props_check=False)