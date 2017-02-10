#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Summary: Plot run information from a GPX File
Author: Bastien Vallet
Copyright (c) 2014, Bastien Vallet

Run with: python plotrun.py [GPX file path]
"""

# Compat
from __future__ import absolute_import, division, print_function

import argparse

# gpxpy to easly extract data from GPX file
import gpxpy

# geopy to calculate distance from the GPS coordonates
from geopy.distance import vincenty

# matplotlib for dynamical display view
import matplotlib.pyplot as plt

from helper import (
    moving_average,
    moving_median,
    hull_average,
)

WINDOWS_SIZE = 15

# pylint: disable=bad-whitespace
GRAPH_CONFIG = {
    # Attribute        Label        is_speed  color    left_y
    'raw_speed':     ('Raw',        True,    'blue',   True),
    'average_speed': ('Average',    True,    'orange', True),
    'median_speed':  ('Median',     True,    'red',    True),
    'hull_speed':    ('Hull',       True,    'green',  True),
    'elevation':     ('Elevation',  False,   'yellow', False),
    'bpm':           ('Heart Rate', False,   'pink',   False),
}


class DataGraph(object):
    x_data = []
    x_time = True
    is_speed = True
    y_data = []
    color = 'blue'
    label = 'Unknown'

    def __init__(self, gpx_points, attribute, speed_pace=True, x_time=True):
        if attribute not in GRAPH_CONFIG:
            raise Exception

        self.label, self.is_speed, self.color, self.left_y = \
            GRAPH_CONFIG.get(attribute)

        if self.is_speed and not speed_pace:
            # Convert speed to pace
            self.x_data = [
                getattr(gpx_point, attribute) / 3600 for
                gpx_point in gpx_points
            ]
        else:
            self.x_data = [
                getattr(gpx_point, attribute) for
                gpx_point in gpx_points
            ]

        if x_time:
            self.y_data = [gpx_point.time for gpx_point in gpx_points]
        else:
            self.y_data = [gpx_point.distance for gpx_point in gpx_points]

    def graph(self):
        plt.plot(
            self.y_data,
            self.x_data,
            color=self.color,
            linewidth=1.0,
            linestyle="-",
            label=self.label,
        )


class GPXPoint(object):
    """
    Store all information computed per point
    """
    time = 0
    coordonates = None
    elevation = None
    distance = 0
    cumulative_distance = 0

    raw_speed = 0
    median_speed = 0
    average_speed = 0
    hull_speed = 0

    def __init__(self, time, coordonates, elevation=None):
        self.time = time
        self.coordonates = coordonates
        self.elevation = elevation


def get_parser():
    parser = argparse.ArgumentParser(description='Set the parameters.')
    parser.add_argument('--raw', action='store_true')
    parser.add_argument('--average', action='store_true')
    parser.add_argument('--median', action='store_true')
    parser.add_argument('--hull', action='store_true')
    parser.add_argument('--bpm', action='store_true')
    parser.add_argument('--elevation', action='store_true')
    parser.add_argument('-s', type=int, action="store", dest="windows_size")
    parser.add_argument('--pace', action='store_true',
                        help='Enabled to switch from speed to pace')
    parser.add_argument('gpx_file')

    return parser


def main():
    arg_parser = get_parser()
    args = arg_parser.parse_args()

    windows_size = args.windows_size or WINDOWS_SIZE

    # Check that at least one parameter is provided
    if not any([args.raw, args.average,
                args.median, args.hull,
                args.elevation]):
        print('*' * 33)
        print("* Add at least one plot to draw *")
        print('*' * 33)
        arg_parser.print_help()
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
                            float((point.time - ref_time).total_seconds()),
                            (point.latitude, point.longitude),
                            point.elevation
                        )
                    )

        prev = gpx_points[0]
        gpx_points[0].distance = 0
        gpx_points[0].cumulative_distance = 0
        gpx_points[0].raw_speed = 0

        for gpx_point in gpx_points[1:]:
            # Compute distance from previous point
            xy_dist = vincenty(prev.coordonates, gpx_point.coordonates).meters
            gpx_point.distance = xy_dist

            # Set cumulative distance
            gpx_point.cumulative_distance = prev.cumulative_distance + xy_dist

            # Get time diff from last point
            xy_time = gpx_point.time - prev.time

            # Then calculate current speed
            gpx_point.raw_speed = (
                xy_dist / xy_time * 3.6
                if xy_time else prev.raw_speed
            )

            prev = gpx_point

        gpx_points[0].raw_speed = gpx_points[1].raw_speed

        x_axis = 'time'
        # x_axis = 'distance'

        if args.raw:
            raw_line = DataGraph(gpx_points, 'raw_speed')
            raw_line.graph()
        if args.average:
            moving_average(gpx_points, windows_size)
            avg_line = DataGraph(gpx_points, 'average_speed')
            avg_line.graph()
        if args.median:
            moving_median(gpx_points, windows_size)
            med_line = DataGraph(gpx_points, 'median_speed')
            med_line.graph()
        if args.hull:
            hull_average(gpx_points, windows_size)
            hul_line = DataGraph(gpx_points, 'hull_speed')
            hul_line.graph()
        if args.elevation:
            ele_line = DataGraph(gpx_points, 'elevation')
            ele_line.graph()

    plt.legend(loc='upper left', frameon=False)
    plt.xlabel(x_axis)
    plt.ylabel('speed')
    plt.grid()
    plt.show()

if __name__ == '__main__':
    main()
