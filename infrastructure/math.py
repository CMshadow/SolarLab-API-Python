"""Helping Math."""
from math import sin, cos, sqrt, atan2, radians


def surfaceDistance(lon1, lat1, lon2, lat2):
    """Surface distance between two longitudes & latitudes."""
    R = 6371000
    lat1Radians = radians(lat1)
    lat2Radians = radians(lat2)
    latDelta = radians(lat2 - lat1)
    lonDelta = radians(lon2 - lon1)

    a = sin(latDelta / 2) * sin(latDelta / 2) + \
        cos(lat1Radians) * cos(lat2Radians) * \
        sin(lonDelta / 2) * sin(lonDelta / 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c
