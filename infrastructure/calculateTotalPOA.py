"""Calculate Total POA."""
import math
import pvlib


def calcaulateTotalPOA(parameters):
    """Calculate total POA."""
    tilt = parameters[0]
    azimuth = parameters[1]
    DNI = parameters[2]
    DHI = parameters[3]
    GHI = parameters[4]
    SunAz = parameters[5]
    AppSunEl = parameters[6]

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

    return[parameters[0], parameters[1], totalPOA, minPOA, monthlyPOA.tolist()]
