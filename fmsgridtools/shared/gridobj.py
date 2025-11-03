import numpy as np
import numpy.typing as npt
from pathlib import Path
from types import SimpleNamespace
import xarray as xr

import pyfms
from fmsgridtools.shared.gridtools_utils import check_file_is_there


"""
GridObj:
Class for containing basic grid data to be used by other grid objects
"""

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
                

        
    def read_xy(self, center: bool = True, radians: bool = True):

        with xr.open_dataset(self.input_dir/self.gridfile) as ds:

            for obj in [self.x_obj, self.y_obj]:
                data = ds[obj.name].data
                if center:
                    data = data[::2, ::2]                
                if radians:
                    data = np.radians(data, dtype=np.float64)
                obj.data = np.ascontiguousarray(data)

            self._set_dims(ds.sizes, center=center)
                
        return self
        
                            
    def to_domain(self, domain: pyfms.Domain):

        isc, iec, jsc, jec = domain.isc, domain.iec, domain.jsc, domain.jec

        self.nx = domain.xsize_c
        self.ny = domain.ysize_c
        self.nxp = domain.xsize_c + 1
        self.nyp = domain.ysize_c + 1

        for obj in self.objlist:

            edge, shape = 2, (self.nyp, self.nxp)
            if obj is self.area_obj: edge, shape = 1, (self.ny, self.nx)

            if obj.data is not None and type(obj.data) is not str:
                obj.data = np.ascontiguousarray(obj.data[jsc:jec+edge, isc:iec+edge])                    
                if obj.data.shape != shape:
                    raise RuntimeError("grid on domain is not the correct size")

        return self

    
    def get_fms_area(self):

        self.area = pyfms.grid_utils.get_grid_area(lon=self.x.data, lat=self.y.data)
        return self.area

    
    def read(self, radians: bool = False, center: bool = False):

        """
        read:
        This function reads in the gridfile and initializes the instance variables
        """

        check_file_is_there(self.gridfile)

        with xr.open_dataset(self.input_dir/self.gridfile) as ds:        
            for obj in self.objlist:
                if obj.name in ds:
                    obj.data = ds[obj.name].data
                    if radians:
                        obj.data = np.radians(obj.data, dtype=np.float64)
                    if center:
                        obj.data = np.ascontiguousarray(obj.data[::2, ::2])
                else:
                    raise RuntimeError(f"could not {obj.name} in {self.gridfile}")
                    
            self._set_dims(ds.sizes, center=center)
            
        return self

    
    def write(self, gridfile: str = None):

        """
        write_out_grid:
        This method will generate a netcdf file containing grid content
        """

        if gridfile is None:
            if self.gridfile is None: pyfms.fms.error(FATAL, "must provide grid filename")
            gridfile = self.gridfile
            
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

        xr.Dataset(data_vars=ds).to_netcdf(gridfile)


    def _set_dims(self, dims: dict, center: bool = True):

        self.nxp = dims.get("nxp")
        self.nyp = dims.get("nyp")
        self.nx = dims.get("nx")
        self.ny = dims.get("ny")

        #nx
        if self.nxp is None:
            if self.nx is None:
                raise RuntimeError("cannot set dimensions")
            self.nxp = self.nx + 1
        elif self.nx is None:
            if self.nxp is None:
                raise RuntimeError("cannot set dimensions")
            self.nx = self.nxp - 1            

        #ny
        if self.nyp is None:
            if self.ny is None:
                raise RuntimeError("cannot set dimensions")
            self.nyp = self.ny + 1
        elif self.ny is None:
            if self.nyp is None:
                raise RuntimeError("cannot set dimensions")
            self.ny = self.nyp - 1            
                
        if center:
            self.nx = self.nx // 2
            self.ny = self.ny // 2
            self.nxp = self.nx + 1
            self.nyp = self.ny + 1


    @property 
    def x(self):
        return self.x_obj.data

    @x.setter
    def x(self, data):
        self.x_obj.data = data

    @property
    def y(self):
        return self.y_obj.data

    @y.setter
    def y(self, data):
        self.y_obj.data = data

    @property
    def tile(self):
        return self.tile_obj.data

    @tile.setter
    def tile(self, data):
        self.tile_obj.data = data

    @property
    def dx(self):
        return self.dx_obj.data 

    @dx.setter
    def dx(self, data):
        self.dx_obj.data = data

    @property
    def dy(self):
        return self.dy_obj.data

    @dy.setter
    def dy(self, data):
        self.dy_obj.data = data

    @property
    def area(self):
        return self.area_obj.data

    @area.setter
    def area(self, data):
        self.area_obj.data = data

    @property
    def angle_dx(self):
        return self.angle_dx_obj.data

    @angle_dx.setter
    def angle_dx(self, data):
        self.angle_dx_obj.data = data

    @property
    def angle_dy(self):
        return self.angle_dy_obj.data

    @angle_dy.setter
    def angle_dy(self, data):
        self.angle_dy_obj.data = data

    @property
    def arcx(self):
        return self.arcx_obj.data

    @arcx.setter
    def arcx(self, data):
        self.arcx_obj.data = data
    
    
    
        
        
    
        
        
