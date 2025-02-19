import dataclasses
from typing import List, Optional
import numpy as np
import numpy.typing as npt
import xarray as xr

from FMSgridtools.shared.gridtools_utils import check_file_is_there
from FMSgridtools.shared.gridobj import GridObj

@dataclasses.dataclass
class HGridObj():
    tile: Optional[str] = None
    x: Optional[npt.NDArray] = None
    y: Optional[npt.NDArray] = None
    dx: Optional[npt.NDArray] = None
    dy: Optional[npt.NDArray] = None
    area: Optional[npt.NDArray] = None
    angle_dx: Optional[npt.NDArray] = None
    angle_dy: Optional[npt.NDArray] = None
    arcx: Optional[str] = None

    def write_out_hgrid(
            self,
            tilename,
            outfile,
            north_pole_tile: Optional[str]="none",
            north_pole_arcx: Optional[str]="none",
            projection: Optional[str]="none",
            geometry: Optional[str]="none",
            discretization: Optional[str]="none",
            conformal: Optional[str]="none",
            out_halo: Optional[int]=0,
            output_length_angle: Optional[int]=0
    ):
        if north_pole_tile == "none":
            tile = xr.DataArray(
                ["tile"],
                attrs=dict(
                    standard_name="grid_tile_spec",
                    geometry=geometry,
                    discretization=discretization,
                    conformal=conformal,
                )
            )
        elif projection == "none":
            tile = xr.DataArray(
                ["tile"],
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
                ["tile"],
                attrs=dict(
                    standard_name="grid_tile_spec",
                    geometry=geometry,
                    north_pole=north_pole_tile,
                    projection=projection,
                    discretization=discretization,
                    conformal=conformal,
                )
            )

        x = xr.DataArray(
            data=self.x,
            dims=["nyp", "nxp"],
            attrs=dict(
                units="degree_east", 
                standard_name="geographic_longitude",
            )
        )

        y = xr.DataArray(
            data=self.y,
            dims=["nyp", "nxp"],
            attrs=dict(
                units="degree_north", 
                standard_name="geographic_latitude",
            )
        )

        if output_length_angle:
            dx = xr.DataArray(
                data=self.dx,
                dims=["nyp", "nx"],
                attrs=dict(
                    units="meters", 
                    standard_name="grid_edge_x_distance",
                )
            )
            
            dy = xr.DataArray(
                data=self.dy,
                dims=["ny", "nxp"],
                attrs=dict(
                    units="meters", 
                    standard_name="grid_edge_y_distance",
                )
            )
                
            angle_dx = xr.DataArray(
                data=self.angle_dx,
                dims=["nyp", "nxp"],
                attrs=dict(
                    units="degrees_east",
                    standard_name="grid_vertex_x_angle_WRT_geographic_east",
                )
            )
            if conformal == "true":
                angle_dy = xr.DataArray(
                    data=self.angle_dy,
                    dims=["nyp", "nxp"],
                    attrs=dict(
                        units="degrees_north",
                        standard_name="grid_vertex_y_angle_WRT_geographic_north",
                    )
                )
        area = xr.DataArray(
            data=self.area,
            dims=["ny", "nx"],
            attrs=dict(
                units="m2",
                standard_name="grid_cell_area",
            )
        )

        if north_pole_arcx == "none":
            arcx = xr.DataArray(
                ["arcx"],
                attrs=dict(
                    standard_name="grid_edge_x_arc_type",
                )
            )
        else:
            arcx = xr.DataArray(
                ["arcx"],
                attrs=dict(
                    standard_name="grid_edge_x_arc_type",
                    north_pole=north_pole_arcx,
                )
            )
        if out_halo > 0:
            x.attrs["_FillValue"] = -9999.
            y.attrs["_FillValue"] = -9999.
            dx.attrs["_FillValue"] = -9999.
            dy.attrs["_FillValue"] = -9999.
            area.attrs["_FillValue"] = -9999.

