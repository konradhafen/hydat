import netCDF4 as nc
import numpy as np


def createNetCDF(fn, xvals, yvals, varname, format='NETCDF4'):
    ds = nc.Dataset(fn, 'w', format=format)
    ds.createDimension('x', len(xvals))
    ds.createDimension('y', len(yvals))
    ds.createDimension('time', None)
    ds.createVariable('time', np.int, ('time',))
    ds.createVariable('x', np.float, ('x',))
    ds.createVariable('y', np.float, ('y',))
    ds.createVariable(varname, np.float, ('time', 'x', 'y'))
    return ds




