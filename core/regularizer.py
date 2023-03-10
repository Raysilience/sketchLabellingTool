#!usr/bin/env python
# coding utf-8
'''
@File       :regularizer.py
@Copyright  :CV Group
@Date       :8/30/2021
@Author     :Rui
@Desc       :
'''
import logging
import math

import cv2
import numpy as np

from utils import MathUtil, ShapeUtil


class Regularizer:

    def __init__(self, config):
        self.MAX_EQUILATERAL_RAD_RELAXATION = config.getint('params', 'MAX_EQUILATERAL_RAD_RELAXATION') * math.pi / 180
        self.MAX_ISOSCELES_RAD_RELAXATION = config.getint('params', 'MAX_ISOSCELES_RAD_RELAXATION') * math.pi / 180
        self.MAX_PARALLEL_RAD_RELAXATION = config.getint('params', 'MAX_PARALLEL_RAD_RELAXATION') * math.pi / 180
        self.MAX_VERTICAL_RAD_RELAXATION = config.getint('params', 'MAX_VERTICAL_RAD_RELAXATION') * math.pi / 180
        self.MAX_DIAG_DIFF_FACTOR = config.getfloat('params', 'MAX_DIAG_DIFF_FACTOR')
        self.MAX_AXIS_DIFF_FACTOR = config.getfloat('params', 'MAX_AXIS_DIFF_FACTOR')
        self.align_on = config.getboolean('params', 'ALIGN_ON')

    def regularize(self, label, vertices):
        logging.debug("entering regularizer")
        sub_label = ''
        vertices = np.asarray(vertices)
        if label == 'ellipse':
            res = cv2.fitEllipse(vertices)
            x, y = res[0]
            axis_w, axis_h = res[1]
            angle = res[2]
            if abs(axis_h - axis_w) < self.MAX_AXIS_DIFF_FACTOR * max(axis_h, axis_w):
                avg = (axis_h + axis_w) / 2
                axis_w, axis_h = avg, avg
                sub_label = 'circle'
            return sub_label, [int(x) for x in [x, y, axis_w, axis_h, angle]]

        elif label == 'triangle':
            radians = []
            equilateral = True
            for i in range(len(vertices)):
                rad = MathUtil.calc_radian(vertices[i] - vertices[i - 1], vertices[i] - vertices[i - 2])
                radians.append(rad)
                if abs(rad - math.pi/3) > self.MAX_EQUILATERAL_RAD_RELAXATION:
                    equilateral = False
            if equilateral:
                sub_label = 'equilateral triangle'
                center, radius = cv2.minEnclosingCircle(vertices)
                direct0 = MathUtil.calc_uniform_vec(vertices[0] - center)
                length = MathUtil.calc_eucleadian_dist(center, vertices[0])
                aff_max = MathUtil.get_affine_matrix(math.pi * 2 / 3)
                direct1 = np.dot(aff_max, direct0)
                direct2 = np.dot(aff_max, direct1)
                vertices[1] = ShapeUtil.translate(center, direct1, length)
                vertices[2] = ShapeUtil.translate(center, direct2, length)
            else:
                if abs(radians[0] - radians[1]) < self.MAX_ISOSCELES_RAD_RELAXATION:
                    sub_label = 'isosceles triangle'
                    vertices = vertices[[2, 1, 0]]
                elif abs(radians[0] - radians[2]) < self.MAX_ISOSCELES_RAD_RELAXATION:
                    sub_label = 'isosceles triangle'
                    vertices = vertices[[1, 0, 2]]
                elif abs(radians[1] - radians[2]) < self.MAX_ISOSCELES_RAD_RELAXATION:
                    sub_label = 'isosceles triangle'

                if sub_label == 'isosceles triangle':
                    length = MathUtil.calc_eucleadian_dist(vertices[0], vertices[1])
                    direct2 = MathUtil.calc_uniform_vec(vertices[2] - vertices[0])
                    vertices[2] = ShapeUtil.translate(vertices[0], direct2, length)


        elif label == 'quadrangle':
            if ShapeUtil.check_parallel(vertices[0], vertices[1], vertices[2], vertices[3], self.MAX_PARALLEL_RAD_RELAXATION) and \
                    ShapeUtil.check_parallel(vertices[0], vertices[3], vertices[1], vertices[2], self.MAX_PARALLEL_RAD_RELAXATION):
                sub_label = 'parallelogram'
                diag02 = MathUtil.calc_eucleadian_dist(vertices[0], vertices[2])
                diag13 = MathUtil.calc_eucleadian_dist(vertices[1], vertices[3])
                if diag02 < diag13:
                    diag02, diag13 = diag13, diag02
                    logging.debug('vertices: {}'.format(vertices))
                    tmp = [vertices[i] for i in [3, 0, 1, 2]]
                    vertices = np.asarray(tmp)

                cross_point = np.asarray(MathUtil.calc_intersect(vertices[0], vertices[2], vertices[1], vertices[3]))
                mid_point = (vertices[0] + vertices[2]) / 2
                direct1 = MathUtil.calc_uniform_vec(cross_point - vertices[1])
                direct3 = -direct1
                length = diag13 / 2

                if diag02 - diag13 < self.MAX_DIAG_DIFF_FACTOR * diag02:
                    sub_label = 'rectangle'
                    length = diag02 / 2
                    if ShapeUtil.check_diag_vertical(vertices[0], vertices[1], vertices[2], vertices[3], self.MAX_VERTICAL_RAD_RELAXATION):
                        sub_label = 'square'
                        direct0 = MathUtil.calc_uniform_vec(cross_point - vertices[0])
                        aff_max = MathUtil.get_affine_matrix(math.pi / 2)
                        direct1 = np.dot(aff_max, direct0)
                        direct3 = -direct1
                else:
                    if ShapeUtil.check_diag_vertical(vertices[0], vertices[1], vertices[2], vertices[3], self.MAX_VERTICAL_RAD_RELAXATION):
                        sub_label = 'diamond'
                        direct0 = MathUtil.calc_uniform_vec(cross_point - vertices[0])
                        aff_max = MathUtil.get_affine_matrix(math.pi / 2)
                        direct1 = np.dot(aff_max, direct0)
                        direct3 = -direct1

                vertices[1] = ShapeUtil.translate(mid_point, direct1, length)
                vertices[3] = ShapeUtil.translate(mid_point, direct3, length)

        if self.align_on:
            vertices = ShapeUtil.align_shape(vertices, self.MAX_PARALLEL_RAD_RELAXATION)

        return sub_label, vertices.tolist()


