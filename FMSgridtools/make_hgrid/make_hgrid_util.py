# import numpy as np
# from numpy.typing import NDArray
# import ctypes

# from FMSgridtools.make_hgrid.hgridobj import HGridObj
# from FMSgridtools.shared.gridtools_utils import get_provenance_attrs
# import pyfrenctools

# def make_grid_info(
#         grid_obj: HGridObj,
#         nxbnds: int,
#         nybnds: int,
#         ntiles: int = 1,
#         ntiles_global: int = 1,
#         nlon: NDArray = None,
#         nlat: NDArray = None,
#         nest_grids: int = 0,
#         parent_tile: NDArray = None,
#         refine_ratio: NDArray = None,
#         istart_nest: NDArray = None,
#         iend_nest: NDArray = None,
#         jstart_nest: NDArray = None,
#         jend_nest: NDArray = None,
#         arcx: str = "small_circle",
#         grid_type: str = None,
# ) -> dict:
    
#     nxl = np.empty(shape=ntiles, dtype=np.int32)
#     nyl = np.empty(shape=ntiles, dtype=np.int32)

#     if grid_type == "GNOMONIC_ED" or grid_type == "CONFORMAL_CUBIC_GRID":
#         for n in range(ntiles_global):
#             nxl[n] = nlon[0]
#             nyl[n] = nxl[n]
#             if nest_grids and parent_tile[0] == 0:
#                 nxl[n] *= refine_ratio[0]
#                 nyl[n] *= refine_ratio[0]

#         for n in range(ntiles_global, ntiles):
#             nn = n - ntiles_global
#             nxl[n] = (iend_nest[nn] - istart_nest[nn] + 1) * refine_ratio[nn]
#             nyl[n] = (jend_nest[nn] - jstart_nest[nn] + 1) * refine_ratio[nn]
#     elif grid_type == "FROM_FILE":
#         for n in range(ntiles_global):
#             nxl[n] = nlon[n]
#             nyl[n] = nlat[n]
#     else:
#         nxl[0] = 0
#         nyl[0] = 0
#         for n in range(nxbnds - 1):
#             nxl[0] += nlon[n]
#         for n in range(nybnds - 1):
#             nyl[0] += nlat[n]

#     nx = nxl[0]
#     ny = nyl[0]
#     nxp = nx + 1
#     nyp = ny + 1
#     grid_info_dict = {}
#     grid_info_dict['nx'] = nx
#     grid_info_dict['ny'] = ny
#     grid_info_dict['nxp'] = nxp
#     grid_info_dict['nyp'] = nyp
#     grid_info_dict['nxl'] = nxl
#     grid_info_dict['nyl'] = nyl

#     size1 = ctypes.c_ulong(0)
#     size2 = ctypes.c_ulong(0)
#     size3 = ctypes.c_ulong(0)
#     size4 = ctypes.c_ulong(0)

#     if grid_type == "FROM_FILE":
#         for n in range(ntiles_global):
#             size1.value += (nlon[n] + 1) * (nlat[n] + 1)
#             size2.value += (nlon[n] + 1) * (nlat[n] + 1 + 1)
#             size3.value += (nlon[n] + 1 +1) * (nlat[n] + 1)
#             size4.value += (nlon[n] + 1) * (nlat[n] + 1)
#     else:
#         size1 = ctypes.c_ulong(nxp * nyp * ntiles_global)
#         size2 = ctypes.c_ulong(nxp * (nyp + 1) * ntiles_global)
#         size3 = ctypes.c_ulong((nxp + 1) * nyp * ntiles_global)
#         size4 = ctypes.c_ulong(nxp * nyp * ntiles_global)

#     if not (nest_grids == 1 and parent_tile[0] == 0):
#         for n_nest  in range(ntiles_global, ntiles_global+nest_grids):
#             size1.value += (nxl[n_nest]+1) * (nyl[n_nest]+1)
#             size2.value += (nxl[n_nest]+1) * (nyl[n_nest]+2)
#             size3.value += (nxl[n_nest]+2) * (nyl[n_nest]+1)
#             size4.value += (nxl[n_nest]+1) * (nyl[n_nest]+1)

#     grid_obj.x = np.empty(shape=size1.value, dtype=np.float64)
#     grid_obj.y = np.empty(shape=size1.value, dtype=np.float64)
#     grid_obj.area = np.empty(shape=size4.value, dtype=np.float64)
#     grid_obj.arcx = arcx
#     grid_obj.dx = np.empty(shape=size2.value, dtype=np.float64)
#     grid_obj.dy = np.empty(shape=size3.value, dtype=np.float64)
#     grid_obj.angle_dx = np.empty(shape=size1.value, dtype=np.float64)
#     grid_obj.angle_dy = np.empty(shape=size1.value, dtype=np.float64)

