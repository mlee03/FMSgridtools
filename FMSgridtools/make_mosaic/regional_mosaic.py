import sys
import xarray as xr
import numpy as np
from FMSgridtools.shared.mosaicobj import MosaicObj

def make(global_mosaic,
        regional_file):
        """ Generates a horizontal grid and solo mosaic for a regional output.
        The created grid and solo mosaic could be used to regrid regional
        output data onto regular lat-lon grid."""

        #get tile number from regional file
        try:
            tile = int(list(filter(str.isdigit, regional_file))[0])
        except IndexError: 
            sys.exit("make_regional_mosaic: tile number not found in the regional_file name")

        ds = xr.open_dataset(regional_file)
        nx = ds.sizes['grid_xt_sub01']
        ny = ds.sizes['grid_yt_sub01']

        indx = ds.grid_xt_sub01.values
        indy = ds.grid_yt_sub01.values

        i_min = np.min(indx)
        i_max = np.max(indx)
        j_min = np.min(indy)
        j_max = np.max(indy)

        if i_max-i_min+1 != nx:
            print("Error: make_regional_mosaic: i_max-i_min+1 != nx")
        if j_max-j_min+1 != ny:
            print("Error: make_regional_mosaic: j_max-j_min+1 != ny")

        grid = MosaicObj(global_mosaic).griddict()
        try:
            x,y = grid[f'tile{tile}'].x, grid[f'tile{tile}'].y
        except KeyError:
            sys.exit("make_regional_mosaic: gridtile with matching tile number not found")
        xarr = x[round(2*j_min - 2):round(2*j_min - 2 + 2*ny+1), round(2*i_min - 2):round(2*i_min - 2 + 2*nx+1)]
        yarr = y[round(2*j_min - 2):round(2*j_min - 2 + 2*ny+1), round(2*i_min - 2):round(2*i_min - 2 + 2*nx+1)]

        outfile = f"regional_grid.tile{tile}.nc"
        write_out_regional_grid(tile, xarr,
                                yarr, outfile)

        mosaic = "regional_mosaic.nc"
        regional_mosaic = MosaicObj(mosaic_name="regional_mosaic",
                               gridfiles=np.array([outfile]),
                               gridtiles=np.array([f"tile{tile}"]))
        regional_mosaic.write_out_regional_mosaic(mosaic)

        print("\nCongratulations: You have successfully run regional mosaic")


def write_out_regional_grid(tile, xarr, yarr, outfile):

        tile = xr.DataArray(
            data=f'tile{tile}',
            attrs=dict(standard_name="grid_tile_spec")).astype('|S255')

        x = xr.DataArray(
            data=xarr,
            dims=["nyp", "nxp"],
            attrs=dict(
            standard_name="geographic_longitude", units="degree_east"))

        y = xr.DataArray(
            data=yarr,
            dims=["nyp", "nxp"],
            attrs=dict(
            standard_name="geographic_latitude", units="degree_north"))

        ds = xr.Dataset(
            data_vars={"tile": tile,
                       "x": x,
                       "y": y})

        encoding = {'x': {'_FillValue': None},
                    'y': {'_FillValue': None}}

        ds.to_netcdf(outfile, encoding=encoding)


