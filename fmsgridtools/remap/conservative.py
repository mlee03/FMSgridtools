from mpi4py import MPI
import numpy as np
import xarray as xr

from fmsgridtools.remap.dataobj import DataObj
from fmsgridtools.shared.xgridobj import XGridObj
from fmsgridtools.shared.mosaicobj import MosaicObj

import pyfms


def remap(xgrid: type[XGridObj] = None,
          input_file: str = None,
          src_mosaic: str = None,
          tgt_mosaic: str = None,
          scalar_variables: list[str] = None,
          input_dir: str = "./",
          output_dir: str = "./",
          output_file: str = None,
          lon_bounds: list = None,
          lat_bounds: list = None,
          kbounds: list = None,
          tbounds: list = None,
          order: int = 1,
          static_file: str = None,
          check_conserve: bool = False) -> XGridObj:

  mydir = "/home/Mikyung.Lee/FRE-NCTools/test-benchmark/tests_fregrid/Testa-conserve1-output/"
  data_dir = "/home/Mikyung.Lee/FRE-NCTools/DONOTDELETEME_DATA/TESTS/TESTS_INPUT/Testa-input/"
  src_mosaic = "C96_mosaic.nc"
  tgt_mosaic = "lonlat_288x180_mosaic.nc"
  src_data = "00010101.atmos_month_aer"

  #get input grid
  src_mosaic = MosaicObj(input_dir=mydir, mosaic_file=src_mosaic).read()
  src_grid_dict = src_mosaic.get_grid(toradians=True, agrid=True)

  #get target grid
  tgt_mosaic = MosaicObj(input_dir=mydir, mosaic_file=tgt_mosaic).read()
  tgt_grid_dict = tgt_mosaic.get_grid(toradians=True, agrid=True)

  #initialize fms
  comm = MPI.COMM_WORLD
  pyfms.fms.init(ndomain=len(tgt_grid_dict), localcomm=comm.py2f())
  pyfms.horiz_interp.init(ninterp=6)

  #domain
  nx, ny = tgt_grid_dict['tile1'].nx, tgt_grid_dict['tile1'].ny
  global_indices = [0, nx, 0, ny]
  layout = pyfms.mpp_domains.define_layout(global_indices, ndivs=pyfms.mpp.npes())
  domain = pyfms.mpp_domains.define_domains(global_indices=global_indices, layout=layout)

  indices = comm.gather([domain.isc, domain.iec, domain.jsc, domain.jec], root=0)

  for tgt_tile in tgt_grid_dict:

    #get tgt grid on domain
    isc, iec, jsc, jec = domain.isc, domain.iec, domain.jsc, domain.jec
    tgt_x = np.ascontiguousarray(tgt_grid_dict[tgt_tile].x[jsc:jec+1, isc:iec+1], dtype=np.float64)
    tgt_y = np.ascontiguousarray(tgt_grid_dict[tgt_tile].y[jsc:jec+1, isc:iec+1], dtype=np.float64)

    interp_ids, src_tiles = {}, []
    for src_tile, src_grid in src_grid_dict.items():

      src_tiles.append(src_tile)

      area = src_grid.get_fms_area()

      interp_ids[src_tile] = pyfms.horiz_interp.get_weights(lon_in=src_grid.x,
                                                 lat_in=src_grid.y,
                                                 lon_out=tgt_x,
                                                 lat_out=tgt_y,
                                                 nlon_in=src_grid.nx,
                                                 nlat_in=src_grid.ny,
                                                 nlon_out=(iec-isc),
                                                 nlat_out=(jec-jsc),
                                                 convert_cf_order=False
      )

    # get list of all variables to regrid
    no_regrid = ["land_mask", "average_T1", "average_T2", "average_DT", "time_bnds", "bk", "pk", "land_mask"]
    if len(src_tiles) > 0: datafile_tile1 = src_data + ".tile1"
    if scalar_variables is None:
      with xr.open_dataset(data_dir+"/"+datafile_tile1+".nc", decode_cf=False) as dataset:
        scalar_variables = [key for key in dataset.data_vars if key not in no_regrid]

    fields = {}
    for variable in scalar_variables:

      field = DataObj(input_dir=data_dir, tiles=src_tiles, datafile=src_data, variable=variable)

      times = list(range(field.dims.ntime)) if field.dims.has_t else [None]
      klevels = list(range(field.dims.nz)) if field.dims.has_z  else [None]

      for itime in times:
        for k in klevels:
          itile = 0
          for tile in field.tiles:

            field_in = field.get_slice(tile=tile, klevel=k, timepoint=itime)
            if field.area_averaged: field_in *= field.static_area / area

            if itile == 0:
              tgt_data = pyfms.horiz_interp.interp(interp_id=interp_ids[tile],
                                                   data_in=field_in,
                                                   convert_cf_order=False)
            else:
              tgt_data += pyfms.horiz_interp.interp(interp_id=interp_ids[tile],
                                                    data_in=field_in,
                                                    convert_cf_order=False)

          field.save(data=tgt_data, klevel=k, timepoint=itime)

      gathered_data = comm.gather(field.tgt_field.values, root=0)

      if pyfms.mpp.pe() == 0:

        if field.dims.has_z and field.dims.has_t:
          dims = [field.dims.time, field.dims.z, field.dims.y, field.dims.x]
          global_array = np.zeros((field.dims.ntime, field.dims.nz, ny, nx))
          for i in range(4):
            isc, iec, jsc, jec = indices[i]
            global_array[:,:, jsc:jec, isc:iec] += gathered_data[i]
        elif field.dims.has_z:
          dims = [field.dims.z, field.dims.y, field.dims.x]
          global_array = np.zeros((field.dims.nz, ny, nx))
          for i in range(4):
            isc, iec, jsc, jec = indices[i]
            global_array[:, jsc:jec, isc:iec] += gathered_data[i]
        elif field.dims.has_t:
          dims = [field.dims.time, field.dims.y, field.dims.x]
          global_array = np.zeros((field.dims.ntime, ny, nx))
          for i in range(4):
            isc, iec, jsc, jec = indices[i]
            global_array[:, jsc:jec, isc:iec] += gathered_data[i]
        else:
          dims = [field.dims.y, field.dims.x]
          global_array = np.zeros((ny, nx))
          for i in range(4):
            isc, iec, jsc, jec = indices[i]
            global_array[jsc:jec, isc:iec] += gathered_data[i]

        field.tgt_field = xr.DataArray(global_array, dims=dims)
        fields[variable] = field.complete_tgt_field()
        print(variable)
    if pyfms.mpp.pe() == 0:
      xr.Dataset(data_vars=fields).to_netcdf("test.nc")


if __name__ == "__main__":
  remap()



