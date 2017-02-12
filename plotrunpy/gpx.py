#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Function for GPX file content parsing
"""

import xmltodict

from converter import parse_time

class GPXPoint(object):
    """
    Output object of the gpx parsing operation
    """
    lat = 0
    lon = 0
    ele = 0
    time = None
    heart_rate = 0
    cadence = 0
    distance = 0
    altitude = 0.0
    speed = 0
    gps_speed = 0
    watch_speed = 0

    def __init__(self, lat, lon, time, elapsed_time, ele=0,
                 heart_rate=None, distance=None, cadence=None,
                 watch_speed=None):
        self.lat = float(lat)
        self.lon = float(lon)
        self.time = parse_time(time)
        self.elapsed_time = elapsed_time
        self.ele = int(round(float(ele)))
        self.heart_rate = int(heart_rate) if heart_rate else None
        self.distance = float(distance) if distance else None
        self.cadence = int(cadence) if cadence else None
        self.watch_speed = (float(watch_speed) * 3.6) if watch_speed else None

    def __repr__(self):
        extra = ["lat=%f lon=%f time=%s" % (self.lat, self.lon, self.time)]
        if self.heart_rate:
            extra.append("heart_rate=%d" % self.heart_rate)
        if self.distance:
            extra.append("distance=%d" % self.distance)
        if self.cadence:
            extra.append("cadence=%d" % self.cadence)
        if self.speed:
            extra.append("speed=%f" % self.speed)

        return ' '.join(extra)

    @property
    def float_time(self):
        """Return time as a float seconds value"""
        return float(self.elapsed_time.total_seconds())

    @property
    def improved_speed(self):
        """Return a computed speed"""
        return (5 * self.watch_speed + self.gps_speed) / 6

def parse_gpx_file(file_path):
    """
    Parse a GPX file base on it's ``file_path``to generate a
    list of GPXPoint in output
    """
    gpx_points = []

    with open(file_path, 'r') as gpx_file:
        gpx_dict = xmltodict.parse(gpx_file.read())
        track = gpx_dict.get('gpx', {}).get('trk', {}).\
                         get('trkseg', {}).get('trkpt', {})

        first = True
        for gpx_point in track:
            if first:
                start_time = parse_time(gpx_point.get('time'))
                first = False

            gpx_points.append(
                GPXPoint(
                    gpx_point.get('@lat'),
                    gpx_point.get('@lon'),
                    gpx_point.get('time'),
                    (parse_time(gpx_point.get('time')) - start_time),
                    ele=gpx_point.get('ele'),
                    heart_rate=gpx_point.get('extensions', {}).\
                        get('gpxtpx:TrackPointExtension', {}).\
                            get('gpxtpx:hr', None),
                    distance=gpx_point.get('extensions', {}).get('gpxdata:distance', None),
                    cadence=gpx_point.get('extensions', {}).get('gpxdata:cadence', None),
                    watch_speed=gpx_point.get('extensions', {}).get('gpxdata:speed', None),

                )
            )

    prev = gpx_points[0]
    gpx_points[0].gps_speed = 0

    for gpx_point in gpx_points[1:]:
        xy_dist = gpx_point.distance - prev.distance
        xy_time = gpx_point.float_time - prev.float_time

        gpx_point.gps_speed = (
            xy_dist / xy_time * 3.6
            if xy_time else prev.gps_speed
        )
        prev = gpx_point

    gpx_points[0].gps_speed = gpx_points[1].gps_speed


    return gpx_points

# import argparse
# def get_parser():
#     parser = argparse.ArgumentParser(description='Set the parameters.')
#     parser.add_argument('gpx_file')

#     return parser


# def main():
#     arg_parser = get_parser()
#     args = arg_parser.parse_args()

#     # print(parse_gpx_file(args.gpx_file,))

# if __name__ == '__main__':
#     main()
