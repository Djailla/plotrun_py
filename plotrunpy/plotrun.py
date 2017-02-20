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
import datetime

# matplotlib for dynamical display view
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker

from helper import (
    moving_average,
    moving_median,
    hull_average,
)
from gpx import parse_gpx_file

WINDOWS_SIZE = 15

# pylint: disable=bad-whitespace
GRAPH_CONFIG = {
    # Attribute        Label        is_speed  color    left_y
    'watch_speed':    ('Watch',      True,    'blue',    True),
    'gps_speed':      ('GPS',        True,    'green',   True),
    'improved_speed': ('Improved',   True,    'red',     True),
    'average_speed':  ('Average',    True,    'magenta', True),
    'median_speed':   ('Median',     True,    'red',     True),
    'hull_speed':     ('Hull',       True,    'green',   True),
    'elevation':      ('Elevation',  False,   'gray',    False),
    'heart_rate':     ('Heart Rate', False,   'pink',    False),
}

PLOT_LIST = []
AXES_LIST = []

class GraphOptions(object):
    """
    GraphOptions allow to set the value for the x and y axis
    """
    x_axis_data = None
    y_axis_data = None

    def __init__(self, x_axis_data, y_axis_data):
        self.x_axis_data = x_axis_data
        self.y_axis_data = y_axis_data

    @property
    def x_axis_label(self):
        """
        Return label to display on the x axis according configuration
        """
        return 'Time (min)' if self.x_axis_data == 'time'\
                          else 'Distance (km)'

    @property
    def y_axis_label(self):
        """
        Return label to display on the y axis according configuration
        """
        return 'Speed (km/h)' if self.y_axis_data == 'speed'\
                              else 'Pace (min/km)'


class DataGraph(object):
    """
    DataGraph class contains all plot related informations
    """
    attribute = None
    x_data = []
    x_time = True
    is_speed = True
    y_data = []
    color = 'blue'
    label = 'Unknown'
    graph_options = None
    plot = None

    def __init__(self, gpx_points, attribute, graph_options):
        if attribute not in GRAPH_CONFIG:
            raise Exception

        self.attribute = attribute
        self.label, self.is_speed, self.color, self.left_y = \
            GRAPH_CONFIG.get(attribute)

        if self.is_speed and graph_options.y_axis_data == 'pace':
            # Convert speed to pace
            self.x_data = [
                60 / getattr(gpx_point, attribute) for
                gpx_point in gpx_points
            ]
        else:
            self.x_data = [
                getattr(gpx_point, attribute) for
                gpx_point in gpx_points
            ]

        self.graph_options = graph_options
        if graph_options.x_axis_data == 'time':
            self.y_data = [gpx_point.float_time for gpx_point in gpx_points]
        else:
            self.y_data = [gpx_point.distance for gpx_point in gpx_points]

    def __repr__(self):
        return "%s" % (self.is_speed)

    @property
    def plot_label(self):
        """Generate the label to display on the graph for this plot"""
        if self.is_speed:
            param = ' speed' if self.graph_options.y_axis_data == 'speed'\
                    else ' pace'
        else:
            param = ""

        return self.label + param

    @property
    def y_axis_label(self):
        """
        Return label to display on the y axis according configuration
        """
        return 'Elevation (m)' if self.attribute == 'elevation'\
                               else 'Heart Rate (bpm)'

    def graph_plot(self, axes):
        """Generic graph plot function"""
        if self.is_speed:
            self.plot = axes.plot(
                self.y_data, self.x_data,
                color=self.color, linewidth=1.5, linestyle="-",
                label=self.plot_label,
            )
        else:
            self.plot = axes.fill_between(
                self.y_data,
                min(self.x_data),
                self.x_data,
                color=self.color, linewidth=1.0, linestyle="-",
                label=self.plot_label, alpha=0.3,
            )

    def graph(self, axes):
        """Display the plot on graph"""
        if self.is_speed:
            self.graph_plot(axes)
        else:
            if len(PLOT_LIST) > 0:
                axes2 = axes.twinx()
                self.graph_plot(axes2)
                axes2.set_ylabel(self.y_axis_label)
                # axes2.grid(linestyle='--', color=self.color)
                AXES_LIST.append(axes2)
            else:
                self.graph_plot(axes)

        PLOT_LIST.append(self.plot)


