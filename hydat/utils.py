import numpy as np
import gdal


def getPRISMFilename(year, month, var, res='4km'):
    fnbase = 'PRISM'
    mversion = 'M3'
    if year < 1981:
        if var == 'ppt':
            mversion = 'M2'
    fn = fnbase + '_' + var + '_stable_' + res + mversion + '_' + str(year) + str(month).zfill(2) + '_bil.bil'
    return fn


def monthlyGridsToNumpy(out_fn, start_year, end_year, in_dir, pvar):
    ncol = (end_year - start_year + 1) * 12
    out_arr = None
    for year in range(start_year, end_year + 1):
        for month in range(0, 12):
            ds = gdal.Open(in_dir + '/' + getPRISMFilename(year, month + 1, pvar))
            temp_arr = ds.GetRasterBand(1).ReadAsArray()
            if out_arr is None:
                out_arr = np.empty((temp_arr.size, ncol), dtype=np.float)
            colidx = (year - start_year) * 12 + month
            out_arr[:, colidx] = temp_arr.flatten()
    np.save(out_fn)