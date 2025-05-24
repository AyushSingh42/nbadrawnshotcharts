import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from court_plot import draw_nba_half_court

# Load shot data
df = pd.read_csv("shots.csv")

# Sidebar: Player selector
player_names = sorted(df['player_name'].unique())
selected_player = st.sidebar.selectbox("Select a Player", player_names)

# Filter for selected player
player_data = df[df['player_name'] == selected_player]

# Plot court
fig, ax = plt.subplots(figsize=(10, 9))
draw_nba_half_court(ax)

# Plot shots
made = player_data[player_data['shot_made_flag'] == 1]
missed = player_data[player_data['shot_made_flag'] == 0]

ax.scatter(made['x'], made['y'], c='green', label='Made', alpha=0.6, edgecolors='k')
ax.scatter(missed['x'], missed['y'], c='red', label='Missed', alpha=0.4, edgecolors='k')
ax.legend()

st.pyplot(fig)