import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Load shot data
@st.cache_data
def load_data():
    return pd.read_csv("shots.csv")

df = load_data()

df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'], format='%Y%m%d')
df['GAME_DATE_STR'] = df['GAME_DATE'].dt.strftime('%m/%d/%Y')

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
    three_line_col = "#777777"
    main_line_col = "#777777"

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
                line=dict(color="#ec7607", width=1),
                fillcolor='#ec7607',
            ),
            dict(
                type="circle", x0=-7.5, y0=-7.5, x1=7.5, y1=7.5, xref="x", yref="y",
                line=dict(color="#ec7607", width=1),
            ),
            dict(
                type="line", x0=-30, y0=-12.5, x1=30, y1=-12.5,
                line=dict(color="#ec7607", width=1),
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

def calculate_player_stats(df):
    total_fga = len(df)  # Field Goal Attempts
    total_fgm = df['SHOT_MADE_FLAG'].sum()  # Field Goals Made
    
    # Three-point shots (distance >= 23.75 feet)
    three_pt_mask = df['SHOT_DISTANCE'] >= 23.75
    three_pt_attempts = three_pt_mask.sum()
    three_pt_made = df.loc[three_pt_mask, 'SHOT_MADE_FLAG'].sum()
    
    fg_pct = total_fgm / total_fga if total_fga > 0 else np.nan
    three_pt_pct = three_pt_made / three_pt_attempts if three_pt_attempts > 0 else np.nan
    
    # Effective Field Goal Percentage formula: (FGM + 0.5 * 3PM) / FGA
    efg_pct = (total_fgm + 0.5 * three_pt_made) / total_fga if total_fga > 0 else np.nan
    
    return fg_pct, three_pt_pct, efg_pct

def round_to_tenth_percent(x):
    return round(x * 100, 1)

players = sorted(df['PLAYER_NAME'].unique())
selected_player = st.selectbox("Select a player", players)

# Filter shots for selected player
player_shots = df[df['PLAYER_NAME'] == selected_player]

# Create figure and draw court
fig = go.Figure()
draw_plotly_court(fig)

# Add shots as scatter points
fig.add_trace(go.Scatter(
    x=player_shots['LOC_X'],
    y=player_shots['LOC_Y'],
    mode='markers',
    marker=dict(
        color=np.where(player_shots['SHOT_MADE_FLAG'] == 1, 'green', 'red'),
        size=6,
        opacity=0.7
    ),
    name='',
    hovertemplate=(
        "Distance: %{customdata[0]:} ft<br>" +
        "Period: %{customdata[2]}<br>" +
        "Time Left: %{customdata[3]}m %{customdata[4]}s<br>" +
        "%{customdata[5]} vs %{customdata[6]} on %{customdata[1]}"  # Teams and formatted date
    ),
    customdata=np.stack([
        player_shots['SHOT_DISTANCE'],         # 0
        player_shots['GAME_DATE_STR'],         # 1 (formatted date)
        player_shots['PERIOD'],                # 2
        player_shots['MINUTES_REMAINING'],    # 3
        player_shots['SECONDS_REMAINING'],    # 4
        player_shots['HTM'],                   # 5 (home team)
        player_shots['VTM'],                   # 6 (visitor team)
    ], axis=-1)
))

fig.update_layout(showlegend=False)

st.plotly_chart(fig, use_container_width=True)

fg_pct, three_pt_pct, efg_pct = calculate_player_stats(player_shots)

if not np.isnan(fg_pct):
    st.markdown(f"**Field Goal %:** {round_to_tenth_percent(fg_pct)}%")
else:
    st.markdown("**Field Goal %:** No shots taken")

if not np.isnan(three_pt_pct):
    st.markdown(f"**Three Point %:** {round_to_tenth_percent(three_pt_pct)}%")
else:
    st.markdown("**Three Point %:** No 3PT attempts")

if not np.isnan(efg_pct):
    st.markdown(f"**Effective Field Goal %:** {round_to_tenth_percent(efg_pct)}%")
else:
    st.markdown("**Effective Field Goal %:** No shots taken")