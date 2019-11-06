import netCDF4 as nc
import numpy as np
import gdal


def copyNetCDF(fn_src, fn_dst, exclude_vars=[], exclude_data=[]):
    """
    Creates a copy of a NetCDF dataset
    Args:
        fn_src: filename of dataset to copy
        fn_dst: filename to save copied dataset
        exclude_vars: list of variables to exclude during copy
        exclude_data: list of data to exclude during copy; if a variable is excluded its data is automatically excluded

    Returns:

    """
    with nc.Dataset(fn_src) as src, nc.Dataset(fn_dst, "w") as dst:
        # copy global attributes all at once via dictionary
        exclude = ['_NCProperties']
        setdict = {i:src.__dict__[i] for i in src.__dict__ if i not in exclude}  # don't copy NCProperties, it throws an error
        dst.setncatts(setdict)
        # copy dimensions
        for name, dimension in src.dimensions.items():
            dst.createDimension(
                name, (len(dimension) if not dimension.isunlimited() else None))
        # copy all file data except for the excluded
        for name, variable in src.variables.items():
            if name not in exclude_vars:
                x = dst.createVariable(name, variable.datatype, variable.dimensions)
                # copy variable attributes all at once via dictionary
                if name not in exclude_data:
                    dst[name][:] = src[name][:]
                dst[name].setncatts(src[name].__dict__)


def createMonthlyDaylNetCDF(fn_src, fn_dst, varname):
    copyNetCDF(fn_src, fn_dst, exclude_vars=['dayl', 'time', varname])
    ds = nc.Dataset(fn_dst, 'r+')
    ds.createVariable('time', np.float64, ('time',))
    ds.createVariable(varname, np.float32, ('time', 'y', 'x'))
    ds.close()


def createMonthlySWENetCDF(fn_src, fn_dst, varname):
    copyNetCDF(fn_src, fn_dst, exclude_vars=['swe', 'time', varname])
    ds = nc.Dataset(fn_dst, 'r+')
    ds.createVariable('time', np.float64, ('time',))
    ds.createVariable(varname, np.float32, ('time', 'y', 'x'))
    ds.close()
    return


def indexRaster(src, dst, is_netcdf=False, var_name=None, no_data=-9999.0):
    if is_netcdf:
        ds = gdal.Open("NETCDF:" + src + ":" + var_name)
    else:
        ds = gdal.Open(src)

    band = ds.GetRasterBand(1).ReadAsArray()

    idx = np.arange(0, ds.RasterXSize*ds.RasterYSize).reshape((ds.RasterYSize, ds.RasterXSize))
    print(idx.shape, band.shape)
    idx[band == no_data] = no_data
    writeArrayAsRaster(dst, idx, ds.RasterYSize, ds.RasterXSize, ds.GetGeoTransform(), ds.GetProjection(),
                       nodata=no_data, nan=no_data)

    # if ds is not None:
    #     print(ds.GetProjection())
    #     geot = ds.GetGeoTransform()
    #     proj = ds.GetProjection()
    #     # print("min x: ", geot[0], "max x:", geot[0] + ds.RasterXSize*geot[1], "min y: ", geot[3] + ds.RasterYSize*geot[5], "max y:", geot[3])
    #     minx = geot[0]-0.0*geot[1]
    #     maxy = geot[3]-0.5*geot[5]
    #     extent = (minx, maxy + ds.RasterYSize*geot[5], minx + ds.RasterXSize*geot[1], maxy)
    #     gdal.Warp(fn_out, fn, dstSRS='EPSG:5070', outputBounds=extent, outputBoundsSRS=proj, width=ds.RasterXSize, height=ds.RasterYSize)
    #     # gdal.Warp(fn_out, fn, dstSRS='EPSG:5070', width=ds.RasterXSize, height=ds.RasterYSize)
    # else:
    #     print("error opening netcdf")

    print('done')
    return


def writeArrayAsRaster(path, array, rows, cols, geot, srs, nodata=-9999.0, nan=-9999.0, datatype=gdal.GDT_Float32,
                       drivername='GTiff'):
    """
    Write array to a raster dataset

    Args:
        path: output file for raster
        array: array containing data
        rows: number of rows in array
        cols: number of columns in array
        geot: affine geotransformation for the output raster
        srs: spatial reference for the output raster (default: None)
        nodata: no data value for the output raster (default: -9999)
        nan: value in array that should be written as nodata (default: -9999)
        datatype: gdal data type of output raster (default: GDT_Float32)
        drivername: Name of GDAL driver to use to create raster (default: 'GTiff')

    Returns:
        None

    """
    driver = gdal.GetDriverByName(drivername)
    bands = 1
    multi = False
    if len(array.shape) == 3:
        bands = array.shape[0]
        multi = True
    ds = driver.Create(path, xsize=cols, ysize=rows, bands=bands, eType=datatype)
    ds.SetProjection(srs)
    ds.SetGeoTransform(geot)
    array = np.where((array==np.nan) | (array==nan), nodata, array)
    for band in range(bands):
        print('writing band', band+1, 'of', bands)
        if multi:
            ds.GetRasterBand(band+1).WriteArray(array[band,:,:])
        else:
            ds.GetRasterBand(band + 1).WriteArray(array)
        ds.GetRasterBand(band+1).SetNoDataValue(nodata)
        ds.GetRasterBand(band+1).FlushCache()
    ds = None
    return None
