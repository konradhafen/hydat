import wget
import os

TIMESTEP = {"day": 1328, "month": 1345, "year": 1343}
VARIABLES = {"Minimum Temperature": "tmin", "Maximum Temperature": "tmax", "Precipitation": "prcp",
             "Day Length": "dayl", "Shortwave Radiation": "srad", "Snow-Water Equivalent": "swe",
             "Vapor Pressure": "vp"}
REGIONS = {"North America": "na", "Hawaii": "hawaii", "Puerto Rico": "puertorico"}


def buildDaymetURL(year, variable, timestep='day', region='na', extent=None, stride=1):
    """
    Build URL to download DayMet data by DayMet region
    Args:
        year: year to download data for
        variable: variable to download; one of tmin (minimum temperature), tmax (maximum temperature),
        prcp (precipitation), dayl (day length), srad (shortwave radiation), swe (snow-water equivalent),
        vp (vapor pressure)
        timestep: day, month, or year
        region: one of na (North America), hawaii (Hawaii), or puertorico (Puerto Rico)
        extent: list of bounding coordinates [n, s, e, w]
        stride: time stride (default: 1)

    Returns:
        url (string) to download data for a region

    """

    checkInputs(extent, region, timestep, variable)
    if extent is not None:
        if timestep == "day":
            url = "https://thredds.daac.ornl.gov/thredds/fileServer/ornldaac/" + str(TIMESTEP[timestep]) + "/" + str(year) + \
                  "/daymet_v3_" + variable + "_1980_" + region + ".nc4?var=lat&var=lon&var=" + variable + "&north=" + \
                  str(extent[0]) + "&west=" + str(extent[3]) + "&east=" + str(extent[2]) + "&south=" + str(extent[1]) + \
                  "&disableProjSubset=on&horizStride=" + str(stride) + "&time_start=" + str(year) + \
                  "-01-01T12%3A00%3A00Z&time_end=" + str(year) + "-12-30T12%3A00%3A00Z&timeStride=" + str(stride) + \
                  "&accept=netcdf"
        elif timestep == "month":
            if variable == "prcp":
                sumstat = "monttl"
            else:
                sumstat = "monavg"
            url = "https://thredds.daac.ornl.gov/thredds/ncss/ornldaac/" + str(TIMESTEP[timestep]) + \
                  "/daymet_v3_" + variable + "_" + sumstat + "_1980_" + region + ".nc4?var=lat&var=lon&var=" + variable + "&north=" + \
                  str(extent[0]) + "&west=" + str(extent[3]) + "&east=" + str(extent[2]) + "&south=" + str(extent[1]) + \
                  "&disableProjSubset=on&horizStride=" + str(stride) + "&time_start=" + str(year) + \
                  "-01-01T12%3A00%3A00Z&time_end=" + str(year) + "-12-30T12%3A00%3A00Z&timeStride=" + str(stride) + \
                  "&accept=netcdf"
        elif timestep == "year":
            if variable == "prcp":
                sumstat = "annttl"
            else:
                sumstat = "annavg"
            url = "https://thredds.daac.ornl.gov/thredds/ncss/ornldaac/" + str(TIMESTEP[timestep]) + \
                  "/daymet_v3_" + variable + "_" + sumstat + "_1980_" + region + ".nc4?var=lat&var=lon&var=" + variable + "&north=" + \
                  str(extent[0]) + "&west=" + str(extent[3]) + "&east=" + str(extent[2]) + "&south=" + str(extent[1]) + \
                  "&disableProjSubset=on&horizStride=" + str(stride) + "&time_start=" + str(year) + \
                  "-01-01T12%3A00%3A00Z&time_end=" + str(year) + "-12-30T12%3A00%3A00Z&timeStride=" + str(stride) + \
                  "&accept=netcdf"
    else:
        urlbase = 'https://thredds.daac.ornl.gov/thredds/fileServer/ornldaac/' + str(TIMESTEP[timestep]) + '/'
        if timestep == "day":
            url = urlbase + str(year) + 'daymet_v3_' + variable + '_' + str(year) + '_' + region + '.nc4'
        elif timestep == "month":
            if variable == "prcp":
                sumstat = "monttl"
            else:
                sumstat = "monavg"
            url = urlbase + 'daymet_v3_' + variable + '_' + sumstat + '_' + str(year) + '_' + region + '.nc4'
        elif timestep == "year":
            if variable == "prcp":
                sumstat = "annttl"
            else:
                sumstat = "annavg"
            url = urlbase + 'daymet_v3_' + variable + '_' + sumstat + '_' + str(year) + '_' + region + '.nc4'
        else:
            raise ValueError("Invalid Daymet timestep. Must be one of 'day', 'month', or 'year'")

    return url


def checkInputs(extent, region, timestep, variable):
    checkExtent(extent)
    checkRegion(region)
    checkTimestep(timestep)
    checkVariable(variable)
    if timestep in ["month", "year"] and variable in ["dayl", "swe", "srad"]:
        raise ValueError("'" + variable + "' is only available at a daily timestep")



def checkExtent(extent):
    if extent is not None:
        if len(extent) == 4:
            if extent[0] < extent[1]:
                raise ValueError("southern latitude (" + str(extent[1]) + ") is greater than northern latitude (" +
                                 str(extent[1]) + ")")
            elif extent[2] < extent[3]:
                raise ValueError("western longitude (" + str(extent[3]) + ") is greater than eastern longitude(" +
                                 str(extent[2]) + ")")
        else:
            raise IndexError("extent must have a length of 4")


def checkTimestep(timestep):
    if timestep not in list(TIMESTEP.keys()):
        raise ValueError("'" + timestep + "' is an invalid Daymet timestep. Must be one of " +
                         str(list(TIMESTEP.keys())))


def checkRegion(region):
    if region not in list(REGIONS.values()):
        raise ValueError("'" + region + "' is an invalid Daymet region. Must be one of " +
                         str(list(REGIONS.values())))


def checkVariable(variable):
    if variable not in list(VARIABLES.values()):
        raise ValueError("'" + variable + "' is an invalid Daymet variable. Must be one of " +
                         str(list(VARIABLES.values())))


def downloadDaymet(fn, year, variable, timestep='day', region='na', extent=None, overwrite=False):
    url = buildDaymetURL(year, variable, timestep, region, extent)
    if overwrite:
        if os.path.exists(fn):
            os.remove(fn)
    wget.download(url, fn)
