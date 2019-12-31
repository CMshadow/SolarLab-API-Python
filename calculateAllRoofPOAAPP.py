"""Calculate all roof POA."""
import boto3
import json
import pvlib
from infrastructure.calculateTotalPOA import calcaulateTotalPOA

def lambda_handler(event, context):
    """Lambda invoke function."""
    print(event)
    targetLon = event['longitude']
    targetLat = event['latitude']
    azimuths = event['azimuths']
    tilts = event['tilts']
    tmy3Filename = event['weatherFilename']

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
    for i, tilt in enumerate(tilts):
        runData.append([tilt, azimuths[i], DNI, DHI, GHI, SunAz, AppSunEl])
    result = map(calcaulateTotalPOA, runData)
    result = list(result)
    minPOA = min(elem[3] for elem in result)
    print(minPOA)
    maxPOA = max(elem[2] for elem in result)
    print(maxPOA)
    everyRoofPOA = [elem[4] for elem in result]

    return {
        'minPOA': minPOA,
        'maxPOA': maxPOA,
        'everyRoofPOA': everyRoofPOA
    }
