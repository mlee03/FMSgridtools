import xarray as xr
import numpy as np
from FMSgridtools.shared.mosaicobj import MosaicObj
from .regionalgridobj import RegionalGridObj

def make(global_mosaic,
        regional_file): -> None
        """ Generates a horizontal grid and solo mosaic for a regional output.
        The created grid and solo mosaic could be used to regrid regional
        output data onto regular lat-lon grid."""

        #get tile number from regional file
        tile = int(list(filter(str.isdigit, regional_file))[0])

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

        global_m = MosaicObj(global_mosaic)
        global_m.griddict()
        xt = global_m.grid_dict[f'tile{tile}'].x
        xarr = xt[round(2*j_min - 2):round(2*j_min - 2 + 2*ny+1), round(2*i_min - 2):round(2*i_min - 2 + 2*nx+1)]
        yt = global_m.grid_dict[f'tile{tile}'].y
        yarr = yt[round(2*j_min - 2):round(2*j_min - 2 + 2*ny+1), round(2*i_min - 2):round(2*i_min - 2 + 2*nx+1)]

        outfile = f"regional_grid.tile{tile}.nc"
        mosaic = "regional_mosaic.nc"
        regional_grid = RegionalGridObj(tile, xarr,
                                        yarr)
        regional_grid.write_out_regional_grid(outfile)
        regional_mosaic = MosaicObj(mosaic_name="regoinal_mosaic",
                               gridfiles=np.array([outfile]),
                               gridtiles=np.array([f"tile{tile}"]))
        regional_mosaic.write_out_regional_mosaic(mosaic)

        print("\nCongratulations: You have successfully run regional mosaic")

