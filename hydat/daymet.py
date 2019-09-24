import wget
import os
import netCDF4 as nc
import numpy as np
import hydat.gis as gis

TIMESTEP = {"day": 1328, "month": 1345, "year": 1343}
VARIABLES = {"Minimum Temperature": "tmin", "Maximum Temperature": "tmax", "Precipitation": "prcp",
             "Day Length": "dayl", "Shortwave Radiation": "srad", "Snow-Water Equivalent": "swe",
             "Vapor Pressure": "vp"}
REGIONS = {"North America": "na", "Hawaii": "hawaii", "Puerto Rico": "puertorico"}
MONTH_END = np.cumsum(np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]))
MONTH_END_LEAP = np.cumsum(np.array([31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]))
NO_DATA_VALUE = -9999.0  # Daymet no data value


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
            url = urlbase + str(year) + '/daymet_v3_' + variable + '_' + str(year) + '_' + region + '.nc4'
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
    return


def getMonthEndList(year):
    if leap_year(year):
        return MONTH_END_LEAP
    else:
        return MONTH_END


def leap_year(y):
    if y % 400 == 0:
        return True
    if y % 100 == 0:
        return False
    if y % 4 == 0:
        return True
    else:
        return False


def monthlySWEMax():
    return


def dailySWEAccumulation(year_start, year_end, output_dir, fn_base):
    varname = 'swe'
    swe_prev = None
    swe = None
    os.chdir(output_dir)
    for year in range(year_start, year_end+1):
        fn = fn_base.replace("%year%", str(year))
        fn_out = "swe_accum_day_" + str(year) + ".nc"
        gis.copyNetCDF(fn, fn_out, exclude_data=['swe'])
        ds_out = nc.Dataset(fn_out, 'r+')
        ds = nc.Dataset(fn)
        ndays = ds.variables['swe'].shape[0]
        for day in range(0, ndays):
            if swe_prev is None:
                swe_prev = ds[varname][day, :, :]
            else:
                swe_prev = swe
            swe = ds[varname][day, :, :]
            swe[swe == NO_DATA_VALUE] = np.nan
            ds_out[varname][day, :, :] = np.subtract(swe, swe_prev)
            ds_out[varname][day, :, :][np.isnan(ds_out[varname][day, :, :])] = NO_DATA_VALUE
            print("day", day)
        ds_out.close()

        # ds_out = gis.createGDALRaster(fn_out, ds.RasterYSize, ds.RasterXSize, ndays, geot=ds.GetGeoTransform(),
        #                               drivername="NetCDF")
        # print("ds", ds.RasterXSize, ds.RasterYSize)
        # print("ds_out", ds_out.RasterXSize, ds_out.RasterYSize)
        # #ndv = ds.GetRasterBand(1).GetNoDataValue()
        # ndays=1
        # for day in range(1, ndays+1):
        #     if swe_prev is None:
        #         swe_prev = ds.GetRasterBand(1).ReadAsArray()
        #     else:
        #         swe_prev = swe
        #     print("read swe", day)
        #     swe = ds.GetRasterBand(day).ReadAsArray()
        #     print("swe read")
        #     swe[swe == ndv] = np.nan
        #     swe_accum = np.subtract(swe, swe_prev)
        #     swe_accum[np.isnan(swe_accum)] = ndv
        #     result = ds_out.GetRasterBand(day).WriteArray(swe_accum)
        #     print("write result", result)
        #     print(day, year)
        # print(year, "done")
        # del ds
        # print("ds closed")
        # del ds_out
        # print("ds_out closed")
    return


def SWEAccumulationMonthly(fn, swe_path, year, month):
    return


def SWEAdjustedPrecip():
    return
