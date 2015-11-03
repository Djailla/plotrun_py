import numpy as np
import gpxpy
from geopy.distance import vincenty
import pprint

import pygal
# from pygal.style import LightenStyle

pp = pprint.PrettyPrinter(indent=4)
PREFIX_DIR = 'sample/'
PREFIX = 'frac2'

GPX_FILE = PREFIX_DIR + PREFIX + '.gpx'
CSV_OUT = PREFIX_DIR + PREFIX + '.csv'
SVG_OUT = PREFIX_DIR + PREFIX + '.svg'

test_list = [1., 1., 1., 2., 2., 2., 3., 3., 3., 4.]


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


with open(GPX_FILE, 'r') as gpx_file:
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
    speed_mean = running_mean(gpx_speed, 20)
    speed_median = running_median(gpx_speed, 20)

    # with open(CSV_OUT, 'w') as csv_out:
    #     for idx in range(len(gpx_points)):
    #         csv_out.write(
    #             '%f;%f;%f;%f\n' % (
    #                 gpx_points[idx]['time'],
    #                 gpx_points[idx]['speed'],
    #                 speed_mean[idx],
    #                 speed_median[idx],
    #             )
    #         )

    # print "Average speed = %f" % np.mean([gpx_point['speed'] for gpx_point in gpx_points])

# dark_lighten_style = LightenStyle('#336676')

xy_chart = pygal.XY(stroke=True, show_dots=False, width=1500, height=1000)
xy_chart.title = 'Speed'
# xy_chart.add('Raw speed', [(gpx_point['time'], gpx_point['speed']) for gpx_point in gpx_points])
# xy_chart.add('Average speed', [(gpx_points[idx]['time'], speed_mean[idx]) for idx in xrange(len(gpx_points))])
xy_chart.add('Mediam speed', [(gpx_points[idx]['time'], speed_median[idx]) for idx in xrange(len(gpx_points))])
# xy_chart.add('Elevation', [(gpx_point['time'], gpx_point['elevation']) for gpx_point in gpx_points])
xy_chart.render_to_file(SVG_OUT)
