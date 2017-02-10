#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import xmltodict

from converter import parse_time

class GPXPoint(object):
    lat = 0
    lon = 0
    ele = 0
    time = None
    heart_rate = 0
    cadence = 0
    distance = 0
    altitude = 0.0
    speed = 0

    def __init__(self, lat, lon, time, ele=0,
                 heart_rate=None, cadence=None, distance=None,
                 altitude=None, speed=None):
        self.lat = float(lat)
        self.lon = float(lon)
        self.time = parse_time(time)
        self.ele = int(round(float(ele)))
        self.heart_rate = int(heart_rate)
        self.cadence = int(cadence) if cadence else None
        self.distance = float(distance) if distance else None
        self.altitude = int(altitude) if altitude else None
        self.speed = float(speed) if speed else None

    def __repr__(self):
        extra = ["lat=%f lon=%f time=%s" % (self.lat, self.lon, self.time)]
        if self.heart_rate:
            extra.append("heart_rate=%d" % self.heart_rate)
        return ' '.join(extra)

def get_parser():
    parser = argparse.ArgumentParser(description='Set the parameters.')
    parser.add_argument('gpx_file')

    return parser


def main():
    arg_parser = get_parser()
    args = arg_parser.parse_args()

    gpx_points = []

    with open(args.gpx_file, 'r') as gpx_file:
        gpx_dict = xmltodict.parse(gpx_file.read())
        track = gpx_dict.get('gpx').get('trk').get('trkseg').get('trkpt')

        for gpx_point in track:
            gpx_points.append(
                GPXPoint(
                    gpx_point.get('@lat'),
                    gpx_point.get('@lon'),
                    gpx_point.get('time'),
                    ele=gpx_point.get('ele'),
                    heart_rate=gpx_point.get('extensions', {}).\
                        get('gpxtpx:TrackPointExtension', {}).\
                            get('gpxtpx:hr', None)
                )
            )

    print(gpx_points,)

if __name__ == '__main__':
    main()
