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
            url = "https://thredds.daac.ornl.gov/thredds/ncss/ornldaac/" + str(TIMESTEP[timestep]) + "/" + str(year) + \
                  "/daymet_v3_" + variable + "_" + str(year) + "_" + region + ".nc4?var=" + variable + "&north=" + \
                  str(extent[0]) + "&west=" + str(extent[3]) + "&east=" + str(extent[2]) + "&south=" + str(extent[1]) + \
                  "&disableProjSubset=on&horizStride=" + str(stride) + "&time_start=" + str(year) + \
                  "-01-01T12%3A00%3A00Z&time_end=" + str(year) + "-12-31T12%3A00%3A00Z&timeStride=" + str(stride) + \
                  "&accept=netcdf"
        elif timestep == "month":
            if variable == "prcp":
                sumstat = "monttl"
            else:
                sumstat = "monavg"
            url = "https://thredds.daac.ornl.gov/thredds/ncss/ornldaac/" + str(TIMESTEP[timestep]) + \
                  "/daymet_v3_" + variable + "_" + sumstat + "_" + str(year) + "_" + region + ".nc4?var=" + variable + "&north=" + \
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
                  "/daymet_v3_" + variable + "_" + sumstat + "_" + str(year) + "_" + region + ".nc4?var=" + variable + "&north=" + \
                  str(extent[0]) + "&west=" + str(extent[3]) + "&east=" + str(extent[2]) + "&south=" + str(extent[1]) + \
                  "&disableProjSubset=on&horizStride=" + str(stride) + "&time_start=" + str(year) + \
                  "-01-01T12%3A00%3A00Z&time_end=" + str(year) + "-12-31T12%3A00%3A00Z&timeStride=" + str(stride) + \
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
                                 str(extent[0]) + ")")
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
    """
    Downloads Datmet climate data.
    Args:
        fn: filename to save data; data are downloaded in NetCDF format and contain data for an entire calendar year
        year: year for which to download data
        variable: one of 'prcp', 'swe', 'tmax', 'tmin', 'dayl', 'vp'; check daymet documentation for variable descriptions
        timestep: one of 'day' (default), 'month', or 'year'; not that not all timesteps are available fore all variables
        region: one of 'na' (default), 'hawaii', or 'puertorico'
        extent: list of geographic coordinates (decimal degrees) in the format [north, south, east, west]
        overwrite: should download overwrite an existing file (default: False)

    Returns:

    """
    url = buildDaymetURL(year, variable, timestep, region, extent)
    if overwrite:
        if os.path.exists(fn):
            os.remove(fn)
    print(url)
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
    return


def montlyAverageDayl(year_start, year_end, output_dir, dayl_base):
    varname = 'dayl'
    daylname = 'daylavg'
    os.chdir(output_dir)
    for year in range(year_start, year_end+1):
        fn_out = "dayl_avg_s_" + str(year) + ".nc"
        fn_in = dayl_base.replace("%year%", str(year))
        gis.createMonthlyDaylNetCDF(fn_in, fn_out, daylname)
        ds_dayl = nc.Dataset(fn_in)
        month_dayl = np.zeros((12, ds_dayl.variables[varname].shape[1], ds_dayl.variables[varname].shape[2]))
        month_end_day = getMonthEndList(year)
        month_end_day[-1] = 365  # Daymet drops data for Dec 31 on leap years
        day_start = 0
        for i in range(0, len(month_end_day)):
            month_dat = ds_dayl[varname][day_start:month_end_day[i], :, :]
            month_dat[month_dat == NO_DATA_VALUE] = np.nan
            month_dayl[i, :, :] = np.average(month_dat, axis=0)
            day_start = month_end_day[i]
        ds_out = nc.Dataset(fn_out, 'r+')
        month_dayl[np.isnan(month_dayl)] = NO_DATA_VALUE
        ds_out[daylname][:] = month_dayl
        ds_out.close()
        print(year, "monthly dayl average finished")


def monthlySWEAccumulation(year_start, year_end, output_dir, swe_base):

    varname = 'swe'
    accumname = 'swe_accum'
    os.chdir(output_dir)
    for year in range(year_start, year_end+1):
        fn_out = "swe_accum_" + str(year) + ".nc"
        fn_in = swe_base.replace("%year%", str(year))
        gis.createMonthlySWENetCDF(fn_in, fn_out, accumname)
        ds_swe = nc.Dataset(fn_in)
        month_swe = np.zeros((12, ds_swe.variables['swe'].shape[1], ds_swe.variables['swe'].shape[2]))
        month_end_day = getMonthEndList(year)
        month_end_day[-1] = 365  # Daymet drops data for Dec 31 on leap years
        for i in range(0, len(month_end_day)):
            end_day = month_end_day[i] - 1
            swe_start = ds_swe[varname][i, :, :]
            swe_start[swe_start == NO_DATA_VALUE] = np.nan
            # print(ds_swe[varname].shape, end_day, month_end_day)
            swe_end = ds_swe[varname][end_day, :, :]
            swe_end[swe_end == NO_DATA_VALUE] = np.nan
            month_swe[i, :, :] = np.subtract(swe_end, swe_start)
        month_swe[np.isnan(month_swe)] = NO_DATA_VALUE
        ds_out = nc.Dataset(fn_out, 'r+')
        ds_out[accumname][:] = month_swe
        ds_out.close()
        print(year, "monthly SWE accumulation finished")


def monthlySWEMax():
    return


def monthlyWaterInput(year_start, year_end, output_dir, ppt_base, swe_base):

    os.chdir(output_dir)
    for year in range(year_start, year_end+1):
        ds_ppt = nc.Dataset(ppt_base.replace("%year%", str(year)))
        ds_swe = nc.Dataset(swe_base.replace("%year%", str(year)))
        month = 1
        ndays = ds_ppt.variables['ppt'].shape[0]
    return
