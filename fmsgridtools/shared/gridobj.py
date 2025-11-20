"""
GridObj:
Class for containing basic grid data to be used by other grid objects
"""

import logging
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import numpy.typing as npt
import xarray as xr

import pyfms

logger = logging.getLogger(__name__)

attrs = {}
attrs["x"] = dict(
    standard_name = "geographic_longitude",
    units = "degree_east"
)
attrs["y"] = dict(
    standard_name = "geographic_latitude",
    units = "degrees_north"
)
attrs["tile"] = {}
attrs["tile_options"] = {}
attrs["tile_options"]["cubic"] = dict(
    standard_name = "grid_tile_spec",
    geometry = "spherical",
    north_pole = "0.0 90.0",
    discretization = "logically_rectangular",
    conformal = "false"
)
attrs["tile_options"]["simple_cartesian"] = dict(
    standard_name = "grid_tile_spec",
    geometry = "planar",
    discretization = "logically_rectangular",
    conformal = "true"
)
attrs["tile_options"]["none"] = dict(
    standard_name = "grid_tile_spec",
    geometry = "spherical",
    north_pole = "0.0 90.0",
    projection = "none",
    discretization = "logically_rectangular",
    conformal = "true"
)

attrs["dx"] = dict(
    standard_name = "grid_edge_x_distance",
    units = "meters"
)
attrs["dy"] = dict(
    standard_name = "grid_edge_y_distance",
    units = "meters"
)
attrs["area"] = dict(
    standard_name = "grid_cell_area",
    units = "m2"
)
attrs["angle_dx"] = dict(
    standard_name = "grid_vertex_x_angle_WRT_geographic_east",
    units = "degrees_east"
)
attrs["angle_dy"] = dict(
    standard_name = "grid_vertex_y_angle_WRT_geographic_north",
    units = "degrees_north"
)
attrs["arcx"] = dict(
    standard_name = "grid_edge_x_arc_type",
    north_pole = "0.0,90.0"
)

dims = {}
dims["x"] = ["nyp", "nxp"]
dims["y"] = ["nyp", "nxp"]
dims["dx"] = ["nyp", "nx"]
dims["dy"] = ["ny", "nxp"]
dims["area"] = ["ny", "nx"]
dims["angle_dx"] = ["nyp", "nxp"]
dims["angle_dy"] = ["nyp", "nxp"]
dims["tile"] = ()
dims["arcx"] = ()