#     isc = 0
#     iec = nx - 1
#     jsc = 0
#     jec = ny - 1

#     grid_info_dict['isc'] = 0
#     grid_info_dict['iec'] = nx - 1
#     grid_info_dict['jsc'] = 0
#     grid_info_dict['jec'] = ny - 1


#     return grid_info_dict

# def grid_writer(
#         grid_obj: HGridObj,
#         info_dict: dict,
#         grid_name: str = "horizontal_grid",
#         ntiles: int = 1,
#         out_halo: int = 0,
# ):
#     north_pole_tile = "0.0 90.0"
#     north_pole_arcx = "0.0 90.0"
#     geometry = "spherical"
#     projection = "none"
#     conformal = "true"
#     discretization = "logically_rectangular"
#     output_length_angle = 1
#     pos_c = 0
#     pos_e = 0
#     pos_t = 0
#     pos_n = 0
#     for n in range(ntiles):
#         grid_obj.tile = "tile" + str(n+1)
#         if ntiles > 1:
#             outfile = grid_name + ".tile" + ".nc" + str(n+1)
#         else:
#             outfile = grid_name + ".nc"
        
#         nx = info_dict['nxl'][n]
#         ny = info_dict['nyl'][n]
#         nxp = nx + 1
#         nyp = ny + 1

#         if out_halo == 0:
#             grid_obj.x = grid_obj.x[pos_c:]
#             grid_obj.y = grid_obj.y[pos_c:]
#             grid_obj.dx = grid_obj.dx[pos_n:]
#             grid_obj.dy = grid_obj.dy[pos_e:]
#             grid_obj.angle_dx = grid_obj.angle_dx[pos_c:]
#             grid_obj.angle_dy = grid_obj.angle_dy[pos_c:]
#             grid_obj.area = grid_obj.area[pos_t:]
#         else:
#             tmp = np.empty(shape=(nxp+2*out_halo)*(nyp+2*out_halo), dtype=np.float64)
#             pyfrenctools.make_hgrid_wrappers.fill_cubic_grid_halo(nx, ny, out_halo, tmp, grid_obj.x, grid_obj.x, n, 1, 1)
#             grid_obj.x = tmp.copy()
#             pyfrenctools.make_hgrid_wrappers.fill_cubic_grid_halo(nx, ny, out_halo, tmp, grid_obj.y, grid_obj.y, n, 1, 1)
#             grid_obj.y = tmp.copy()
#             pyfrenctools.make_hgrid_wrappers.fill_cubic_grid_halo(nx, ny, out_halo, tmp, grid_obj.angle_dx, grid_obj.angle_dx, n, 1, 1)
#             grid_obj.angle_dx = tmp.copy()
#             pyfrenctools.make_hgrid_wrappers.fill_cubic_grid_halo(nx, ny, out_halo, tmp, grid_obj.angle_dy, grid_obj.angle_dy, n, 1, 1)
#             grid_obj.angle_dy = tmp.copy()
#             pyfrenctools.make_hgrid_wrappers.fill_cubic_grid_halo(nx, ny, out_halo, tmp, grid_obj.dx, grid_obj.dy, n, 0, 1)
#             grid_obj.dx = tmp.copy()
#             pyfrenctools.make_hgrid_wrappers.fill_cubic_grid_halo(nx, ny, out_halo, tmp, grid_obj.dy, grid_obj.dx, n, 1, 0)
#             grid_obj.dy = tmp.copy()
#             pyfrenctools.make_hgrid_wrappers.fill_cubic_grid_halo(nx, ny, out_halo, tmp, grid_obj.area, grid_obj.area, n, 0, 0)
#             grid_obj.area = tmp.copy()

#         nx = info_dict['nxl'][n]
#         ny = info_dict['nyl'][n]
#         nxp = nx + 1
#         nyp = ny + 1
#         pos_c += nxp*nyp
#         pos_e += nxp*ny
#         pos_n += nx*nyp
#         pos_t += nx*ny

#     prov_attrs = get_provenance_attrs(great_circle_algorithm=True)
#     grid_obj.write_out_hgrid(
#         outfile=outfile,
#         nx=nx,
#         ny=ny,
#         nxp=nxp,
#         nyp=nyp,
#         global_attrs=prov_attrs,
#         north_pole_tile=north_pole_tile,
#         north_pole_arcx=north_pole_arcx,
#         projection=projection,
#         geometry=geometry,
#         discretization=discretization,
#         conformal=conformal,
#         out_halo=out_halo,
#         output_length_angle=output_length_angle,
#     )

