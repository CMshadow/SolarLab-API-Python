"""Optimal Tilt calculation based on given location and azimuth."""
import boto3
import json
import decimal
from infrastructure import math as myMath
from boto3.dynamodb.conditions import Key


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


def fetchGlobalOptimal(tmy3Lon, tmy3Lat):
    """Fetch global optimal Tilt and Azimuth by given tmy3file lon and lat."""

    dynamodb = boto3.resource('dynamodb', region_name='us-west-1')
    table = dynamodb.Table('US-OptimalTiltAzimuth')

    response = table.query(
        KeyConditionExpression=Key('longitude')
        .eq(decimal.Decimal(str(tmy3Lon))) &
        Key('latitude').eq(decimal.Decimal(str(tmy3Lat)))
    )

    optimalTilt = float(response['Items'][0]['optimalTilt'])
    optimalAzimuth = float(response['Items'][0]['optimalAzimuth'])

    return (optimalTilt, optimalAzimuth)


def lambda_handler(event, context):
    """Lambda invoke function."""
    targetLon = event['longitude']
    targetLat = event['latitude']

    closestWeatherFile = findClosestWeatherFile(targetLon, targetLat)
    tmy3lon = closestWeatherFile['lon']
    tmy3lat = closestWeatherFile['lat']

    optimalTilt, optimalAzimuth = fetchGlobalOptimal(tmy3lon, tmy3lat)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "optimalTilt": optimalTilt,
            "optimalAzimuth": optimalAzimuth
        }),
    }
