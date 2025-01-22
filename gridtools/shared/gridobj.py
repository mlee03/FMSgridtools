import numpy as np
import numpy.typing as npt
import xarray as xr
from typing import List, Optional
import dataclasses

from gridtools.shared.gridtools_utils import check_file_is_there

@dataclasses.dataclass
class GridObj:
    grid_data: Optional[xr.Dataset] = None
    grid_file: Optional[str] = None
    x: Optional[npt.NDArray] = None
    y: Optional[npt.NDArray] = None
    dx: Optional[npt.NDArray] = None
    dy: Optional[npt.NDArray] = None
    area: Optional[npt.NDArray] = None
    angle_dx: Optional[npt.NDArray] = None
    angle_dy: Optional[npt.NDArray] = None

    def __post_init__(self):
        if self.grid_data is not None:
            self.x = self.grid_data.x.values
            self.y = self.grid_data.y.values
            self.dx = self.grid_data.dx.values
            self.dy = self.grid_data.dy.values
            self.area = self.grid_data.area.values
            self.angle_dx = self.grid_data.angle_dx.values
            self.angle_dy = self.grid_data.angle_dy.values
        elif self.grid_file is not None:
            self.from_file(self.grid_file)
        else:
            pass

    @classmethod
    def from_file(cls, filepath: str) -> "GridObj":
        """
        This class method will return an instance of GridObj with attributes
        matching the contents of the passed netcdf file containing the grid
        data.
        """
        _x = None
        _y = None
        _dx = None
        _dy = None
        _area = None
        _angle_dx = None
        _angle_dy = None
        check_file_is_there(filepath)
        with xr.open_dataset(filepath) as ds:
            return cls(
                grid_data=ds,
                grid_file=filepath,
                x = ds.x.values,
                y = ds.y.values,
                dx = ds.dx.values,
                dy = ds.dy.values,
                area = ds.area.values,
                angle_dx = ds.angle_dx.values,
                angle_dy = ds.angle_dy.values,
            )
        
    def write_out_grid(self, filepath: str):
        """
        This method will generate a netcdf file containing the contents of the
        grid_data attribute.
        """
        if self.x is not None:
            x = xr.DataArray(
                data=self.x,
                dims=["nyp", "nxp"],
                attrs=dict(
                    units="degree_east", 
                    standard_name="geographic_longitude",
                )
            )
        if self.y is not None:
            y = xr.DataArray(
                data=self.y,
                dims=["nyp", "nxp"],
                attrs=dict(
                    units="degree_north", 
                    standard_name="geographic_latitude",
                )
            )
        if self.dx is not None:
            dx = xr.DataArray(
                data=self.dx,
                dims=["nyp", "nx"],
                attrs=dict(
                    units="meters", 
                    standard_name="grid_edge_x_distance",
                )
            )
        if self.dy is not None:
            dy = xr.DataArray(
                data=self.dy,
                dims=["ny", "nxp"],
                attrs=dict(
                    units="meters", 
                    standard_name="grid_edge_y_distance",
                )
            )
        if self.area is not None:
            area = xr.DataArray(
                data=self.area,
                dims=["ny", "nx"],
                attrs=dict(
                    units="m2", 
                    standard_name="grid_cell_area",
                )
            )
        if self.angle_dx is not None:
            angle_dx = xr.DataArray(
                data=self.angle_dx,
                dims=["nyp", "nxp"],
                attrs=dict(
                    units="degrees_east", 
                    standard_name="grid_vertex_x_angle_WRT_geographic_east",
                )
            )
        if self.angle_dy is not None:
            angle_dy = xr.DataArray(
                data=self.angle_dy,
                dims=["nyp", "nxp"],
                attrs=dict(
                    units="degrees_east", 
                    standard_name="grid_vertex_x_angle_WRT_geographic_east",
                )
            )

        out_grid_dataset = xr.Dataset(
            data_vars={
                "x": x,
                "y": y,
                "dx": dx,
                "dy": dy,
                "area": area,
                "angle_dx": angle_dx,
                "angle_dy": angle_dy,
            }
        )
        out_grid_dataset.to_netcdf(filepath)

    def get_variable_list(self) -> List:
        """
        This method returns a list of variables contained within the grid_data
        dataset.
        """
        return list(self.grid_data.data_vars)

#TODO: I/O method for passing to the host