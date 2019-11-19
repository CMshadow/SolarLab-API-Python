"""Find the closest US tmy3 file associate with a given lon and lat."""
import boto3
from .math import surfaceDistance


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
            surfaceDistance(x['lon'], x['lat'], targetLon, targetLat)
    )

    return closestWeatherFile
