"""
GridObj:
Class for containing basic grid data to be used by other grid objects
"""

import logging
from pathlib import Path

import numpy as np
import numpy.typing as npt
import xarray as xr

import pyfms

logger = logging.getLogger(__name__)

attrs = {}
attrs["x"] = dict(
    standard_name = "geographic_longitude",
    units = "degree_east",
    _FillValue = False
)
attrs["y"] = dict(
    standard_name = "geographic_latitude",
    units = "degrees_north",
    _FillValue = False
)
attrs["tile"] = {}
attrs["tile_options"] = {}
attrs["tile_options"]["cubic"] = dict(
    standard_name = "grid_tile_spec",
    geometry = "spherical",
    north_pole = "0.0 90.0",
    discretization = "logically_rectangular",
    conformal = "false",
    _FillValue = False
)
attrs["tile_options"]["simple_cartesian"] = dict(
    standard_name = "grid_tile_spec",
    geometry = "planar",
    discretization = "logically_rectangular",
    conformal = "true",
    _FillValue = False
)
attrs["tile_options"]["none"] = dict(
    standard_name = "grid_tile_spec",
    geometry = "spherical",
    north_pole = "0.0 90.0",
    projection = "none",
    discretization = "logically_rectangular",
    conformal = "true",
    _FillValue = False
)

