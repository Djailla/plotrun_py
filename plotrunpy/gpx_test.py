#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Summary: Plot run information from a GPX File
Author: Bastien Vallet
Copyright (c) 2014, Bastien Vallet

Run with: python plotrun.py [GPX file path]
"""

import argparse
import os
import pprint

# numpy lib to boost median and mean calculation
import numpy as np

# gpxpy to easly extract data from GPX file
import gpxpy

# geopy to calculate distance from the GPS coordonates
from geopy.distance import vincenty

# pygal to draw SVG output files
import pygal

pp = pprint.PrettyPrinter(indent=4)


def running_mean(x, N):
    mean = np.empty_like(x)
    mid_interval = N // 2

    cumsum = np.cumsum(x)

    x_len = len(x)
    x_len_interval = x_len - mid_interval

    for idx in xrange(x_len):
        min_idx = idx > mid_interval and idx - mid_interval or 0
        max_idx = idx < x_len_interval and idx + mid_interval or (x_len - 1)
        mean[idx] = (cumsum[max_idx] - cumsum[min_idx]) / (max_idx - min_idx)
    return mean


def running_median(x, N):
    median = np.empty_like(x)
    mid_interval = N // 2

    for idx in xrange(len(x)):
        min_idx = idx > mid_interval and idx - mid_interval or None
        median[idx] = np.median(x[min_idx: idx + mid_interval])
    return median

if __name__ == '__main__':
    # logging.basicConfig(format='%(levelname)s: %(message)s',
    #                     level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Set the parameters.')
    parser.add_argument('--raw', action='store_true')
    parser.add_argument('--mean', action='store_true')
    parser.add_argument('--median', action='store_true')
    parser.add_argument('--elevation', action='store_true')
    parser.add_argument('gpx_file')

    args = parser.parse_args()

    # Check that at least one parameter is provided
    if not any([args.raw, args.mean, args.median, args.elevation]):
        print '*' * 33
        print "* Add at least one plot to draw *"
        print '*' * 33
        parser.print_help()
        exit(1)

    gpx_dir, gpx_file_name = os.path.split(args.gpx_file)
    gpx_file_prefix, gpx_file_extension = os.path.splitext(gpx_file_name)
    svg_path = os.path.join(gpx_dir, gpx_file_prefix + '.svg')

    with open(args.gpx_file, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        gpx_points = []

        for track in gpx.tracks:
            for segment in track.segments:
                ref_time = segment.points[0].time

                for point in segment.points:
                    gpx_points.append(
                        {
                            'time': (point.time - ref_time).total_seconds(),
                            'coordonates': (point.latitude, point.longitude),
                            'elevation': point.elevation,
                        }
                    )

        prev = gpx_points[0]
        gpx_points[0]['distance'] = 0
        gpx_points[0]['speed'] = 0

        distances = []
        for gpx_point in gpx_points[1:]:
            d = vincenty(prev['coordonates'], gpx_point['coordonates']).meters
            gpx_point['distance'] = d
            gpx_point['speed'] = d / (gpx_point['time'] - prev['time']) * 3.6

            prev = gpx_point
            # distances.append(d)

        gpx_points[0]['speed'] = gpx_points[1]['speed']

        gpx_speed = [gpx_point['speed'] for gpx_point in gpx_points]
        if args.mean:
            speed_mean = running_mean(gpx_speed, 20)

        if args.median:
            speed_median = running_median(gpx_speed, 20)

    xy_chart = pygal.XY(stroke=True, show_dots=False, width=1500, height=1000)
    xy_chart.title = 'Speed'
    if args.raw:
        xy_chart.add('Raw speed', [(gpx_point['time'], gpx_point['speed'])
                     for gpx_point in gpx_points])
    if args.mean:
        xy_chart.add('Average speed', [(gpx_points[idx]['time'], speed_mean[idx])
                     for idx in xrange(len(gpx_points))])
    if args.median:
        xy_chart.add('Mediam speed', [(gpx_points[idx]['time'], speed_median[idx])
                     for idx in xrange(len(gpx_points))])
    if args.elevation:
        xy_chart.add('Elevation', [(gpx_point['time'], gpx_point['elevation'])
                     for gpx_point in gpx_points])
    xy_chart.render_to_file(svg_path)
