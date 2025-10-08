from mpi4py import MPI
import numpy as np
from pathlib import Path
import xarray as xr

from fmsgridtools.remap.dataobj import DataObj
from fmsgridtools.shared.xgridobj import XGridObj
from fmsgridtools.shared.mosaicobj import MosaicObj

import pyfms


def call_horiz_interp(interp_ids: dict, field: DataObj, k: int = None, itime: int = None):

    for tile in interp_ids:

        field_in = field.get_slice(tile=tile, klevel=k, timepoint=itime)
        if field.area_averaged:
            field_in *= field.static_area / area

        if itile == 0:
            remapped_data = pyfms.horiz_interp.interp(interp_id=interp_ids[tile],
                                                      data_in=field_in,
                                                      convert_cf_order=False)
        else:
            remapped_data += pyfms.horiz_interp.interp(interp_id=interp_ids[tile],
                                                       data_in=field_in,
                                                       convert_cf_order=False)
        itile += 1

    return remapped_data


def remap(input_dir: str = "./",
          output_dir: str = "./",
          input_mosaic_dir: str = "./",
          output_mosaic_dir: str = "./",
          input_file: str = None,
          src_mosaic: str = None,
          tgt_mosaic: str = None,
          output_file: str = None,
          scalar_variables: list[str] = None,
          lon_bounds: list = None,
          lat_bounds: list = None,
          kbounds: list = None,
          tbounds: list = None,
          order: int = 1,
          check_conserve: bool = False) -> XGridObj:

    # get input grid
    src_mosaic = MosaicObj(input_dir=input_mosaic_dir,
                           mosaic_file=src_mosaic).read()
    src_grid_dict = src_mosaic.get_grid(toradians=True, agrid=True)

    # get target grid
    tgt_mosaic = MosaicObj(input_dir=output_mosaic_dir,
                           mosaic_file=tgt_mosaic).read()
    tgt_grid_dict = tgt_mosaic.get_grid(toradians=True, agrid=True)

    # initialize fms
    pyfms.fms.init(ndomain=len(tgt_grid_dict))
    pyfms.horiz_interp.init(ninterp=len(src_grid_dict))

    # identify root pe
    is_root_pe = pyfms.mpp.pe() == pyfms.mpp.root_pe()

    # domain
    global_indices = [0, tgt_grid_dict['tile1'].nx,
                      0, tgt_grid_dict['tile1'].ny]
    layout = pyfms.mpp_domains.define_layout(
        global_indices, ndivs=pyfms.mpp.npes())
    domain = pyfms.mpp_domains.define_domains(
        global_indices=global_indices, layout=layout)

    # get tgt grid on domain
    for tile in tgt_grid_dict:
        tgt_grid_dict[tile].to_domain(domain)

    for tgt_tile in tgt_grid_dict:
        interp_ids = {}
        tgt_grid = tgt_grid_dict[tgt_tile]
        for src_tile in src_tiles:

            src_grid = src_grid_dict[src_tile]
            area = src_grid.get_fms_area()

            interp_ids[src_tile] = pyfms.horiz_interp.get_weights(lon_in=src_grid.x,
                                                                  lat_in=src_grid.y,
                                                                  lon_out=tgt_grid.x,
                                                                  lat_out=tgt_grid.y,
                                                                  nlon_in=src_grid.nx,
                                                                  nlat_in=src_grid.ny,
                                                                  nlon_out=tgt_grid.nx,
                                                                  nlat_out=tgt_grid.ny,
                                                                  convert_cf_order=False
                                                                  )

        # get list of all variables to regrid
        no_regrid = ["land_mask", "average_T1", "average_T2",
                     "average_DT", "time_bnds", "bk", "pk", "land_mask"]
        if len(src_tiles) > 0:
            input_file_tile1 = input_file + ".tile1"
        if scalar_variables is None:
            with xr.open_dataset(input_dir+"/"+input_file_tile1+".nc", decode_cf=False) as dataset:
                scalar_variables = [
                    key for key in dataset.data_vars if key not in no_regrid]

        fields = {}
        for variable in scalar_variables:

            field = DataObj(input_dir=input_dir, tiles=src_tiles,
                            datafile=input_file, variable=variable)

            times = list(range(field.dims.ntime)
                         ) if field.dims.has_t else [None]
            klevels = list(range(field.dims.nz)
                           ) if field.dims.has_z else [None]

            new_t_start, new_z_start = field.dims.has_t_and_z, False

            for itime in times:
                new_t, new_z = new_t_start, new_z_start  # only matters if t and z exists
                for k in klevels:
                    remapped_data = call_horiz_interp(
                        interp_ids, field, k=k, itime=itime)
                    gathered = pyfms.mpp.gather(domain, remapped_data)
                    if is_root_pe:
                        field.tgt.save(gathered, new_t=new_t, new_z=new_z)
                    new_t, new_z = False, True  # only matters if t and z exists

            fields[variable] = field.tgt.complete()

        if is_root_pe:
            if output_file is None:
                output_file = input_file + ".nc"
            xr.Dataset(data_vars=fields).to_netcdf(
                Path(output_dir)/output_file)


if __name__ == "__main__":
    remap()