def get_parser():
    """Set plotrun parser options"""
    parser = argparse.ArgumentParser(description='Set the parameters.')
    parser.add_argument('--raw', action='store_true')
    parser.add_argument('--average', action='store_true')
    parser.add_argument('--median', action='store_true')
    parser.add_argument('--hull', action='store_true')


    right_y = parser.add_mutually_exclusive_group()
    right_y.add_argument('--bpm', action='store_true')
    right_y.add_argument('--elevation', action='store_true')

    parser.add_argument('-s', type=int, action="store", dest="windows_size")
    parser.add_argument(
        '--pace', action='store_true',
        help='Enabled to switch from speed to pace')
    parser.add_argument(
        '--x_distance', action='store_true',
        help='Set distance instead of time as parameter for x axis')
    parser.add_argument('gpx_file')

    return parser


def error_message(arg_parser, message='Unknown error'):
    """Print error message and exit"""
    print('*' * 33)
    print("* %s *", message)
    print('*' * 33)
    arg_parser.print_help()
    exit(1)


def main():
    """Main plotrun function"""

    # Parse input args
    arg_parser = get_parser()
    args = arg_parser.parse_args()
    windows_size = args.windows_size or WINDOWS_SIZE

    # # Check that at least one parameter is provided
    # if not any([args.raw, args.average,
    #             args.median, args.hull]):
    #     error_message(arg_parser, "Add at least one plot to draw")

    # Parse GPX file to generate the list of GPX points
    gpx_points = parse_gpx_file(args.gpx_file)

    # Prepare the resource to draw content
    fig = plt.figure(figsize=(15, 8))
    graph_options = GraphOptions(
        'distance' if args.x_distance else 'time',
        'pace' if args.pace else 'speed'
    )

    axes1 = fig.add_subplot(111)
    AXES_LIST.append(axes1)

    # Add a plot per data requested
    if args.raw:
        # raw_line = DataGraph(gpx_points, 'gps_speed')
        # raw_line.graph()
        raw_line2 = DataGraph(gpx_points, 'watch_speed', graph_options)
        raw_line2.graph(axes1)
        # raw_line3 = DataGraph(gpx_points, 'improved_speed')
        # raw_line3.graph()
    if args.average:
        moving_average(gpx_points, windows_size)
        avg_line = DataGraph(gpx_points, 'average_speed', graph_options)
        avg_line.graph(axes1)
    if args.median:
        moving_median(gpx_points, windows_size)
        med_line = DataGraph(gpx_points, 'median_speed', graph_options)
        med_line.graph(axes1)
    if args.hull:
        hull_average(gpx_points, windows_size)
        hul_line = DataGraph(gpx_points, 'hull_speed', graph_options)
        hul_line.graph(axes1)

    # Check right Y axis data
    if args.elevation:
        ele_line = DataGraph(gpx_points, 'elevation', graph_options)
        ele_line.graph(axes1)
    if args.bpm:
        ele_line = DataGraph(gpx_points, 'heart_rate', graph_options)
        ele_line.graph(axes1)

    plt.autoscale(enable=True, axis='x', tight=True)

    axes1.grid(linestyle=':', alpha=0.5)
    axes1.set_xlabel(graph_options.x_axis_label)
    axes1.set_ylabel(graph_options.y_axis_label)

    xloc = plticker.MultipleLocator(base=5.0)
    axes1.xaxis.set_major_locator(xloc)

    if graph_options.y_axis_data == 'speed':
        yloc = plticker.MultipleLocator(base=1.0)
        axes1.yaxis.set_major_locator(yloc)
    else:
        def time_ticks(x_input, _pos):
            """Set ticks as duration"""
            delta = datetime.timedelta(seconds=(x_input * 60))
            return str(delta)

        formatter = plticker.FuncFormatter(time_ticks)
        axes1.yaxis.set_major_formatter(formatter)

    handle1, line1 = AXES_LIST[0].get_legend_handles_labels()
    if len(AXES_LIST) == 2:
        handle2, line2 = AXES_LIST[1].get_legend_handles_labels()
        axes1.legend(handle1 + handle2, line1 + line2, loc=2)
    else:
        axes1.legend(handle1, line1, loc=2)

    fig.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
