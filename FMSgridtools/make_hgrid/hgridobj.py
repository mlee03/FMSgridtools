import sys
import ctypes
import numpy as np
from numpy.typing import NDArray
import xarray as xr

from FMSgridtools.shared.gridtools_utils import get_provenance_attrs
from FMSgridtools.shared.gridobj import GridObj

def fill_cubic_grid_halo(
        nx: int, 
        ny: int, 
        halo: int, 
        data: NDArray[np.float64], 
        data1_all: NDArray[np.float64],
        data2_all: NDArray[np.float64],
        tile: int,
        ioff: int,
        joff: int,
):
    nxp = nx + ioff
    nyp = ny + joff
    nxph = nx + ioff + 2*halo
    nyph = ny + joff + 2*halo
        
    for i in range(nxph*nyph):
        data[i] = -9999.

    # first copy computing domain data
    for j in range (nyp+1):
        for i in range(nxp+1):
            data[j*nxph+i] = data1_all[tile*nxp*nyp+(j-1)*nxp+(i-1)]
                
    ntiles = 6
        
    if tile%2 == 1:
        lw = (tile+ntiles-1)%ntiles
        le = (tile+ntiles+2)%ntiles
        ls = (tile+ntiles-2)%ntiles
        ln = (tile+ntiles+1)%ntiles
        for j in range(nyp+1):
            data[j*nxph] = data1_all[lw*nxp*nyp+(j-1)*nxp+nx-1]       # west halo
            data[j*nxph+nxp+1] = data2_all[le*nxp*nyp+ioff*nxp+nyp-j] # east halo
        for i in range(nxp+1):
            data[i] = data2_all[ls*nxp*nyp+(nxp-i)*nyp+(nx-1)]        # south halo
            data[(nyp+1)*nxph+i] = data1_all[ln*nxp*nyp+joff*nxp+i-1] # north halo
    else:
        lw = (tile+ntiles-2)%ntiles
        le = (tile+ntiles+1)%ntiles
        ls = (tile+ntiles-1)%ntiles
        ln = (tile+ntiles+2)%ntiles
        for j in range(nyp+1):
            data[j*nxph] = data2_all[lw*nxp*nyp+(ny-1)*nxp+nyp-j]     # west halo
            data[j*nxph+nxp+1] = data1_all[le*nxp*nyp+(j-1)*nxp+ioff] # east halo
        for i in range(nxp+1):
            data[i] = data1_all[ls*nxp*nyp+(ny-1)*nxp+i-1]                # south halo
            data[(nyp+1)*nxph+i] = data2_all[ln*nxp*nyp+(nxp-i)*nyp+joff] # north halo

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
            nxbnds: int=None,
            nybnds: int=None,
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
            conformal: str="true",
            output_length_angle: bool=True,
            verbose: bool=False,
    ):
        """Get super grid size"""

        self.nxl = np.empty(shape=ntiles, dtype=np.int32)
        self.nyl = np.empty(shape=ntiles, dtype=np.int32)

        if grid_type == "GNOMONIC_ED" or grid_type == "CONFORMAL_CUBIC_GRID":
            """
            NOTE: The if-block in the loop below is changed with multiple nests.
            It appeared to allow refinement of the global grid
            without using any nests. However, the method used the
            nesting parameters "parent_tile" and "refine_ratio" to
            achieve this, which was enabled by setting parent_tile = 0 .
            This is no longer possible, as parent_tile is now an array.
            Instead, if the first value in the list of parent_tile values is 0,
            then the first value in the list of refine_ratio values will be
            applied to the global grid. This global-refinement application
            may not be valid for all permutations of nesting and refinement. [Ahern]
            """
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

        """Create grid information"""

        size1 = ctypes.c_ulong(0)
        size2 = ctypes.c_ulong(0)
        size3 = ctypes.c_ulong(0)
        size4 = ctypes.c_ulong(0)

        for n_nest in range(ntiles):
            print(f"[INFO] tile: {n_nest}, {self.nxl[n_nest]}, {self.nyl[n_nest]}, ntiles: {ntiles}\n")

        if grid_type == "FROM_FILE":
            size1 = 0
            size2 = 0
            size3 = 0
            size4 = 0
            for n in range(ntiles_global):
                size1.value += (nlon[n] + 1) * (nlat[n] + 1)
                size2.value += (nlon[n] + 1) * (nlat[n] + 1 + 1)
                size3.value += (nlon[n] + 1 + 1) * (nlat[n] + 1)
                size4.value += (nlon[n] + 1) * (nlat[n] + 1)
        else:
            size1 = ctypes.c_ulong(self.nxp * self.nyp * ntiles_global)
            size2 = ctypes.c_ulong(self.nx * self.nyp * ntiles_global)
            size3 = ctypes.c_ulong(self.nxp * self.ny * ntiles_global)
            size4 = ctypes.c_ulong(self.nx * self.ny * ntiles_global)

        if not (nest_grids == 1 and parent_tile[0] == 0):
            for n_nest  in range(ntiles_global, ntiles_global+nest_grids):
                if verbose:
                    print(f"[INFO] Adding memory size for nest {n_nest}, nest_grids: {nest_grids}\n", file=sys.stderr)
                size1.value += (self.nxl[n_nest]+1) * (self.nyl[n_nest]+1)
                size2.value += (self.nxl[n_nest]+1) * (self.nyl[n_nest]+2)
                size3.value += (self.nxl[n_nest]+2) * (self.nyl[n_nest]+1)
                size4.value += (self.nxl[n_nest]+1) * (self.nyl[n_nest]+1)

        if verbose:
            print(f"[INFO] Allocating arrays of size {size1.value} for x, y based on nxp: {self.nxp} nyp: {self.nyp} ntiles: {ntiles}\n", file=sys.stderr)
            print(f"size1 = {size1.value}, size2 = {size2.value}, size3 = {size3.value}, size4 = {size4.value}")
        self.x = np.empty(shape=size1.value, dtype=np.float64)
        self.y = np.empty(shape=size1.value, dtype=np.float64)
        self.area = np.empty(shape=size4.value, dtype=np.float64)
        self.arcx = arcx
        if output_length_angle:
            self.dx = np.empty(shape=size2.value, dtype=np.float64)
            self.dy = np.empty(shape=size3.value, dtype=np.float64)
            self.angle_dx = np.empty(shape=size1.value, dtype=np.float64)
            if conformal != "true":
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
            output_length_angle: bool=True,
            verbose: bool=False,
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

            if verbose:
                print(f"Writing out {outfile}\n", file=sys.stderr)

            tile = xr.DataArray(
                [self.tile],
                attrs=dict(
                    standard_name="grid_tile_spec",
                    geometry=geometry,
                    discretization=discretization,
                    conformal=conformal,
                )
            )
            if north_pole_tile is None:
                tile = tile.assign_attrs(projection=projection)
            if projection is "none":
                tile = tile.assign_attrs(north_pole_tile=north_pole_tile)
            var_dict['tile'] = tile

            if north_pole_arcx is None:
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
        
            """define dimension"""
            nx = self.nxl[n]
            ny = self.nyl[n]
            if verbose:
                print(f"[INFO] Outputting arrays of size nx: {nx} and ny: {ny} for tile: {n}")
            nxp = nx + 1
            nyp = ny + 1

            if out_halo == 0:
                if verbose:
                    print(f"[INFO] START NC XARRAY write out_halo = {out_halo} tile number = {n} offset = pos_c: {pos_c}", file=sys.stderr)
                    print(f"[INFO] XARRAY: n: {n} x[0]: {self.x[pos_c]} x[1]: {self.x[pos_c+1]} x[2]: {self.x[pos_c+2]} x[3]: {self.x[pos_c+3]} x[4]: {self.x[pos_c+4]} x[5]: {self.x[pos_c+5]} x[10]: {self.x[pos_c+10]}", file=sys.stderr)
                    if n > 0:
                        print(f"[INFO] XARRAY: n: {n} x[0]: {self.x[pos_c]} x[-1]: {self.x[pos_c-1]} x[-2]: {self.x[pos_c-2]} x[-3]: {self.x[pos_c-3]} x[-4]: {self.x[pos_c-4]} x[-5]: {self.x[pos_c-5]} x[-10]: {self.x[pos_c-10]}", file=sys.stderr)
                x = xr.DataArray(
                    data=self.x[pos_c:].reshape((nyp,nxp)),
                    dims=["nyp", "nxp"],
                    attrs=dict(
                        units="degree_east", 
                        standard_name="geographic_longitude",
                    )
                )
                var_dict['x'] = x

                y = xr.DataArray(
                    data=self.y[pos_c:].reshape((nyp, nxp)),
                    dims=["nyp", "nxp"],
                    attrs=dict(
                        units="degree_north", 
                        standard_name="geographic_latitude",
                    )
                )
                var_dict['y'] = y

                area = xr.DataArray(
                    data=self.area[pos_t:].reshape((ny, nx)),
                    dims=["ny", "nx"],
                    attrs=dict(
                        units="m2",
                        standard_name="grid_cell_area",
                    )
                )
                var_dict['area'] = area

                if output_length_angle:
                    dx = xr.DataArray(
                        data=self.dx[pos_n:].reshape((nyp, nx)),
                        dims=["nyp", "nx"],
                        attrs=dict(
                            units="meters", 
                            standard_name="grid_edge_x_distance",
                        )
                    )
                    var_dict['dx'] = dx

                    dy = xr.DataArray(
                        data=self.dy[pos_e:].reshape((ny, nxp)),
                        dims=["ny", "nxp"],
                        attrs=dict(
                            units="meters", 
                            standard_name="grid_edge_y_distance",
                        )
                    )
                    var_dict['dy'] = dy

                    angle_dx = xr.DataArray(
                        data=self.angle_dx[pos_c:].reshape((nyp, nxp)),
                        dims=["nyp", "nxp"],
                        attrs=dict(
                            units="degrees_east",
                            standard_name="grid_vertex_x_angle_WRT_geographic_east",
                        )
                    )
                    var_dict['angle_dx'] = angle_dx

                    if conformal != "true":
                        angle_dy = xr.DataArray(
                            data=self.angle_dy[pos_c:].reshape((nyp, nxp)),
                            dims=["nyp", "nxp"],
                            attrs=dict(
                                units="degrees_north",
                                standard_name="grid_vertex_y_angle_WRT_geographic_north",
                            )
                        )
                        var_dict['angle_dy'] = angle_dy
            else:
                tmp = np.empty(shape=(nxp+2*out_halo)*(nyp+2*out_halo), dtype=np.float64)

                if verbose:
                    print(f"[INFO] INDEX NC write with halo tile number = n: {n}", file=sys.stderr)

                fill_cubic_grid_halo(nx, ny, out_halo, tmp, self.x, self.x, n, 1, 1)
                self.x = tmp.copy()
                x = xr.DataArray(
                    data=self.x.reshape((nyp,nxp)),
                    dims=["nyp", "nxp"],
                    attrs=dict(
                        units="degree_east", 
                        standard_name="geographic_longitude",
                        _FillValue=-9999.,
                    )
                )
                var_dict['x'] = x

                fill_cubic_grid_halo(nx, ny, out_halo, tmp, self.y, self.y, n, 1, 1)
                self.y = tmp.copy()
                y = xr.DataArray(
                    data=self.y.reshape((nyp, nxp)),
                    dims=["nyp", "nxp"],
                    attrs=dict(
                        units="degree_north", 
                        standard_name="geographic_latitude",
                        _FillValue = -9999.,
                    )
                )
                var_dict['y'] = y

                fill_cubic_grid_halo(nx, ny, out_halo, tmp, self.area, self.area, n, 0, 0)
                self.area = tmp.copy()
                area = xr.DataArray(
                    data=self.area.reshape((ny, nx)),
                    dims=["ny", "nx"],
                    attrs=dict(
                        units="m2",
                        standard_name="grid_cell_area",
                        _FillValue=-9999.,
                    )
                )
                var_dict['area'] = area

                if output_length_angle:
                    fill_cubic_grid_halo(nx, ny, out_halo, tmp, self.dx, self.dy, n, 0, 1)
                    self.dx = tmp.copy()
                    dx = xr.DataArray(
                        data=self.dx.reshape((nyp, nx)),
                        dims=["nyp", "nx"],
                        attrs=dict(
                            units="meters", 
                            standard_name="grid_edge_x_distance",
                            _FillValue=-9999.,
                        )
                    )
                    var_dict['dx'] = dx

                    fill_cubic_grid_halo(nx, ny, out_halo, tmp, self.dy, self.dx, n, 1, 0)
                    self.dy = tmp.copy()
                    dy = xr.DataArray(
                        data=self.dy.reshape((ny, nxp)),
                        dims=["ny", "nxp"],
                        attrs=dict(
                            units="meters", 
                            standard_name="grid_edge_y_distance",
                            _FillValue=-9999.,
                        )
                    )
                    var_dict['dy'] = dy

                    fill_cubic_grid_halo(nx, ny, out_halo, tmp, self.angle_dx, self.angle_dx, n, 1, 1)
                    self.angle_dx = tmp.copy()
                    angle_dx = xr.DataArray(
                        data=self.angle_dx.reshape((nyp, nxp)),
                        dims=["nyp", "nxp"],
                        attrs=dict(
                            units="degrees_east",
                            standard_name="grid_vertex_x_angle_WRT_geographic_east",
                            _FillValue=-9999.,
                        )
                    )
                    var_dict['angle_dx'] = angle_dx

                    if conformal != "true":
                        fill_cubic_grid_halo(nx, ny, out_halo, tmp, self.angle_dy, self.angle_dy, n, 1, 1)
                        self.angle_dy = tmp.copy()
                        angle_dy = xr.DataArray(
                            data=self.angle_dy.reshape((nyp, nxp)),
                            dims=["nyp", "nxp"],
                            attrs=dict(
                                units="degrees_north",
                                standard_name="grid_vertex_y_angle_WRT_geographic_north",
                                _FillValue=-9999.,
                            )
                        )
                        var_dict['angle_dy'] = angle_dy

            nx = self.nxl[n]
            ny = self.nyl[n]
            nxp = nx + 1
            nyp = ny + 1

            if verbose:
                print(f"[INFO] INDEX Before increment n: {n} pos_c {pos_c} nxp {nxp} nyp {nyp} nxp*nyp {nxp*nyp}\n", file=sys.stderr)
            pos_c += nxp*nyp
            if verbose:
                print(f"[INFO] INDEX After increment n: {n} pos_c {pos_c}\n", file=sys.stderr)
            pos_e += nxp*ny
            pos_n += nx*nyp
            pos_t += nx*ny

            if verbose:
                print(f"About to close {outfile}")

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


