from scipy.spatial.distance import euclidean
from scipy.special import expit
import numpy as np


def radius_calc(dist_to_ball):
    return 4 + 6 * (dist_to_ball >= 15) + (dist_to_ball ** 3) / 560 * (dist_to_ball < 15)

def constant_factors_player_influence(theta, speed, player_coords, ball_coords):

    dist_to_ball = euclidean(player_coords, ball_coords)

    S_ratio = (speed / 13) ** 2    # we set max_speed to 13 m/s
    RADIUS = radius_calc(dist_to_ball)  # updated

    S_matrix = np.matrix([[0.5*RADIUS * (1 + S_ratio), 0], [0, 0.5*RADIUS * (1 - S_ratio)]])
    R_matrix = np.matrix([[np.cos(theta), - np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    COV_matrix = np.dot(np.dot(np.dot(R_matrix, S_matrix), S_matrix), np.linalg.inv(R_matrix))

    mu_play = player_coords + speed * np.array([np.cos(theta), np.sin(theta)]) / 2
    norm_fact = (1 / 2 * np.pi) * (1 / np.sqrt(np.linalg.det(COV_matrix)))

    intermed_scalar_player = np.dot(np.dot((player_coords - mu_play),
                                    np.linalg.inv(COV_matrix)),
                             np.transpose((player_coords - mu_play)))

    denominator_player_influence = norm_fact * np.exp(- 0.5 * intermed_scalar_player[0, 0])
    return np.array([denominator_player_influence, mu_play, norm_fact, COV_matrix])

@np.vectorize
def intermed_compute_influence(
    x_point, y_point, norm_fact):
    global mu_play, COV_matrix

    point = np.array([x_point, y_point])
    intermed_scalar_point = np.dot(np.dot((point - mu_play),
                                    np.linalg.inv(COV_matrix)),
                             np.transpose((point - mu_play)))
    point_influence = norm_fact * np.exp(- 0.5 * intermed_scalar_point[0, 0])


    return point_influence

def compute_player_influence(x_points, y_points, theta, speed, player_coords, ball_coords):
    '''Compute the influence of a certain player over a coordinate (x, y) of the pitch
    '''
    global mu_play, COV_matrix
    [denominator_player_influence, mu_play, norm_fact,COV_matrix] = constant_factors_player_influence(
        theta, speed, player_coords, ball_coords)

    return np.around(
        intermed_compute_influence(x_points, y_points, norm_fact)/denominator_player_influence
        ,4)


def compute(x_points, y_points):
    '''Compute the pitch control over a coordinate (x, y)
    '''
    offense_score = np.zeros([len(x_points),len(x_points[0])])
    for offense_id in offense_ids:
        offense_score = offense_score + compute_influence(x_points, y_points, offense_id)

    defense_score = np.zeros([len(x_points),len(x_points[0])])
    for defense_id in defense_ids:
        defense_score = defense_score + compute_influence(x_points, y_points, defense_id)

    return expit(offense_score - defense_score)

