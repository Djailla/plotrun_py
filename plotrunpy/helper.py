#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Function helpers for gpx data interpretor"""

from math import sqrt

# numpy lib to boost median and mean calculation
import numpy as np


def moving_average(gpx_points, windows_size):
    """Compute moving average for value list"""
    x_values = [gpx_point.watch_speed for gpx_point in gpx_points]
    mid_interval = windows_size // 2
    cumsum = np.cumsum(x_values)

    x_len = len(x_values)
    x_len_interval = x_len - mid_interval

    for x_idx in range(x_len):
        min_idx = x_idx > mid_interval and x_idx - mid_interval or 0
        max_idx = (x_idx < x_len_interval and x_idx + mid_interval or
                   (x_len - 1))
        gpx_points[x_idx].average_speed = (
            cumsum[max_idx] - cumsum[min_idx]) / (max_idx - min_idx)


def moving_average_list(input_list, windows_size):
    """Compute moving average for value list"""
    output_list = np.empty_like(input_list)
    mid_interval = windows_size // 2
    cumsum = np.cumsum(input_list)

    x_len = len(input_list)
    x_len_interval = x_len - mid_interval

    for x_idx in range(x_len):
        min_idx = x_idx > mid_interval and x_idx - mid_interval or 0
        max_idx = (x_idx < x_len_interval and x_idx + mid_interval or
                   (x_len - 1))
        output_list[x_idx] = (
            cumsum[max_idx] - cumsum[min_idx]) / (max_idx - min_idx)

    return output_list


def moving_median(gpx_points, windows_size):
    """Compute moving median for value list"""
    x_values = [gpx_point.watch_speed for gpx_point in gpx_points]
    mid_interval = windows_size // 2

    for x_idx in range(len(x_values)):
        min_idx = x_idx > mid_interval and x_idx - mid_interval or None
        gpx_points[x_idx].median_speed = \
            np.median(x_values[min_idx: x_idx + mid_interval])


def hull_average(gpx_points, windows_size):
    """Compute hull average for value list"""
    x_values = [gpx_point.watch_speed for gpx_point in gpx_points]

    moving_average_half = moving_average_list(x_values, windows_size // 2)
    moving_average_full = moving_average_list(x_values, windows_size)

    temp_list = np.cumsum(x_values)
    for x_idx in range(len(x_values)):
        temp_list[x_idx] = 2 * moving_average_half[x_idx] - \
                           moving_average_full[x_idx]

    hull_list = moving_average_list(temp_list, int(sqrt(windows_size)))
    for x_idx in range(len(x_values)):
        gpx_points[x_idx].hull_speed = hull_list[x_idx]
