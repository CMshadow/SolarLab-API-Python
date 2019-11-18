"""Optimal Tilt calculation based on given location and azimuth."""
import boto3
import json
import math
import numpy as np
import pvlib
from multiprocessing import Process, Pipe
from infrastructure import math as myMath


def calcaulateTotalPOA(parameters, conn):
    """Calculate total POA."""
    tilt = parameters[2]
    azimuth = parameters[3]
    DNI = parameters[4]
    DHI = parameters[5]
    GHI = parameters[6]
    SunAz = parameters[7]
    AppSunEl = parameters[8]

    aoi = pvlib.irradiance.aoi(tilt, azimuth, 90 - AppSunEl, SunAz)
    eb = aoi * 0
    temp = aoi[aoi < 90]
    for i in range(len(temp)):
        temp[i] = math.cos(math.radians(temp[i]))

    eb[aoi < 90] = DNI[aoi < 90] * temp

    ediffSky = pvlib.irradiance.isotropic(tilt, DHI)
    Albedo = 0.2
    ediffGround = pvlib.irradiance.grounddiffuse(tilt, GHI, Albedo)
    totalPOA = sum(eb) + sum(ediffSky) + sum(ediffGround)
    minPOA = sum(ediffSky) + sum(ediffGround)

    hourPOA = eb + ediffSky + ediffGround
    monthlyPOA = hourPOA.values.reshape(-1, 730).sum(1)
    monthlyPOA = monthlyPOA / 1000

    conn.send([
        parameters[0], parameters[1], totalPOA, minPOA, monthlyPOA.tolist()
    ])
    conn.close()


def findClosestWeatherFile(targetLon, targetLat):
    """Find Closest Weather File in s3."""
    dynamodb = boto3.resource('dynamodb', region_name='us-west-1')
    table = dynamodb.Table('US-tmy3-index')

    wheatherFilesInfo = []

    response = table.scan()
    for i in response['Items']:
        obj = {
            'lon': float(i['lon']),
            'lat': float(i['lat']),
            'filename': i['filename']
        }
        wheatherFilesInfo.append(obj)

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])

        for i in response['Items']:
            obj = {
                'lon': float(i['lon']),
                'lat': float(i['lat']),
                'filename': i['filename']
            }
            wheatherFilesInfo.append(obj)

    closestWeatherFile = min(
        wheatherFilesInfo,
        key=lambda x:
            myMath.surfaceDistance(x['lon'], x['lat'], targetLon, targetLat)
    )

    return closestWeatherFile


def calculateOptimalTilt(tmy3Filename, userAzimuth):
    """Calculate optimal Tilt by given Azimuth and tmy3File."""

    s3 = boto3.resource('s3')
    s3.Bucket('us-tmy3').download_file(
        tmy3Filename, '/tmp/{}'.format(tmy3Filename)
    )
    tmy3Data, tmy3Metadata = pvlib.tmy.readtmy3('/tmp/{}'.format(tmy3Filename))
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

    tiltArray = np.arange(0, 60, 2)
    azimuthArray = np.array([userAzimuth])

    totalPOA = [[0]*len(azimuthArray) for i in range(len(tiltArray))]

    parent_connections = []
    processes = []
    for i in range(len(tiltArray)):
        for j in range(len(azimuthArray)):
            parent_conn, child_conn = Pipe()
            parent_connections.append(parent_conn)
            p = Process(target=calcaulateTotalPOA, args=([
                i, j, tiltArray[i], azimuthArray[j], DNI, DHI, GHI, SunAz,
                AppSunEl
            ], child_conn,))
            processes.append(p)

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    result = []
    for parent_connection in parent_connections:
        result.append(parent_connection.recv())

    for i in result:
        totalPOA[i[0]][i[1]] = i[2]
    totalPOA = np.array(totalPOA)
    optimailTiltAndAzimuth = np.unravel_index(
        totalPOA.argmax(), totalPOA.shape
    )

    optimalTilt = tiltArray[optimailTiltAndAzimuth[0]]
    optimalAzimuth = azimuthArray[optimailTiltAndAzimuth[1]]

    print(optimalTilt)
    print(optimalAzimuth)
    return int(optimalTilt)


def lambda_handler(event, context):
    """Lambda invoke function."""
    targetLon = event['longitude']
    targetLat = event['latitude']
    userAzimuth = event['azimuth']

    closestWeatherFile = findClosestWeatherFile(targetLon, targetLat)
    tmy3Filename = closestWeatherFile['filename']

    optimalTilt = calculateOptimalTilt(tmy3Filename, userAzimuth)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "optimalTilt": optimalTilt,
        }),
    }