class GridObj:

    """
    Class for grid information
    """

    def __init__(self,
                 input_dir: str = "./",
                 gridfile: str = None,
                 domain: pyfms.Domain = None,
                 gridtype: str = None,
                 tile: str = None,
                 nx: int = None,
                 ny: int = None,
                 nxp: int = None,
                 nyp: int = None,
                 x: npt.NDArray = None,
                 y: npt.NDArray = None,
                 dx: npt.NDArray = None,
                 dy: npt.NDArray = None,
                 area: npt.NDArray = None,
                 angle_dx: npt.NDArray = None,
                 angle_dy: npt.NDArray = None,
                 arcx: npt.NDArray = None,
                 on_gpu: bool = False
    ):

        self.input_dir = Path(input_dir)
        self.gridfile = gridfile
        self.domain = domain

        self.nx = nx
        self.ny = ny
        self.nxp = nxp
        self.nyp = nyp

        self.gridtype = gridtype

        self.x_obj = SimpleNamespace(
            name="x",
            data=x,
        )
        self.y_obj = SimpleNamespace(
            name="y",
            data=y,
        )
        self.tile_obj = SimpleNamespace(
            name="tile",
            data=tile,
        )
        self.dx_obj = SimpleNamespace(
            name="dx",
            data=dx,
        )
        self.dy_obj = SimpleNamespace(
            name="dy",
            data=dy,
        )
        self.area_obj = SimpleNamespace(
            name="area",
            data=area,
        )
        self.angle_dx_obj = SimpleNamespace(
            name="angle_dx",
            data=angle_dx,
        )
        self.angle_dy_obj = SimpleNamespace(
            name="angle_dy",
            data=angle_dy,
        )
        self.arcx_obj = SimpleNamespace(
            name="arcx",
            data=arcx,
        )
        self.objlist = [
            self.x_obj,
            self.y_obj,
            self.dx_obj,
            self.dy_obj,
            self.area_obj,
            self.angle_dx_obj,
            self.angle_dy_obj,
            self.arcx_obj,
            self.tile_obj
        ]
        

    def to_domain(self):

        """
        Stores data on the compute domain
        """

        isc, iec, jsc, jec = self.domain.isc, self.domain.iec, self.domain.jsc, self.domain.jec

        for obj in self.objlist:            
            if obj.data is not None and not self.arcx_obj:
                logger.info("saving %s on domain", {obj.name})
                edge = 1 if obj is self.area_obj else 2
                obj.data = np.ascontiguousarray(obj.data[jsc:jec+edge, isc:iec+edge])

        self._set_dims(on_domain=True)

        return self


    def to_radians(self):

        """
        Converts data from degres to radians
        """

        objlist = [self.x_obj, self.y_obj, self.dx_obj, self.dy_obj, self.angle_dx_obj, self.angle_dy_obj]
        for obj in objlist:
            if obj.data is not None:
                logger.info("converting %s to radians", {obj.name})
                obj.data = np.radians(obj.data, dtype=np.float64)
   

    def get_fms_area(self):

        """
        Compute grid cell areas
        """

        logger.info("computing grid cell area with fms")

        x = np.ascontiguousarray(self.x, dtype=np.float64)
        y = np.ascontiguousarray(self.y, dtype=np.float64)
        self.area = pyfms.grid_utils.get_grid_area(lon=x, lat=y, convert_cf_order=False)
        return self.area


    def read(self, radians: bool = False, center: bool = False, on_domain: bool = False, xy_only: bool = True):

        """
        Reads in the gridfile and initializes the instance variables
        """

        if xy_only:
            logger.info("reading only x and y coordinates from file %s", {self.gridfile})
            objlist = [self.x_obj, self.y_obj]            
        else:
            objlist = self.objlist
            logger.info(f"reading in file {self.gridfile}")

        with xr.open_dataset(self.input_dir/self.gridfile) as ds:
            for obj in objlist:
                if obj.name in ds:
                    obj.data = ds[obj.name].data
                    if center:
                        logger.info("saving center points for %s", {obj.name})
                        obj.data = np.ascontiguousarray(obj.data[::2, ::2])
                else:
                    logger.error("could not %s in %s", {obj.name}, {self.gridfile})
            
            if radians:
                self.to_radians()
        
            if on_domain:
                if self.domain is None:
                    logger.error("please specify domain by ")
                self.to_domain()

            self._set_dims(ds.sizes, center=center, on_domain=on_domain)

        return self


    def write(self, gridfile: str = None):

        """
        write_out_grid:
        This method will generate a netcdf file containing grid content
        """

        if gridfile is None:
            if self.gridfile is None: 
                logger.error("must provide gridfile name")
            gridfile = self.gridfile

        logger.info()"writing out gridfile %s", {gridfile})

        if self.gridtype == "none":
            attrs["tile"] = attrs["tile_options"]["none"]
        elif self.gridtype == "cubic":
            attrs["tile"] = attrs["tile_options"]["cubic"]
        elif self.gridtype == "simple_cartesian":
            attrs["tile"] = attrs["tile_options"]["simple_cartesian"]

        ds = {}
        for obj in self.objlist:
            if obj.data is not None:
                name = obj.name
                ds[name] = xr.DataArray(
                    data = obj.data,
                    attrs = attrs[name],
                    dims=dims[name]
                )
                logger.info(ds[name])

        xr.Dataset(data_vars=ds).to_netcdf(gridfile)


    def _set_dims(self, dims: dict = None, center: bool = True, on_domain: bool = False):


        if on_domain:
            self.nx = self.domain.xsize_c
            self.ny = self.domain.ysize_c
            self.nxp = self.nx + 1
            self.nyp = self.ny + 1
            return

        self.nxp = dims.get("nxp")
        self.nyp = dims.get("nyp")
        self.nx = dims.get("nx")
        self.ny = dims.get("ny")

        #nx
        if self.nxp is None:
            if self.nx is None:
                logger.error("cannot set dimension nxp")
            self.nxp = self.nx + 1
        elif self.nx is None:
            if self.nxp is None:
                logger.error("cannot set dimension nx")
            self.nx = self.nxp - 1

        #ny
        if self.nyp is None:
            if self.ny is None:
                logger.error("cannot set dimension nyp")
            self.nyp = self.ny + 1
        elif self.ny is None:
            if self.nyp is None:
                logger.error("cannot set dimension ny")
            self.ny = self.nyp - 1

        if center:
            self.nx = self.nx // 2
            self.ny = self.ny // 2
            self.nxp = self.nx + 1
            self.nyp = self.ny + 1


    @property
    def x(self):

        """
        retrieve x
        """

        return self.x_obj.data

    @x.setter
    def x(self, data):

        """
        set x
        """

        self.x_obj.data = data

    @property
    def y(self):

        """
        retrieve y
        """

        return self.y_obj.data

    @y.setter
    def y(self, data):

        """
        set y
        """

        self.y_obj.data = data

    @property
    def tile(self):

        """"
        retrieve tile
        """

        return self.tile_obj.data

    @tile.setter
    def tile(self, data):

        """
        set tile
        """

        self.tile_obj.data = data

    @property
    def dx(self):

        """
        retrieve dx
        """

        return self.dx_obj.data

    @dx.setter
    def dx(self, data):

        """
        set dx
        """

        self.dx_obj.data = data

    @property
    def dy(self):

        """
        retrieve dy
        """

        return self.dy_obj.data

    @dy.setter
    def dy(self, data):

        """
        set dy
        """

        self.dy_obj.data = data

    @property
    def area(self):

        """
        retrieve area
        """

        return self.area_obj.data

    @area.setter
    def area(self, data):

        """
        set area
        """

        self.area_obj.data = data

    @property
    def angle_dx(self):

        """
        retrieve angle_dx
        """

        return self.angle_dx_obj.data

    @angle_dx.setter
    def angle_dx(self, data):

        """
        set angle_dx
        """

        self.angle_dx_obj.data = data

    @property
    def angle_dy(self):

        """
        retrieve angle_dy
        """

        return self.angle_dy_obj.data

    @angle_dy.setter
    def angle_dy(self, data):

        """
        set angle_dy
        """

        self.angle_dy_obj.data = data

    @property
    def arcx(self):

        """
        retrieve arcx
        """

        return self.arcx_obj.data

    @arcx.setter
    def arcx(self, data):

        """
        set arcx
        """

        self.arcx_obj.data = data


    def __repr__(self):
        summary = f"\n\nGrid for {self.gridfile}, tile = {self.tile_obj.name}\n"
        summary += "nx = {:>5} ny = {:>5} nxp = {:>5} nyp = {:>5}\n".format(self.nx, self.ny, self.nxp, self.nyp)
        summary += f"gridtype = {self.gridtype}\n"

        for obj in self.objlist:
            summary += f"{obj.name} = {obj.data}\n"

        return summary






