import ctypes
import numpy as np
from numpy.typing import NDArray
import xarray as xr

from FMSgridtools.shared.gridtools_utils import check_file_is_there, get_provenance_attrs
from FMSgridtools.shared.gridobj import GridObj
import pyfrenctools

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
        self.nx = None
        self.ny = None
        self.nxp = None
        self.nyp = None
        self.nxl = None
        self.nyl = None
        self.isc = None
        self.iec = None
        self.jsc = None
        self.jec = None

    def make_grid_info(
            self,
            nxbnds: int,
            nybnds: int,
            ntiles: int=1,
            ntiles_global: int=1,
            nlon: NDArray=None,
            nlat: NDArray=None,
            nest_grids: int=0,
            parent_tile: NDArray=None,
            refine_ratio: NDArray=None,
            istart_nest: NDArray=None,
            iend_nest: NDArray=None,
            jstart_nest: NDArray=None,
            jend_nest: NDArray=None,
            arcx: str="small_circle",
            grid_type: str=None,
    ):
        self.nxl = np.empty(shape=ntiles, dtype=np.int32)
        self.nyl = np.empty(shape=ntiles, dtype=np.int32)

        if grid_type == "GNOMONIC_ED" or grid_type == "CONFORMAL_CUBIC_GRID":
            for n in range(ntiles_global):
                self.nxl[n] = nlon[0]
                self.nyl[n] = self.nxl[n]
                if nest_grids and parent_tile[0] == 0:
                    self.nxl[n] *= refine_ratio[0]
                    self.nyl[n] *= refine_ratio[0]

            for n in range(ntiles_global, ntiles):
                nn = n - ntiles_global
                self.nxl[n] = (iend_nest[nn] - istart_nest[nn] + 1) * refine_ratio[nn]
                self.nyl[n] = (jend_nest[nn] - jstart_nest[nn] + 1) * refine_ratio[nn]
        elif grid_type == "FROM_FILE":
            for n in range(ntiles_global):
                self.nxl[n] = nlon[n]
                self.nyl[n] = nlat[n]
        else:
            self.nxl[0] = 0
            self.nyl[0] = 0
            for n in range(nxbnds - 1):
                self.nxl[0] += nlon[n]
            for n in range(nybnds - 1):
                self.nyl[0] += nlat[n]

        self.nx = self.nxl[0]
        self.ny = self.nyl[0]
        self.nxp = self.nx + 1
        self.nyp = self.ny + 1

        size1 = ctypes.c_ulong(0)
        size2 = ctypes.c_ulong(0)
        size3 = ctypes.c_ulong(0)
        size4 = ctypes.c_ulong(0)

        if grid_type == "FROM_FILE":
            for n in range(ntiles_global):
                size1.value += (nlon[n] + 1) * (nlat[n] + 1)
                size2.value += (nlon[n] + 1) * (nlat[n] + 1 + 1)
                size3.value += (nlon[n] + 1 +1) * (nlat[n] + 1)
                size4.value += (nlon[n] + 1) * (nlat[n] + 1)
        else:
            size1 = ctypes.c_ulong(self.nxp * self.nyp * ntiles_global)
            size2 = ctypes.c_ulong(self.nxp * (self.nyp + 1) * ntiles_global)
            size3 = ctypes.c_ulong((self.nxp + 1) * self.nyp * ntiles_global)
            size4 = ctypes.c_ulong(self.nxp * self.nyp * ntiles_global)

        if not (nest_grids == 1 and parent_tile[0] == 0):
            for n_nest  in range(ntiles_global, ntiles_global+nest_grids):
                size1.value += (self.nxl[n_nest]+1) * (self.nyl[n_nest]+1)
                size2.value += (self.nxl[n_nest]+1) * (self.nyl[n_nest]+2)
                size3.value += (self.nxl[n_nest]+2) * (self.nyl[n_nest]+1)
                size4.value += (self.nxl[n_nest]+1) * (self.nyl[n_nest]+1)

        self.x = np.empty(shape=size1.value, dtype=np.float64)
        self.y = np.empty(shape=size1.value, dtype=np.float64)
        self.area = np.empty(shape=size4.value, dtype=np.float64)
        self.arcx = arcx
        self.dx = np.empty(shape=size2.value, dtype=np.float64)
        self.dy = np.empty(shape=size3.value, dtype=np.float64)
        self.angle_dx = np.empty(shape=size1.value, dtype=np.float64)
        self.angle_dy = np.empty(shape=size1.value, dtype=np.float64)
        self.isc = 0
        self.iec = self.nx - 1
        self.jsc = 0
        self.jec = self.ny - 1


    def write_out_hgrid(
            self,
            grid_name: str="horizontal_grid",
            ntiles: int=1,
            north_pole_tile: str="0.0 90.0",
            north_pole_arcx: str="0.0 90.0",
            projection: str="none",
            geometry: str="spherical",
            discretization: str="logically_rectangular",
            conformal: str="true",
            out_halo: int=0,
            output_length_angle: int=0,
    ):
        
        var_dict={}
        pos_c = 0
        pos_e = 0
        pos_t = 0
        pos_n = 0
        for n in range(ntiles):
            self.tile = "tile" + str(n+1)
            if ntiles > 1:
                outfile = grid_name + ".tile" + ".nc" + str(n+1)
            else:
                outfile = grid_name + ".nc"
        
            nx = self.nxl[n]
            ny = self.nyl[n]
            nxp = nx + 1
            nyp = ny + 1

            if out_halo == 0:
                self.x = self.x[pos_c:]
                self.y = self.y[pos_c:]
                self.dx = self.dx[pos_n:]
                self.dy = self.dy[pos_e:]
                self.angle_dx = self.angle_dx[pos_c:]
                self.angle_dy = self.angle_dy[pos_c:]
                self.area = self.area[pos_t:]
            else:
                tmp = np.empty(shape=(nxp+2*out_halo)*(nyp+2*out_halo), dtype=np.float64)
                pyfrenctools.make_hgrid_wrappers.fill_cubic_grid_halo(nx, ny, out_halo, tmp, self.x, self.x, n, 1, 1)
                self.x = tmp.copy()
                pyfrenctools.make_hgrid_wrappers.fill_cubic_grid_halo(nx, ny, out_halo, tmp, self.y, self.y, n, 1, 1)
                self.y = tmp.copy()
                pyfrenctools.make_hgrid_wrappers.fill_cubic_grid_halo(nx, ny, out_halo, tmp, self.angle_dx, self.angle_dx, n, 1, 1)
                self.angle_dx = tmp.copy()
                pyfrenctools.make_hgrid_wrappers.fill_cubic_grid_halo(nx, ny, out_halo, tmp, self.angle_dy, self.angle_dy, n, 1, 1)
                self.angle_dy = tmp.copy()
                pyfrenctools.make_hgrid_wrappers.fill_cubic_grid_halo(nx, ny, out_halo, tmp, self.dx, self.dy, n, 0, 1)
                self.dx = tmp.copy()
                pyfrenctools.make_hgrid_wrappers.fill_cubic_grid_halo(nx, ny, out_halo, tmp, self.dy, self.dx, n, 1, 0)
                self.dy = tmp.copy()
                pyfrenctools.make_hgrid_wrappers.fill_cubic_grid_halo(nx, ny, out_halo, tmp, self.area, self.area, n, 0, 0)
                self.area = tmp.copy()

            nx = self.nxl[n]
            ny = self.nyl[n]
            nxp = nx + 1
            nyp = ny + 1
            pos_c += nxp*nyp
            pos_e += nxp*ny
            pos_n += nx*nyp
            pos_t += nx*ny

        tile = xr.DataArray(
            [self.tile],
            attrs=dict(
                standard_name="grid_tile_spec",
                geometry=geometry,
                discretization=discretization,
                conformal=conformal,
            )
        )
        if north_pole_tile is "none":
            tile = tile.assign_attrs(projection=projection)
        if projection is "none":
            tile = tile.assign_attrs(north_pole_tile=north_pole_tile)
        var_dict['tile'] = tile

        if self.x is not None:
            x = xr.DataArray(
                data=self.x[:(nyp*nxp)].reshape((nyp,nxp)),
                dims=["nyp", "nxp"],
                attrs=dict(
                    units="degree_east", 
                    standard_name="geographic_longitude",
                )
            )

            if out_halo > 0:
                x.attrs["_FillValue"] = -9999.

            var_dict['x'] = x
            
        if self.y is not None:
            y = xr.DataArray(
                data=self.y[:(nyp*nxp)].reshape((nyp, nxp)),
                dims=["nyp", "nxp"],
                attrs=dict(
                    units="degree_north", 
                    standard_name="geographic_latitude",
                )
            )

            if out_halo > 0:
                y.attrs["_FillValue"] = -9999.

            var_dict['y'] = y
    
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

                if out_halo > 0:
                    dx.attrs["_FillValue"] = -9999.

                var_dict['dx'] = dx

            if self.dy is not None:    
                dy = xr.DataArray(
                    data=self.dy[:(ny*nxp)].reshape((ny, nxp)),
                    dims=["ny", "nxp"],
                    attrs=dict(
                        units="meters", 
                        standard_name="grid_edge_y_distance",
                    )
                )

                if out_halo > 0:
                    dy.attrs["_FillValue"] = -9999.

                var_dict['dy'] = dy

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
                    angle_dx.attrs["_FillValue"] = -9999.

                var_dict['angle_dx'] = angle_dx
                    
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
                        angle_dy.attrs["_FillValue"] = -9999.

                    var_dict['angle_dy'] = angle_dy

        if self.area is not None:
            area = xr.DataArray(
                data=self.area[:(ny*nx)].reshape((ny, nx)),
                dims=["ny", "nx"],
                attrs=dict(
                    units="m2",
                    standard_name="grid_cell_area",
                )
            )

            if out_halo > 0:
                area.attrs["_FillValue"] = -9999.

            var_dict['area'] = area

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

        var_dict['arcx'] = arcx

        prov_attrs = get_provenance_attrs(great_circle_algorithm=True)   

        dataset = xr.Dataset(
            data_vars=var_dict
        )
        dataset.attrs = prov_attrs
        self.dataset = dataset
        dataset.to_netcdf(outfile)

    def make_gridobj(self) -> "GridObj":
        var_dict = {}
        if self.dataset is None:
            tile = xr.DataArray(
                [self.tile]
            )
            var_dict['tile'] = tile
            if self.x is not None:
                x = xr.DataArray(
                    data=self.x,
                    dims=["nyp", "nxp"],
                )
                var_dict['x'] = x
            if self.y is not None:
                y = xr.DataArray(
                    data=self.y,
                    dims=["nyp", "nxp"],
                )
                var_dict['y'] = y
            if self.dx is not None:
                dx = xr.DataArray(
                    data=self.dx,
                    dims=["nyp", "nx"],
                )
                var_dict['dx'] = dx
            if self.dy is not None:
                dy = xr.DataArray(
                    data=self.dy,
                    dims=["ny", "nxp"],
                )
                var_dict['dy'] = dy
            if self.angle_dx is not None:
                angle_dx = xr.DataArray(
                    data=self.angle_dx,
                    dims=["nyp", "nxp"],
                )
                var_dict['angle_dx'] = angle_dx
            if self.angle_dy is not None:
                angle_dy = xr.DataArray(
                    data=self.angle_dy,
                    dims=["nyp", "nxp"],
                )
                var_dict['angle_dy'] = angle_dy
            if self.area is not None:
                area = xr.DataArray(
                    data=self.area,
                    dims=["ny", "nx"],
                )
                var_dict['area'] = area
            if self.arcx is not None:
                arcx = xr.DataArray(
                    [self.arcx],
                )
                var_dict['arcx'] = arcx
            dataset = xr.Dataset(
                data_vars = var_dict
            )
        else:
            dataset=self.dataset
        return GridObj(dataset=dataset)


