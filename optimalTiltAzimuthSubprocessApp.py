"""Optimal Tilt calculation based on given location and azimuth."""
import boto3
import json
import math
import time
import numpy as np
from infrastructure.calculateTotalPOA import calcaulateTotalPOA
from infrastructure.calculateTotalPOA import calcaulateTotalPOA



def calculateOptimalTiltAzimuthSubprocess(tmy3Filename, tilt, azimuth):
    """Calculate optimal Tilt and Azimuth by a tmy3File."""
    # s3 = boto3.resource('s3')
    # s3.Bucket('us-tmy3').download_file(
    #     tmy3Filename, '/tmp/{}'.format(tmy3Filename)
    # )
    # tmy3Data, tmy3Metadata = pvlib.tmy.readtmy3('/tmp/{}'.format(tmy3Filename))
    tmy3Data, tmy3Metadata = pvlib.tmy.readtmy3(tmy3Filename)
    lat = tmy3Metadata['latitude']
    lon = tmy3Metadata['longitude']

    DNI = tmy3Data.DNI
    DHI = tmy3Data.DHI
    GHI = tmy3Data.GHI
    PresPa = tmy3Data.Pressure * 100
    solar_position = pvlib.solarposition.get_solarposition(
        tmy3Data.index, lat, lon, PresPa, tmy3Data.DryBulb
    )
    SunAz = solar_position.azimuth
    AppSunEl = solar_position.apparent_elevation

    data = []
    # for t in range(0, 51, 2):
    for a in range(125, 235, 5):
        data.append([
            tilt, a, DNI, DHI, GHI, SunAz, AppSunEl
        ])

    result = map(calcaulateTotalPOA, data)
    # result = calcaulateTotalPOA([
    #     tilt, azimuth, DNI, DHI, GHI, SunAz, AppSunEl
    # ])
    # print(list(result))
    sortresult = sorted(list(result), key=lambda x: x[2], reverse=True)
    print(sortresult)
    return (sortresult[0][0], sortresult[0][1], sortresult[0][2])


def lambda_handler(event, context):
    """Lambda invoke function."""
    print(event)
    starttime = time.time()
    targetLon = event['longitude']
    targetLat = event['latitude']
    azimuths = event['azimuth']
    tilt = event['tilt']

    # closestWeatherFile = findClosestWeatherFile(targetLon, targetLat)
    # tmy3Filename = closestWeatherFile['filename']
    tmy3Filename = '701740TYA.CSV'

    result = calculateOptimalTiltAzimuthSubprocess(tmy3Filename, tilt, azimuths)
    print(time.time() - starttime)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "result": result
        }),
    }
