import netCDF4 as nc


def copyNetCDF(fn_src, fn_dst, exclude_vars=[], exclude_data=[]):
    with nc.Dataset(fn_src) as src, nc.Dataset(fn_dst, "w") as dst:
        # copy global attributes all at once via dictionary
        dst.setncatts(src.__dict__)
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