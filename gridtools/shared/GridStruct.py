import numpy as np
import numpy.typing as npt
import xarray as xr
from typing import List, Optional, Type
import dataclasses

@dataclasses.dataclass
class GridStruct:
    tile: str = None
    # geometry: str = None
    # north_pole: str = None
    # projection: str = None
    # discretization: str = None
    # conformal: bool = None
    x: npt.NDArray[np.float64] = None
    y: npt.NDArray[np.float64] = None
    dx: npt.NDArray[np.float64] = None
    dy: npt.NDArray[np.float64] = None
    area: npt.NDArray[np.float64] = None
    angle_dx: npt.NDArray[np.float64] = None
    angle_dy: npt.NDArray[np.float64] = None
    arcx: str = None

    @classmethod
    def grid_from_file(cls, file_path: str) -> "GridStruct":
        with xr.open_dataset(file_path) as ds:
            return cls(
                tile = ds.tile.values.item(),
                # geometry = ds.tile.attrs["geometry"],
                # north_pole = ds.tile.attrs["north_pole"],
                # projection = ds.tile.attrs["projeciton"],
                # discretization = ds.tile.attrs["discretization"],
                # conformal = ds.tile.conformal["conformal"],
                x = ds.x.values,
                y = ds.y.values,
                dx = ds.dx.values,
                dy = ds.dy.values,
                area = ds.area.values,
                angle_dx = ds.angle_dx.values,
                angle_dy = ds.angle_dy.values,
                arcx = ds.arcx.values.item(),
            )    
        
    def write_out_grid(self, file_path: str):
        tile = xr.DataArray(
            [self.tile],
            attrs=dict(
                standard_name="grid_tile_spec",
                geometry="spherical",
                north_pole="0.0 90.0",
                projection="cube_gnomonic",
                discretization="logically_rectangular",
                conformal="False",
            )
        )
        x = xr.DataArray(
            data=self.x,
            dims=["nyp", "nxp"],
            attrs=dict(
                standard_name="geographic_longitude",
                units="degree_east",
                _FillValue=False,
            )
        )
        y = xr.DataArray(
            data=self.y,
            dims=["nyp", "nxp"],
            attrs=dict(
                standard_name="geographic_latitude",
                units="degree north",
                _FillValue=False,
            )
        )
        dx = xr.DataArray(
            data=self.dx,
            dims=["nyp", "nx"],
            attrs=dict(
                standard_name="grid_edge_x_distance",
                units="meters",
                _FillValue=False,
            )
        )
        dy = xr.DataArray(
            data=self.dy,
            dims=["ny", "nxp"],
            attrs=dict(
                standard_name="grid_edge_y_distance",
                units="meters",
                _FillValue=False,
            )
        )
        area = xr.DataArray(
            data=self.area,
            dims=["ny", "nx"],
            attrs=dict(
                standard_name="grid_cell_area",
                units="m2",
                _FillValue=False,
            )
        )
        angle_dx = xr.DataArray(
            data=self.angle_dx,
            dims=["nyp", "nxp"],
            attrs=dict(
                standard_name="grid_vertex_x_angle_WRT_geographic_east",
                units="degrees_east",
                _FillValue=False,
            )
        )
        angle_dy = xr.DataArray(
            data=self.angle_dy,
            dims=["nyp", "nxp"],
            attrs=dict(
                standard_name="grid_vertex_y_angle_WRT_geographic_north",
                units="degrees_north",
                _FillValue=False,
            )
        )
        arcx = xr.DataArray(
            [self.arcx],
            attrs=dict(
                standard_name="grid_edge_x_arc_type",
                north_pole="0.0 90.0",
                _FillValue=False,
            )
        )

        out = xr.Dataset(
            data_vars={
                "tile": tile,
                "x": x,
                "y": y,
                "dx": dx,
                "dy": dy,
                "area": area,
                "angle_dx": angle_dx,
                "angle_dy": angle_dy,
                "arcx": arcx,
            }
        )
        out.to_netcdf(file_path)
    
    #TODO: I/O method for passing to the host