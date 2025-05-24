import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_nba_half_court(ax=None, court_color='white', line_color='black', lw=2):
    if ax is None:
        fig, ax = plt.subplots(figsize=(15, 14))
    
    # Court elements
    hoop = patches.Circle((25, 5.25), radius=0.75, linewidth=lw, color=line_color, fill=False)
    backboard = patches.Rectangle((22, 4), 6, 0.1, linewidth=lw, color=line_color)
    paint = patches.Rectangle((17, 0), 16, 19, linewidth=lw, color=line_color, fill=False)
    free_throw_top = patches.Circle((25, 19), 6, linewidth=lw, color=line_color, fill=False)
    free_throw_bottom = patches.Circle((25, 19), 6, linewidth=lw, color=line_color, linestyle='dashed', fill=False)
    
    # Restricted area
    restricted = patches.Arc((25, 5.25), 8, 8, theta1=0, theta2=180, linewidth=lw, color=line_color)

    # 3pt line
    corner3_left = patches.Rectangle((3, 0), 0.1, 14, linewidth=lw, color=line_color)
    corner3_right = patches.Rectangle((47, 0), 0.1, 14, linewidth=lw, color=line_color)
    three_arc = patches.Arc((25, 5.25), 47.5, 47.5, theta1=22, theta2=158, linewidth=lw, color=line_color)

    # Baseline
    baseline = patches.Rectangle((0, 0), 50, 0.1, linewidth=lw, color=line_color)

    # Add all shapes to the court
    court_elements = [hoop, backboard, paint, free_throw_top, free_throw_bottom,
                      restricted, corner3_left, corner3_right, three_arc, baseline]

    for element in court_elements:
        ax.add_patch(element)

    # Set dimensions and hide axes
    ax.set_xlim(0, 50)
    ax.set_ylim(0, 47)
    ax.set_facecolor(court_color)
    ax.set_aspect('equal')
    ax.axis('off')

    return ax

# Plot the court
fig, ax = plt.subplots(figsize=(10, 9))
draw_nba_half_court(ax)
plt.show()
