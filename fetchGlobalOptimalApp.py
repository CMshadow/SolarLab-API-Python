"""Optimal Tilt calculation based on given location and azimuth."""
import boto3
import json
import decimal
from infrastructure.findClosestWeatherFile import findClosestWeatherFile
from boto3.dynamodb.conditions import Key


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
