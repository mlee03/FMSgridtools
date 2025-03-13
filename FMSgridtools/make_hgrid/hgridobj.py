import dataclasses
from typing import List, Optional
import numpy as np
import numpy.typing as npt
import xarray as xr

from FMSgridtools.shared.gridtools_utils import check_file_is_there
from FMSgridtools.shared.gridobj import GridObj

class HGridObj():
    def __init__(self):
        self.tile = ""
        self.x = None
        self.y = None
        self.dx = None
        self.dy = None
        self.area = None
        self.angle_dx = None
        self.angle_dy = None
        self.arcx = ""

    def write_out_hgrid(
            self,
            tilename,
            outfile,
            nx: int,
            ny: int,
            nxp: int,
            nyp: int,
            north_pole_tile="none",
            north_pole_arcx="none",
            projection="none",
            geometry="none",
            discretization="none",
            conformal="none",
            out_halo=0,
            output_length_angle=0
    ):
        tile = None
        x = None
        y = None
        dx = None
        dy = None
        area = None
        angle_dx = None
        angle_dy = None
        arcx = None
        if north_pole_tile == "none":
            tile = xr.DataArray(
                [tilename],
                attrs=dict(
                    standard_name="grid_tile_spec",
                    geometry=geometry,
                    discretization=discretization,
                    conformal=conformal,
                )
            )
        elif projection == "none":
            tile = xr.DataArray(
                [tilename],
                attrs=dict(
                    standard_name="grid_tile_spec",
                    geometry=geometry,
                    north_pole=north_pole_tile,
                    discretization=discretization,
                    conformal=conformal,
                )
            )
        else:
            tile = xr.DataArray(
                [tilename],
                attrs=dict(
                    standard_name="grid_tile_spec",
                    geometry=geometry,
                    north_pole=north_pole_tile,
                    projection=projection,
                    discretization=discretization,
                    conformal=conformal,
                )
            )

        if self.x is not None:
            x = xr.DataArray(
                data=self.x[:(nyp*nxp)].reshape((nyp,nxp)),
                dims=["nyp", "nxp"],
                attrs=dict(
                    units="degree_east", 
                    standard_name="geographic_longitude",
                )
            )
            
        if self.y is not None:
            y = xr.DataArray(
                data=self.y[:(nyp*nxp)].reshape((nyp, nxp)),
                dims=["nyp", "nxp"],
                attrs=dict(
                    units="degree_north", 
                    standard_name="geographic_latitude",
                )
            )
    
        if output_length_angle:
            if self.dx is not None:
                dx = xr.DataArray(
                    data=self.dx[:(nyp*nx)].reshape((nyp, nx)),
                    dims=["nyp", "nx"],
                    attrs=dict(
                        units="meters", 
                        standard_name="grid_edge_x_distance",
                    )
                )
            if self.dy is not None:    
                dy = xr.DataArray(
                    data=self.dy[:(ny*nxp)].reshape((ny, nxp)),
                    dims=["ny", "nxp"],
                    attrs=dict(
                        units="meters", 
                        standard_name="grid_edge_y_distance",
                    )
                )
            if self.angle_dx is not None:   
                angle_dx = xr.DataArray(
                    data=self.angle_dx[:(nyp*nxp)].reshape((nyp, nxp)),
                    dims=["nyp", "nxp"],
                    attrs=dict(
                        units="degrees_east",
                        standard_name="grid_vertex_x_angle_WRT_geographic_east",
                    )
                )
            if out_halo > 0:
                if dx is not None:
                    dx.attrs["_FillValue"] = -9999.
                if dy is not None:
                    dy.attrs["_FillValue"] = -9999.
                if angle_dx is not None:
                    angle_dx.attrs["_FillValue"] = -9999.
            if conformal != "true":
                if self.angle_dy is not None:
                    angle_dy = xr.DataArray(
                        data=self.angle_dy.reshape((nyp, nxp)),
                        dims=["nyp", "nxp"],
                        attrs=dict(
                            units="degrees_north",
                            standard_name="grid_vertex_y_angle_WRT_geographic_north",
                        )
                    )
                if out_halo > 0:
                    if angle_dy is not None:
                        angle_dy.attrs["_FillValue"] = -9999.

        if self.area is not None:
            area = xr.DataArray(
                data=self.area[:(ny*nx)].reshape((ny, nx)),
                dims=["ny", "nx"],
                attrs=dict(
                    units="m2",
                    standard_name="grid_cell_area",
                )
            )

        if north_pole_arcx == "none":
            arcx = xr.DataArray(
                [self.arcx],
                attrs=dict(
                    standard_name="grid_edge_x_arc_type",
                )
            )
        else:
            arcx = xr.DataArray(
                [self.arcx],
                attrs=dict(
                    standard_name="grid_edge_x_arc_type",
                    north_pole=north_pole_arcx,
                )
            )
        if out_halo > 0:
            if x is not None:
                x.attrs["_FillValue"] = -9999.
            if y is not None:
                y.attrs["_FillValue"] = -9999.
            if area is not None:
                area.attrs["_FillValue"] = -9999.

        dataset = xr.Dataset(
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
        self.dataset = dataset
        dataset.to_netcdf(outfile)

    def make_gridobj(self) -> "GridObj":
        if self.dataset is None:
            tile = None
            x = None
            y = None
            dx = None
            dy = None
            angle_dx = None
            angle_dy = None
            area = None
            arcx = None
            if self.tile is not None:
                tile = xr.DataArray(
                    [self.tile]
                )
            if self.x is not None:
                x = xr.DataArray(
                    data=self.x,
                    dims=["nyp", "nxp"],
                )
            if self.y is not None:
                y = xr.DataArray(
                    data=self.y,
                    dims=["nyp", "nxp"],
                )
            if self.dx is not None:
                dx = xr.DataArray(
                    data=self.dx,
                    dims=["nyp", "nx"],
                )
            if self.dy is not None:
                dy = xr.DataArray(
                    data=self.dy,
                    dims=["ny", "nxp"],
                )
            if self.angle_dx is not None:
                angle_dx = xr.DataArray(
                    data=self.angle_dx,
                    dims=["nyp", "nxp"],
                )
            if self.angle_dy is not None:
                angle_dy = xr.DataArray(
                    data=self.angle_dy,
                    dims=["nyp", "nxp"],
                )
            if self.area is not None:
                area = xr.DataArray(
                    data=self.area,
                    dims=["ny", "nx"],
                )
            if self.arcx is not None:
                arcx = xr.DataArray(
                    [self.arcx],
                )
            dataset = xr.Dataset(
                data_vars = {
                    "tile": tile,
                    "x": x,
                    "y": y,
                    "dx": dx,
                    "dy": dy,
                    "angle_dx": angle_dx,
                    "angle_dy": angle_dy,
                    "area": area,
                    "arcx": arcx
                }
            )
        else:
            dataset=self.dataset
        return GridObj(dataset=dataset)


