import urllib

TIMESTEP = {"day": 1328, "month": 1345, "year": 1343}
VARIABLES = ["tmin", "tmax", "prcp", "dayl", "srad", "swe", "vp"]
REGIONS = ["na", "hawaii", "puertorico"]

def buildURL(year, variable, timestep='day', region='na', extent=[]):
    """
    Build URL to download DayMet data by DayMet region
    Args:
        year: year to download data for
        variable: variable to download; one of tmin (minimum temperature), tmax (maximum temperature),
        prcp (precipitation), dayl (day length), srad (shortwave radiation), swe (snow-water equivalent),
        vp (vapor pressure)
        timestep: day, month, or year
        region: one of na (North America), hawaii (Hawaii), or puertorico (Puerto Rico)
        extent: 

    Returns:
        url (string) to download data for a region

    """
    urlBase = 'https://thredds.daac.ornl.gov/thredds/fileServer/ornldaac/' + TIMESTEP[timestep] + '/'
    url = urlBase + str(year) + '/daymet_v3_' + variable + '_' + str(year) + '_' + region + '.nc4'
    return url

def downloadURL(url, fn):