attrs["dx"] = dict(
    standard_name = "grid_edge_x_distance",
    units = "meters",
    _FillValue = False
)
attrs["dy"] = dict(
    standard_name = "grid_edge_y_distance",
    units = "meters",
    _FillValue = False
)
attrs["area"] = dict(
    standard_name = "grid_cell_area",
    units = "m2",
    _FillValue = False
)
attrs["angle_dx"] = dict(
    standard_name = "grid_vertex_x_angle_WRT_geographic_east",
    units = "degrees_east",
    _FillValue = False
)
attrs["angle_dy"] = dict(
    standard_name = "grid_vertex_y_angle_WRT_geographic_north",
    units = "degrees_north",
    _FillValue = False
)
attrs["arcx"] = dict(
    standard_name = "grid_edge_x_arc_type",
    north_pole = "0.0,90.0",
    _FillValue = False
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

class Variable:
    def __init__(self, name: str = None, data = None):
        self.name = name
        self.data = data

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
                 arcx: npt.NDArray = None
    ):

        self.input_dir = Path(input_dir)
        self.gridfile = gridfile
        self.domain = domain

        self.nx = nx
        self.ny = ny
        self.nxp = nxp
        self.nyp = nyp

        self.gridtype = gridtype

        self.x_obj = Variable(name="x", data=x)
        self.y_obj = Variable(name="y", data=y)
        self.tile_obj = Variable(name="tile", data=tile)
        self.dx_obj = Variable(name="dx", data=dx)
        self.dy_obj = Variable(name="dy", data=dy)
        self.area_obj = Variable(name="area", data=area)
        self.angle_dx_obj = Variable(name="angle_dx", data=angle_dx)
        self.angle_dy_obj = Variable(name="angle_dy", data=angle_dy)
        self.arcx_obj = Variable(name="arcx", data=arcx)

        self._set_dims()

        logger.info("Created new GridObj named:\n %s", self.__repr__())


    def to_domain(self, domain: dict = None):

        """
        Stores data on the compute domain
        """

        if domain is None:
            if self.domain is None:
                logger.error("Please specify Domain object from pyfms")
            domain = self.domain
        else:
            if self.domain is not None:
                logger.warning("Overwriting %s with %s", self.domain, domain)
                self.domain = domain

        if not pyfms.fms.module_is_initialized():
            logger.error("Please initialize pyfms first")

        isc, jsc = self.domain.isc, self.domain.jsc
        xsize_c, ysize_c = self.domain.xsize_c, self.domain.ysize_c

        objdict = {
            self.x_obj: (ysize_c+1, xsize_c+1),
            self.y_obj: (ysize_c+1, xsize_c+1),
            self.area_obj: (ysize_c, xsize_c),
            self.dx_obj: (ysize_c+1, xsize_c),
            self.dy_obj: (ysize_c, xsize_c+1),
            self.angle_dx_obj: (ysize_c+1, xsize_c),
            self.angle_dy_obj: (ysize_c, xsize_c+1)
        }

        for obj, (ysize, xsize) in objdict.items():
            if obj.data is not None:
                logger.info("Saving %s on domain", {obj.name})
                obj.data = np.ascontiguousarray(obj.data[jsc:jsc+ysize, isc:isc+xsize])

        self._set_dims()

        return self


    def to_radians(self):

        """
        Converts data from degres to radians
        """

        objlist = [self.x_obj, self.y_obj, self.dx_obj, self.dy_obj, self.angle_dx_obj, self.angle_dy_obj]
        for obj in objlist:
            if obj.data is not None:
                logger.info("Converting %s to radians", {obj.name})
                obj.data = np.radians(obj.data, dtype=np.float64)


    def get_fms_area(self):

        """
        Compute grid cell areas
        """

        logger.info("Computing grid cell area with fms")

        if not pyfms.fms.module_is_initialized():
            logger.error("Please initialize pyfms first")

        x = np.ascontiguousarray(self.x, dtype=np.float64)
        y = np.ascontiguousarray(self.y, dtype=np.float64)
        self.area = pyfms.grid_utils.get_grid_area(lon=x, lat=y, convert_cf_order=False)
        return self.area


    def read(self, radians: bool = False, center: bool = False, on_domain: bool = False, xy_only: bool = False):

        """
        Reads in the gridfile and initializes the instance variables
        """

        objlist = [self.x_obj, self.y_obj]
        if xy_only:
            logger.info("reading only x and y coordinates from file %s", {self.gridfile})
        else:
            objlist += [self.area_obj, self.dx_obj, self.dy_obj, self.angle_dx_obj,
                        self.angle_dy_obj, self.arcx_obj, self.tile_obj
            ]
            logger.info("reading in file %s\n", self.gridfile)

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
                self.to_domain()

            self._set_dims()

            logger.info("Finished reading file %s\n %s", self.gridfile, self.__repr__())

        return self


    def write(self, gridfile: str = None):

        """
        Generate a netcdf file containing grid content
        """

        if gridfile is None:
            if self.gridfile is None:
                logger.error("Please provide gridfile name")
            gridfile = self.gridfile

        logger.info("Writing out gridfile %s", {gridfile})

        if self.gridtype == "none":
            attrs["tile"] = attrs["tile_options"]["none"]
        elif self.gridtype == "cubic":
            attrs["tile"] = attrs["tile_options"]["cubic"]
        elif self.gridtype == "simple_cartesian":
            attrs["tile"] = attrs["tile_options"]["simple_cartesian"]

        objlist = [self.x_obj, self.y_obj, self.dx_obj, self.dy_obj, self.area_obj,
        self.angle_dx_obj, self.angle_dy_obj, self.arcx_obj, self.tile_obj]

        ds = {}
        for obj in objlist:
            if obj.data is not None:
                name = obj.name
                ds[name] = xr.DataArray(
                    data = obj.data,
                    attrs = attrs[name],
                    dims=dims[name]
                )
                logger.info(ds[name])

        xr.Dataset(data_vars=ds).to_netcdf(gridfile)


    def _set_dims(self):

        if self.x_obj.data is None:
            logger.warning("Cannot set dimensions if x and y coordinates are not set")
        else:
            self.nyp, self.nxp = self.x_obj.data.shape
            self.ny = self.nyp - 1
            self.nx = self.nxp - 1


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
        summary = "%s\n" % (self.__class__.__name__)
        summary += "gridfile = %s\n" % (self.gridfile)
        summary += "gridtype = %s\n" % (self.gridtype)
        summary += "nx = %s\n" % (self.nx)
        summary += "ny = %s\n" % (self.ny)
        summary += "nxp = %s\n" %(self.nxp)
        summary += "nyp = %s\n" %(self.nyp)

        objlist = [self.x_obj, self.y_obj, self.dx_obj, self.dy_obj, self.area_obj,
        self.angle_dx_obj, self.angle_dy_obj, self.arcx_obj, self.tile_obj]

        for obj in objlist:
            summary += "%s = %s\n" % (obj.name, obj.data)

        return summary






