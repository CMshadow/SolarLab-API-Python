"""Optimal Tilt calculation based on given location and azimuth."""
import boto3
import json
import pvlib
from infrastructure.calculateTotalPOA import calcaulateTotalPOA


def calculateSubsetOptimal(tmy3Filename, tiltList, AzimuthList):
    """Calculate optimal Tilt by given Azimuth & Tilt subsets and tmy3File."""
    tmy3FilePath = '/tmp/{}'.format(tmy3Filename)
    s3 = boto3.resource('s3')
    s3.Bucket('us-tmy3').download_file(tmy3Filename, tmy3FilePath)
    tmy3Data, tmy3Metadata = pvlib.tmy.readtmy3(tmy3FilePath)
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

    runData = []
    for tilt in tiltList:
        for azimuth in AzimuthList:
            runData.append([tilt, azimuth, DNI, DHI, GHI, SunAz, AppSunEl])

    result = map(calcaulateTotalPOA, runData)
    sortedResult = sorted(list(result), key=lambda x: x[2], reverse=True)

    return {
        'tilt': sortedResult[0][0],
        'azimuth': sortedResult[0][1],
        'totalPOA': sortedResult[0][2],
        'minPOA': sortedResult[0][3],
        'monthlyPOA': sortedResult[0][4]
    }


def lambda_handler(event, context):
    """Lambda invoke function."""
    targetLon = event['longitude']
    targetLat = event['latitude']
    azimuths = event['azimuths']
    tilts = event['tilts']
    tmy3Filename = event['weatherFilename']

    optimalTilt = calculateSubsetOptimal(tmy3Filename, tilts, azimuths)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "optimalTilt": json.dumps(optimalTilt),
        }),
    }
