import numpy as np
from pathlib import Path
import xarray as xr

from fmsgridtools.remap.dataobj import DataObj
from fmsgridtools.shared.xgridobj import XGridObj
from fmsgridtools.shared.mosaicobj import MosaicObj

import pyfms


def get_variables(input_dir: str|Path, input_file: str, tile: str = None):
    if tile is None:
        input_file += ".nc"
    else:
        input_file += "." + tile + ".nc"
    with xr.open_dataset(Path(input_dir)/input_file, decode_cf=False) as dataset:
        return [key for key in dataset.data_vars]


def call_horiz_interp(interp_ids: dict, field: DataObj, scale_area: dict = None,
                      k: int = None, itime: int = None):

    itile = 0
    for src_tile in interp_ids:

        field_in = field.get_data(tile=src_tile, klevel=k, timepoint=itime)
        if field.area_averaged:
            if scale_area is None: raise RuntimeError("must provide scale_area")
            field_in *= scale_area[src_tile]

        if itile == 0:
            remapped_data = pyfms.horiz_interp.interp(interp_id=interp_ids[src_tile],
                                                      data_in=field_in,
                                                      convert_cf_order=False)
        else:
            remapped_data += pyfms.horiz_interp.interp(interp_id=interp_ids[src_tile],
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

    input_mosaic_dir = "/home/Mikyung.Lee/FRE-NCTools/test-benchmark/tests_fregrid/Testa-conserve1-output/"
    output_mosaic_dir = input_mosaic_dir
    input_dir = "/home/Mikyung.Lee/FRE-NCTools/DONOTDELETEME_DATA/TESTS/TESTS_INPUT/Testa-input/"
    src_mosaic = "C96_mosaic.nc"
    tgt_mosaic = "lonlat_288x180_mosaic.nc"
    input_file = "00010101.atmos_month_aer"
    scalar_variables = ["zsurf", "ps", "temp", "sphum", "sulfate", "sulfate_col", "sm_dust", "sm_dust_col"]#,
                        #"lg_dust", "lg_dust_col", "salt", "salt_col", "blk_crb", "blk_crb_col", "org_crb",
                        #"org_crb_col", "sulfate_ex_c_vs", "sm_dst_ex_c_vs", "lg_dst_ex_c_vs",
                        #"blk_crb_ex_c_vs", "org_crb_ex_c_vs", "salt_ex_c_vs", "aer_ex_c_vs",
                        #"aer_ab_c_vs", "aer_c", "aer_ex_vs", "aer_ab_vs"]

    # get input grid
    src_mosaic = MosaicObj(input_dir=input_mosaic_dir, mosaic_file=src_mosaic).read()
    src_grid_dict = src_mosaic.get_grid(toradians=True, agrid=True)
    src_tiles = src_mosaic.gridtiles

    # get target grid
    tgt_mosaic = MosaicObj(input_dir=output_mosaic_dir, mosaic_file=tgt_mosaic).read()
    tgt_grid_dict = tgt_mosaic.get_grid(toradians=True, agrid=True)

    # initialize fms
    pyfms.fms.init(ndomain=len(tgt_grid_dict))
    pyfms.horiz_interp.init(ninterp=len(src_grid_dict))

    # identify root pe
    is_root_pe = pyfms.mpp.pe() == pyfms.mpp.root_pe()

    # domain
    global_indices = [0, tgt_grid_dict['tile1'].nx-1, 0, tgt_grid_dict['tile1'].ny-1]
    layout = pyfms.mpp_domains.define_layout(global_indices, ndivs=pyfms.mpp.npes())
    domain = pyfms.mpp_domains.define_domains(global_indices=global_indices, layout=layout)

    # get tgt grid on domain
    for tile in tgt_grid_dict:
        tgt_grid_dict[tile].to_domain(domain)

    # get weights
    for tgt_tile in tgt_grid_dict:

        interp_ids, fms_areas = {}, {}
        tgt_grid = tgt_grid_dict[tgt_tile]

        for src_tile in src_tiles:

            src_grid = src_grid_dict[src_tile]

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

            fms_areas[src_tile] =  src_grid.get_fms_area()

        # delete huge grids
        del src_grid_dict

        fields = {}
        for variable in scalar_variables:

            print(f"**{variable}**", flush=True)

            field = DataObj(input_dir=input_dir, tiles=src_mosaic.gridtiles,
                            datafile=input_file, variable=variable)

            #THISISWRONG
            field.tgt.dims.nx = domain.ieg - domain.isg + 1
            field.tgt.dims.ny = domain.jeg - domain.isg + 1

            scale_area = {}
            if field.area_averaged:
                for src_tile in src_tiles:
                    scale_area[src_tile] = field.static_area[src_tile]/fms_areas[src_tile]

            times = list(range(field.dims.ntime)) if field.dims.has_t else [None]
            klevels = list(range(field.dims.nz)) if field.dims.has_z else [None]

            new_t_start, new_z_start = field.dims.has_t_and_z, False

            for itime in times:
                new_t, new_z = new_t_start, new_z_start  # only matters if t and z exists
                for k in klevels:
                    remapped_data = call_horiz_interp(interp_ids, field, scale_area, k=k, itime=itime)
                    gathered = pyfms.mpp.gather(domain, remapped_data, convert_cf_order=False)
                    if is_root_pe:
                        field.tgt.save(gathered, new_t=new_t, new_z=new_z)
                    new_t, new_z = False, True  # only matters if t and z exists

            if is_root_pe:
                fields[variable] = field.tgt.complete()
                #(field.tgt.data)

        if is_root_pe:
            if output_file is None:
                output_file = input_file + ".nc"
            xr.Dataset(data_vars=fields).to_netcdf(Path(output_dir)/output_file)


if __name__ == "__main__":
    remap()
