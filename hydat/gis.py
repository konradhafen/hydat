import netCDF4 as nc
import numpy as np


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


def createMonthlySWENetCDF(fn_src, fn_dst, varname):
    copyNetCDF(fn_src, fn_dst, exclude_vars=['swe', 'time', varname])
    ds = nc.Dataset(fn_dst, 'r+')
    ds.createVariable('time', np.float64, ('time',))
    ds.createVariable(varname, np.float32, ('time', 'y', 'x'))
    ds.close()
