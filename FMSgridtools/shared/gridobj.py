import dataclasses
from typing import List, Optional

import numpy as np
import numpy.typing as npt
import xarray as xr

from FMSgridtools.shared.gridtools_utils import check_file_is_there

"""
GridObj:

Dataclass for containing basic grid data to be used by other grid objects
"""
@dataclasses.dataclass
class GridObj:
    grid_data: Optional[xr.Dataset] = None
    grid_file: Optional[str] = None
    tile: Optional[str] = None
    x: Optional[npt.NDArray] = None
    y: Optional[npt.NDArray] = None
    dx: Optional[npt.NDArray] = None
    dy: Optional[npt.NDArray] = None
    area: Optional[npt.NDArray] = None
    angle_dx: Optional[npt.NDArray] = None
    angle_dy: Optional[npt.NDArray] = None
    arcx: Optional[str] = None

    def __post_init__(self):
        if self.grid_data is not None:
            varlist = list(self.grid_data.data_vars)
            if "tile" in varlist:
                self.tile = self.grid_data.tile.values.item().decode('ascii')
            if "x" in varlist:
                self.x = np.ascontiguousarray(self.grid_data.x.values)
            if "y" in varlist:
                self.y = np.ascontiguousarray(self.grid_data.y.values)
            if "dx" in varlist:
                self.dx = np.ascontiguousarray(self.grid_data.dx.values)
            if "dy" in varlist:
                self.dy = np.ascontiguousarray(self.grid_data.dy.values)
            if "area" in varlist:
                self.area = np.ascontiguousarray(self.grid_data.area.values)
            if "angle_dx" in varlist:
                self.angle_dx = np.ascontiguousarray(self.grid_data.angle_dx.values)
            if "angle_dy" in varlist:
                self.angle_dy = np.ascontiguousarray(self.grid_data.angle_dy.values)
            if "arcx" in varlist:
                self.arcx = self.grid_data.arcx.values.item().decode('ascii')
        elif self.grid_file is not None:
            check_file_is_there(self.grid_file)
            with xr.open_dataset(self.grid_file) as ds:
                self.grid_data = ds
                varlist = list(self.grid_data.data_vars)
                if "tile" in varlist:
                    self.tile = self.grid_data.tile.values.item().decode('ascii')
                if "x" in varlist:
                    self.x = np.ascontiguousarray(self.grid_data.x.values)
                if "y" in varlist:
                    self.y = np.ascontiguousarray(self.grid_data.y.values)
                if "dx" in varlist:
                    self.dx = np.ascontiguousarray(self.grid_data.dx.values)
                if "dy" in varlist:
                    self.dy = np.ascontiguousarray(self.grid_data.dy.values)
                if "area" in varlist:
                    self.area = np.ascontiguousarray(self.grid_data.area.values)
                if "angle_dx" in varlist:
                    self.angle_dx = np.ascontiguousarray(self.grid_data.angle_dx.values)
                if "angle_dy" in varlist:
                    self.angle_dy = np.ascontiguousarray(self.grid_data.angle_dy.values)
                if "arcx" in varlist:
                    self.arcx = self.grid_data.arcx.values.item().decode('ascii')
        else:
            pass

    """
    from_file:

    This class method will return an instance of GridObj with attributes
    matching the contents of the passed netcdf file containing the grid
    data.
    """
    @classmethod
    def from_file(cls, filepath: str) -> "GridObj":
        check_file_is_there(filepath)
        with xr.open_dataset(filepath) as ds:
            varlist = list(ds.data_vars)
            if "tile" in varlist:
                _tile = ds.tile.values.item().decode('ascii')
            if "x" in varlist:
                _x = np.ascontiguousarray(ds.x.values)
            if "y" in varlist:
                _y = np.ascontiguousarray(ds.y.values)
            if "dx" in varlist:
                _dx = np.ascontiguousarray(ds.dx.values)
            if "dy" in varlist:
                _dy = np.ascontiguousarray(ds.dy.values)
            if "area" in varlist:
                _area = np.ascontiguousarray(ds.area.values)
            if "angle_dx" in varlist:
                _angle_dx = np.ascontiguousarray(ds.angle_dx.values)
            if "angle_dy" in varlist:
                _angle_dy = np.ascontiguousarray(ds.angle_dy.values)
            if "arcx" in varlist:
                _arcx = ds.arcx.values.item().decode('ascii')
            return cls(
                grid_data=ds,
                grid_file=filepath,
                tile = _tile,
                x = _x,
                y = _y,
                dx = _dx,
                dy = _dy,
                area = _area,
                angle_dx = _angle_dx,
                angle_dy = _angle_dy,
                arcx = _arcx,
            )
        
    """
    write_out_grid:

    This method will generate a netcdf file containing the contents of the
    grid_data attribute.
    """
    def write_out_grid(self, filepath: str):
        if self.tile is not None:
            tile = xr.DataArray(
                [self.tile.encode("utf-8")],
                attrs=dict(
                    standard_name = "grid_tile_spec",
                    geometry = "spherical",
                    north_pole = "0.0 90.0",
                    projection = "cube_gnomonic",
                    discretization = "logically_rectangular",
                    conformal = "FALSE",
                )
            )
        else:
            tile = None
        if self.x is not None:
            x = xr.DataArray(
                data=self.x,
                dims=["nyp", "nxp"],
                attrs=dict(
                    units="degree_east",
                    standard_name="geographic_longitude",
                )
            )
        else:
            x = None
        if self.y is not None:
            y = xr.DataArray(
                data=self.y,
                dims=["nyp", "nxp"],
                attrs=dict(
                    units="degree_north",
                    standard_name="geographic_latitude",
                )
            )
        else:
            y = None
        if self.dx is not None:
            dx = xr.DataArray(
                data=self.dx,
                dims=["nyp", "nx"],
                attrs=dict(
                    units="meters",
                    standard_name="grid_edge_x_distance",
                )
            )
        else:
            dx = None
        if self.dy is not None:
            dy = xr.DataArray(
                data=self.dy,
                dims=["ny", "nxp"],
                attrs=dict(
                    units="meters",
                    standard_name="grid_edge_y_distance",
                )
            )
        else:
            dy = None
        if self.area is not None:
            area = xr.DataArray(
                data=self.area,
                dims=["ny", "nx"],
                attrs=dict(
                    units="m2",
                    standard_name="grid_cell_area",
                )
            )
        else:
            area = None
        if self.angle_dx is not None:
            angle_dx = xr.DataArray(
                data=self.angle_dx,
                dims=["nyp", "nxp"],
                attrs=dict(
                    units="degrees_east",
                    standard_name="grid_vertex_x_angle_WRT_geographic_east",
                )
            )
        else:
            angle_dx = None
        if self.angle_dy is not None:
            angle_dy = xr.DataArray(
                data=self.angle_dy,
                dims=["nyp", "nxp"],
                attrs=dict(
                    units="degrees_east",
                    standard_name="grid_vertex_x_angle_WRT_geographic_east",
                )
            )
        else:
            angle_dy = None
        if self.arcx is not None:
            arcx = xr.DataArray(
                [self.arcx.encode("utf-8")],
                attrs=dict(
                    standard_name = "grid_edge_x_arc_type",
                    north_pole = "0.0 90.0",
                )
            )
        else:
            arcx = None
        out_grid_dataset = xr.Dataset(
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
        out_grid_dataset.to_netcdf(filepath)

    """
    get_agrid_lonlat:

    This method returns the lon and lat for the A-grid as calculated from the
    x and y attributes of the GridObj.
    """
    def get_agrid_lonlat(self)-> tuple[npt.NDArray, npt.NDArray]:
        D2R = np.pi/180
        a_lon = None
        a_lat = None
        if self.x is not None and self.y is not None:
            nx = (self.x.shape[1]-1)//2
            ny = (self.x.shape[0]-1)//2
            x_flat = self.x.flatten()
            y_flat = self.y.flatten()

            a_lon = np.zeros(shape=nx)
            a_lat = np.zeros(shape=ny)

            for i in range(nx):
                a_lon[i] = x_flat[2*nx+1+2*i+1]*D2R
            for j in range(ny):
                a_lat[i] = y_flat[(2*j+1)*(2*nx+1)+1]*D2R

        return np.ascontiguousarray(a_lon), np.ascontiguousarray(a_lat)
    
    """
    get_variable_list:

    This method returns a list of variables contained within the grid_data
    dataset.
    """
    def get_variable_list(self) -> List:
        return list(self.grid_data.data_vars)

#TODO: I/O method for passing to the host
