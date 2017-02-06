#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Summary: Plot run information from a GPX File
Author: Bastien Vallet
Copyright (c) 2014, Bastien Vallet

Run with: python plotrun.py [GPX file path]
"""

import argparse
from math import sqrt

# numpy lib to boost median and mean calculation
import numpy as np

# gpxpy to easly extract data from GPX file
import gpxpy

# geopy to calculate distance from the GPS coordonates
from geopy.distance import vincenty

# matplotlib for dynamical display view
import matplotlib.pyplot as plt


WINDOWS_SIZE = 15


def moving_average(gpx_points, windows_size):
    """Compute moving average for value list"""
    x_values = [gpx_point.raw_speed for gpx_point in gpx_points]
    mid_interval = windows_size // 2
    cumsum = np.cumsum(x_values)

    x_len = len(x_values)
    x_len_interval = x_len - mid_interval

    for x_idx in xrange(x_len):
        min_idx = x_idx > mid_interval and x_idx - mid_interval or 0
        max_idx = x_idx < x_len_interval and x_idx + mid_interval or (x_len - 1)
        gpx_points[x_idx].average_speed = (
            cumsum[max_idx] - cumsum[min_idx]) / (max_idx - min_idx)


def moving_average_list(input_list, windows_size):
    """Compute moving average for value list"""
    output_list = np.empty_like(input_list)
    mid_interval = windows_size // 2
    cumsum = np.cumsum(input_list)

    x_len = len(input_list)
    x_len_interval = x_len - mid_interval

    for x_idx in xrange(x_len):
        min_idx = x_idx > mid_interval and x_idx - mid_interval or 0
        max_idx = x_idx < x_len_interval and x_idx + mid_interval or (x_len - 1)
        output_list[x_idx] = (
            cumsum[max_idx] - cumsum[min_idx]) / (max_idx - min_idx)

    return output_list


def moving_median(gpx_points, windows_size):
    """Compute moving median for value list"""
    x_values = [gpx_point.raw_speed for gpx_point in gpx_points]
    mid_interval = windows_size // 2

    for x_idx in xrange(len(x_values)):
        min_idx = x_idx > mid_interval and x_idx - mid_interval or None
        gpx_points[x_idx].median_speed = \
            np.median(x_values[min_idx: x_idx + mid_interval])


def hull_average(gpx_points, windows_size):
    """Compute hull average for value list"""
    x_values = [gpx_point.raw_speed for gpx_point in gpx_points]

    moving_average_half = moving_average_list(x_values, windows_size/2)
    moving_average_full = moving_average_list(x_values, windows_size)

    temp_list = np.cumsum(x_values)
    for x_idx in xrange(len(x_values)):
        temp_list[x_idx] = 2 * moving_average_half[x_idx] - \
                           moving_average_full[x_idx]

    hull_list = moving_average_list(temp_list, int(sqrt(windows_size)))
    for x_idx in xrange(len(x_values)):
        gpx_points[x_idx].hull_speed = hull_list[x_idx]


def display_in_graph(gpx_points, value_type, color="blue"):
    """Add a data in final graph"""
    plt.plot(
        [gpx_point.time for gpx_point in gpx_points],
        [getattr(gpx_point, value_type) for gpx_point in gpx_points],
        color=color, linewidth=1.0, linestyle="-",
        label=value_type
    )

class GPXPoint(object):
    """
    Store all information computed per point
    """
    time = 0
    coordonates = None
    elevation = None
    distance = 0

    raw_speed = 0
    median_speed = 0
    average_speed = 0
    hull_speed = 0

    def __init__(self, time, coordonates, elevation=None):
        self.time = time
        self.coordonates = coordonates
        self.elevation = elevation


def main():
    parser = argparse.ArgumentParser(description='Set the parameters.')
    parser.add_argument('--raw', action='store_true')
    parser.add_argument('--average', action='store_true')
    parser.add_argument('--median', action='store_true')
    parser.add_argument('--hull', action='store_true')
    parser.add_argument('--bpm', action='store_true')
    parser.add_argument('--elevation', action='store_true')
    parser.add_argument('-s', type=int, action="store", dest="windows_size")
    parser.add_argument('--pace', action='store_true', help='Enabled to switch from speed to pace')
    parser.add_argument('gpx_file')

    args = parser.parse_args()

    windows_size = args.windows_size or WINDOWS_SIZE

    print windows_size

    # Check that at least one parameter is provided
    if not any([args.raw, args.average,
                args.median, args.hull,
                args.elevation]):
        print '*' * 33
        print "* Add at least one plot to draw *"
        print '*' * 33
        parser.print_help()
        exit(1)

    plt.figure(figsize=(15, 8))

    with open(args.gpx_file, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        gpx_points = []

        for track in gpx.tracks:
            for segment in track.segments:
                ref_time = segment.points[0].time

                for point in segment.points:
                    gpx_points.append(
                        GPXPoint(
                            (point.time - ref_time).total_seconds(),
                            (point.latitude, point.longitude),
                            point.elevation
                        )
                    )

        prev = gpx_points[0]
        gpx_points[0].distance = 0
        gpx_points[0].raw_speed = 0

        for gpx_point in gpx_points[1:]:
            xy_dist = vincenty(prev.coordonates, gpx_point.coordonates).meters
            gpx_point.distance = xy_dist
            xy_time = gpx_point.time - prev.time

            gpx_point.raw_speed = xy_dist / xy_time * 3.6

            prev = gpx_point

        gpx_points[0].raw_speed = gpx_points[1].raw_speed

        if args.raw:
            display_in_graph(gpx_points, 'raw_speed', 'blue')
        if args.average:
            moving_average(gpx_points, windows_size)
            display_in_graph(gpx_points, 'average_speed', 'orange')
        if args.median:
            moving_median(gpx_points, windows_size)
            display_in_graph(gpx_points, 'median_speed', 'red')
        if args.hull:
            hull_average(gpx_points, windows_size)
            display_in_graph(gpx_points, 'hull_speed', 'green')
        if args.elevation:
            display_in_graph(gpx_points, 'elevation', 'pink')

    # plt.yticks(np.linspace(-1,1,5,endpoint=True))

    plt.legend(loc='upper left', frameon=False)
    plt.grid()
    plt.show()

if __name__ == '__main__':
    main()
