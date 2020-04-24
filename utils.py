import matplotlib.patches as patches
import matplotlib.pyplot as plt
import math
import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d

plt.ioff()

def create_football_field(linenumbers=True,
                          endzones=True,
                          figsize=(12*2, 6.33*2)):
    """
    Function that plots the football field for viewing plays.
    Allows for showing or hiding endzones.
    """

    rect = patches.Rectangle((-52.5, -35), 105, 70, linewidth=3,capstyle='round',
                             edgecolor='w', facecolor='darkgreen', alpha=0.5)

    fig, ax = plt.subplots(1, figsize=figsize)
    fig.patch.set_facecolor('green')
    fig.patch.set_alpha(0.7)
    ax.add_patch(rect)

    #borders
    plt.plot([-52.5, -52.5, 52.5,52.5, -52.5], [-35, 35, 35, -35, -35], c='w', linewidth=4)

    ## goals
    plt.plot([-52.5, -55, -55, -52.5], [-5, -5, 5, 5], c='w', linewidth=4)
    plt.plot([52.5, 55, 55, 52.5], [-5, -5, 5, 5], c='w', linewidth=4)

    ## middle line
    plt.plot([0,0],[-35,35],c='w', linewidth=3, alpha=0.25)

    plt.xlim(-56, 56)
    plt.ylim(-37, 37)
    plt.axis('off')

    return fig, ax

def show_players_and_ball(row):
    fig, ax = create_football_field()
    ball = row[-2:]
    defense, offense = [x.reshape(-1,2) for x in row[:-2].reshape(-1,11*2)]

    ax.scatter(offense[:,0],offense[:,1], c='b', s=150)
    ax.scatter(defense[:,0],defense[:,1], c='r', s=150)
    ax.scatter(ball[0], ball[1], c='yellow', s=50)
    return fig, ax

def show_voronoi(row):
    xy = row[:-2].reshape(-1,2)
    n_points = xy.shape[0]
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
                plt.plot(*zip(*polygon), c='black', alpha=0.25, linewidth=3)
            else:
                plt.fill(*zip(*polygon), c='r', alpha=0.25, edgecolor="black", linewidth=0.0)
                plt.plot(*zip(*polygon), c='black', alpha=0.25, linewidth=3)

    # Used to return the plot as an image rray
    fig.canvas.draw()       # draw the canvas, cache the renderer
    image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
    image  = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    return image
