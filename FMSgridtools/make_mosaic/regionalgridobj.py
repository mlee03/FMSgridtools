import numpy as np
import xarray as xr
import numpy.typing as npt

class RegionalGridObj(self, 
                      tile: int,
                      x: npt.NDArray,
                      y: npt.NDArray):   
    
    self.tile: tile
    self.x = x
    self.y = y


    def write_out_regional_grid(self, outfile: str):

        tile = xr.DataArray(
            data=f'tile{self.tile}',
            attrs=dict(standard_name="grid_tile_spec")).astype('|S255')

        x = xr.DataArray(
            data=self.x,
            dims=["nyp", "nxp"],
            attrs=dict(
            standard_name="geographic_longitude", units="degree_east"))

        y = xr.DataArray(
            data=self.y,
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
