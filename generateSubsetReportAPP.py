"""generte the report of a roof."""
import boto3
import json
import pvlib
import os
import copy
import math
import inspect
import pandas as pd
import numpy as np
import sys
from numpy import genfromtxt
sys.path.append('..')

def getDataBaseOnMonth(data):
    days = int(len(data) / 24)
    returnData = []
    for i in range(days):
        returnData.append(sum(data[i*24:(i+1)*24]))
    return returnData

def getDataOnSpecificDate(data, month, day):
    data = list(map(float, data))
    if month == 0:
        return [
            sum(data[0:744]), sum(data[744:1416]), sum(data[1416:2160]),
            sum(data[2160:2880]), sum(data[2880:3624]), sum(data[3624:4344]),
            sum(data[4344:5088]), sum(data[5088:5832]), sum(data[5832:6552]),
            sum(data[6552:7296]), sum(data[7296:8016]), sum(data[8016:8760])
        ]
    if day != 0:
        if month == 1:
            return data[0+24*(day-1):0+day*24]
        elif month == 2:
            return data[744+24*(day-1):744+day*24]
        elif month == 3:
            return data[1416+24*(day-1):1416+day*24]
        elif month == 4:
            return data[2160+24*(day-1):2160+day*24]
        elif month == 5:
            return data[2880+24*(day-1):2880+day*24]
        elif month == 6:
            return data[3624+24*(day-1):3624+day*24]
        elif month == 7:
            return data[4344+24*(day-1):4344+day*24]
        elif month == 8:
            return data[5088+24*(day-1):5088+day*24]
        elif month == 9:
            return data[5832+24*(day-1):5832+day*24]
        elif month == 10:
            return data[6552+24*(day-1):6552+day*24]
        elif month == 11:
            return data[7296+24*(day-1):7296+day*24]
        elif month == 12:
            return data[8016+24*(day-1):8016+day*24]
    else:
        if month == 1:
            return getDataBaseOnMonth(data[0:744])
        elif month == 2:
            return getDataBaseOnMonth(data[744:1416])
        elif month == 3:
            return getDataBaseOnMonth(data[1416:2160])
        elif month == 4:
            return getDataBaseOnMonth(data[2160:2880])
        elif month == 5:
            return getDataBaseOnMonth(data[2880:3624])
        elif month == 6:
            return getDataBaseOnMonth(data[3624:4344])
        elif month == 7:
            return getDataBaseOnMonth(data[4344:5088])
        elif month == 8:
            return getDataBaseOnMonth(data[5088:5832])
        elif month == 9:
            return getDataBaseOnMonth(data[5832:6552])
        elif month == 10:
            return getDataBaseOnMonth(data[6552:7296])
        elif month == 11:
            return getDataBaseOnMonth(data[7296:8016])
        elif month == 12:
            return getDataBaseOnMonth(data[8016:8760])

def getMonthsDay(month):
    if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
        return [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31]
    elif month == 4 or month == 6 or month == 9 or month == 11:
        return [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
    else:
        return [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28]


def lambda_handler(event, context):
    """Lambda invoke function."""
    targetLon = event['longitude']
    targetLat = event['latitude']
    azimuths = event['azimuths']
    tilts = event['tilts']
    tmy3Filename = event['weatherFilename']

    optimalTilt = calculateSubsetOptimal(tmy3Filename, tilts, azimuths)

    return optimalTilt
