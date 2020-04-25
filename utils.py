import matplotlib.patches as patches
import matplotlib.pyplot as plt
import math
import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.cm as cm

plt.ioff()

def create_football_field(figsize=(12*2, 6.33*2), goals=True):
    """
    Function that plots the football field for viewing plays.
    """

    #pitch outline & centre line
    pitch = patches.Rectangle((-52.5, -35), 105, 70, linewidth=2,capstyle='round',
                             edgecolor='w', facecolor='darkgreen')

    fig, ax = plt.subplots(1, figsize=figsize)
    fig.patch.set_facecolor('green')
    fig.patch.set_alpha(0.7)

    ## goals
    if goals:
        plt.plot([-52.5, -55, -55, -52.5], [-5, -5, 5, 5], c='w', linewidth=2)
        plt.plot([52.5, 55, 55, 52.5], [-5, -5, 5, 5], c='w', linewidth=2)

    ## middle line
    midline = patches.ConnectionPatch([0,-35], [0,35], "data", "data", color='white')

    #center circle
    centreCircle = plt.Circle((0,0), 10, color="white", fill = False, linewidth=2)
    centreSpot = plt.Circle((0,0), 0.3, color="white", linewidth=2)

    #left, right penalty area
    leftPenalty = patches.Rectangle([-52.5,-15], width=14.5, height=30, fill = False,
                                    color='white', linewidth=2)
    rightPenalty = patches.Rectangle([38.0,-15], width=14.5, height=30, fill = False,
                                     color='white', linewidth=2)

    #left, right 6-yard box
    leftSixYard = patches.Rectangle([-52.5,-8], width=4.5, height=16, fill=False,
                                    color='white', linewidth=2)
    rightSixYard = patches.Rectangle([48,-8], width=4.5, height=16, fill=False,
                                     color='white', linewidth=2)

    #penalty spots
    leftPenSpot = plt.Circle((-43.5,0),0.3, color="white", linewidth=2)
    rightPenSpot = plt.Circle((43.5,0),0.3, color="white", linewidth=2)

    element = [pitch, midline, centreCircle, centreSpot, leftPenalty, rightPenalty, leftSixYard,
               rightSixYard, rightPenSpot, leftPenSpot]

    for i in element:
        ax.add_patch(i)

    plt.xlim(-56, 56)
    plt.ylim(-37, 37)
    plt.axis('off')
    return fig, ax

def show_players_and_ball(row):
    fig, ax = create_football_field()
    ball = row[-2:]
    defense, offense = [x.reshape(-1,2) for x in row[:-2].reshape(-1,11*2)]

    ax.scatter(offense[:,0],offense[:,1], c='b', s=150, zorder=3)
    ax.scatter(defense[:,0],defense[:,1], c='r', s=150, zorder=3)
    ax.scatter(ball[0], ball[1], c='yellow', s=50, zorder=3)
    return fig, ax

def show_voronoi(row):
    xy = row[:-2].reshape(-1,2)
    n_points = xy.shape[0]

    #To deal with unbounded Voronoi regions, I decided to mirror points across field boundaries.
    xy1 = xy.copy()
    xy1[:,1] = -35 + (-35 - xy[:,1])
    xy2 = xy.copy()
    xy2[:,1] = 35 + (35 - xy[:,1])
    xy3 = xy.copy()
    xy3[:,0] = -52.5 + (-52.5 - xy[:,0])
    xy4 = xy.copy()
    xy4[:,0] = 52.5 + (52.5 - xy[:,0])
    xy = np.concatenate((xy, xy1, xy2, xy3, xy4), axis=0)
    vor = Voronoi(xy)

    fig, ax = show_players_and_ball(row)
    #voronoi_plot_2d(vor, ax=ax, show_points=False, show_vertices=False)
    for r in range(n_points):
        region = vor.regions[vor.point_region[r]]
        if not -1 in region:
            polygon = [vor.vertices[i] for i in region]
            if r>10:
                #Offense players
                plt.plot(*zip(*polygon), c='black', alpha=0.25, linewidth=3)
            else:
                #Defense players
                plt.fill(*zip(*polygon), c='r', alpha=0.25, edgecolor="black", linewidth=0.0)
                plt.plot(*zip(*polygon), c='black', alpha=0.25, linewidth=3)

    # Used to return the plot as an image rray
    fig.canvas.draw()       # draw the canvas, cache the renderer
    image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
    image  = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    return image

def get_dx_dy(radian_angle, dist):
    dx = dist * math.cos(radian_angle)
    dy = dist * math.sin(radian_angle)
    return dx, dy

def draw_player_influence_area(X, Y, player_influence, x_player, y_player, theta,speed, row):
    fig, ax = show_players_and_ball(row)
    dx, dy = get_dx_dy(theta, speed)
    ax.arrow(x_player, y_player, dx, dy, length_includes_head=False, width=0.2, color='black', alpha=0.5)
    contours = plt.contour(X, Y, player_influence, cmap='RdBu')
    plt.clabel(contours, inline=True, fontsize=12)
    plt.title('Player Influence Area', fontsize=24, color='white')

    # Used to return the plot as an image rray
    fig.canvas.draw()       # draw the canvas, cache the renderer
    image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
    image  = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    return image

def draw_pitch_control(X, Y, pitch_control, row):
    fig, ax = show_players_and_ball(row)
    plt.contour(X, Y, pitch_control, colors='black', zorder=2,  vmin=0.2, vmax=0.8)

    plt.imshow(pitch_control, extent=[-52.5, 52.5, -35, 35], origin='lower',
            cmap='RdBu', alpha=0.5, zorder=1)

    plt.clim(0.2, 0.8)  # manually setup the range of the colorscale and colorbar
    plt.colorbar()

    # Used to return the plot as an image rray
    fig.canvas.draw()       # draw the canvas, cache the renderer
    image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
    image  = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    return image
