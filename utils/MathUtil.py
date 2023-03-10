#!usr/bin/env python
# coding utf-8
"""
@File       :test.py
@Copyright  :CV Group
@Date       :8/23/2021
@Author     :Rui
@Desc       :
"""
import math

import numpy as np


def calc_cos_angle(vec1, vec2):
    mod1 = np.linalg.norm(vec1)
    mod2 = np.linalg.norm(vec2)
    ans = 0
    if mod1 * mod2 != 0:
        ans = np.dot(vec1, vec2) / (mod1 * mod2)
        ans = min(ans, 1)
        ans = max(ans, -1)
    return ans


def calc_sin_angle(vec1, vec2):
    mod1 = np.linalg.norm(vec1)
    mod2 = np.linalg.norm(vec2)
    vec_c = np.cross(vec1, vec2)
    return np.linalg.norm(vec_c) / (mod1 * mod2) if mod1 * mod2 != 0 else 0


def calc_radian(vec1, vec2):
    cos_theta = calc_cos_angle(vec1, vec2)
    return math.acos(cos_theta)


def calc_uniform_vec(vec):
    return vec/(np.linalg.norm(vec) + 1e-9)


def calc_eucleadian_dist(vec1, vec2):
    return np.linalg.norm(vec1-vec2)


def calc_cos_against_x_pos_axis(vec):
    unit_x = np.array([1, 0])
    return calc_cos_angle(vec, unit_x)


def calc_cos_against_y_pos_axis(vec):
    unit_y = np.array([1, 0])
    return calc_cos_angle(vec, unit_y)


def within_ball(point1, point2, epsilon, ord=None):
    vec = np.asarray(point1) - np.asarray(point2)
    dis = np.linalg.norm(vec, ord)
    return dis < epsilon


def calc_intersect(p0, p1, p2, p3):
    # line 0
    a0 = p0[1] - p1[1]
    b0 = p1[0] - p0[0]
    c0 = p0[0] * p1[1] - p0[1] * p1[0]

    # line 1
    a1 = p2[1] - p3[1]
    b1 = p3[0] - p2[0]
    c1 = p2[0] * p3[1] - p2[1] * p3[0]

    if a0 * b1 == a1 * b0:
        return None
    else:
        denom = a0 * b1 - a1 * b0

    x = (c1 * b0 - c0 * b1) / denom
    y = (c0 * a1 - c1 * a0) / denom
    return int(x), int(y)


def polar_to_cartesian(rho, radius):
    x = radius * math.cos(rho)
    y = radius * math.sin(rho)
    return x, y


def get_affine_matrix(radian):
    res = np.eye(2)
    res[0][0] = math.cos(radian)
    res[0][1] = -math.sin(radian)
    res[1][0] = math.sin(radian)
    res[1][1] = math.cos(radian)
    return res


def calc_triangle_area(vec1, vec2):
    return 0.5 * np.cross(vec1, vec2)


def calc_polygon_area_perimeter(vertices):
    """
    calculate area and perimeter of the polygon
    :param vertices: numpy array of points in the clockwise of anti-clockwise order
    :return: area, perimeter
    """
    if len(vertices) < 2:
        return 0, 0
    elif len(vertices) < 3:
        return 0, np.linalg.norm(vertices[0]-vertices[1])
    peri = 0
    area = 0
    for i in range(len(vertices)):
        peri += np.linalg.norm(vertices[i-1] - vertices[i])
        area += vertices[i-1][0] * vertices[i][1] - vertices[i][0] * vertices[i-1][1]
    area = 0.5 * abs(area)

    return area, peri
