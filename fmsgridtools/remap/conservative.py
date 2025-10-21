import numpy as np
from pathlib import Path
import xarray as xr

from fmsgridtools.remap.dataobj import DataObj
from fmsgridtools.shared.xgridobj import XGridObj
from fmsgridtools.shared.mosaicobj import MosaicObj

import pyfms


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


def get_interps_cpu(tgt_grid, src_grid_dict):
    
    interp_ids = {}        
    for src_tile in src_grid_dict:
        src_grid = src_grid_dict[src_tile]
        interp_ids[src_tile] = pyfms.horiz_interp.get_weights(
            lon_in=src_grid.x,
            lat_in=src_grid.y,
            lon_out=tgt_grid.x,
            lat_out=tgt_grid.y,
            nlon_in=src_grid.nx,
            nlat_in=src_grid.ny,
            nlon_out=tgt_grid.nx,
            nlat_out=tgt_grid.ny,
            save_weights_as_fregrid=True,
            convert_cf_order=False
        )

    #write remap file
    data_dict = {"tile1":{}}
    itile = 1
    for src_tile in interp_ids:
        this_dict = data_dict["tile1"][src_tile] = {}
        interpobj = pyfms.ConserveInterp(interp_ids[src_tile], weights_as_fregrid=True)
        this_dict["src_i"] = interpobj.i_src
        this_dict["src_j"] = interpobj.j_src
        this_dict["tgt_i"] = interpobj.i_dst
        this_dict["tgt_j"] = interpobj.j_dst
        this_dict["xarea"] = interpobj.xgrid_area
        this_dict["tile"] = [itile]*interpobj.nxgrid
        itile += 1

    xgrid = XGridObj(datadict=data_dict)
    xgrid.write(outfile="remap.nc")
        
    return interp_ids


def get_interps_gpu(tgt_grid_dict, src_grid_dict, domain, is_root_pe):

    #root to gpu
    if is_root_pe:
        xgrid = XGridObj(src_grid=src_grid_dict, tgt_grid=tgt_grid_dict, on_gpu=True)
        xgrid.create_xgrid()
        xgrid.write(outfile="remap.nc")        
    pyfms.mpp.sync()
        
    i = 1
    interp_ids = {}
    for src_tile in src_grid_dict:
        src_grid = src_grid_dict[src_tile]
        interp_ids[src_tile] = pyfms.horiz_interp.read_weights_conserve(
            "remap.nc",
            "fregrid",
            src_grid.nx,
            src_grid.ny,
            domain,
            src_tile = i
        )
        i += 1
    return interp_ids


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
          check_conserve: bool = False,
          gpu: bool = False):

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
    domain = pyfms.mpp_domains.define_domains(global_indices=global_indices)

    # get weights
    for tgt_tile in tgt_grid_dict:

        if gpu:
            tgt_grid = tgt_grid_dict[tgt_tile]
            interp_ids = get_interps_gpu({tgt_tile:tgt_grid}, src_grid_dict, domain, is_root_pe)
        else:
            # get tgt grid on domain
            tgt_grid_dict[tgt_tile].to_domain(domain)
            tgt_grid = tgt_grid_dict[tgt_tile]
            interp_ids = get_interps_cpu(tgt_grid, src_grid_dict)

        fms_areas = {}
        for src_tile in src_tiles:
            fms_areas[src_tile] =  src_grid_dict[src_tile].get_fms_area()

        # delete huge grids
        del src_grid_dict
        
        fields = {}
        for variable in scalar_variables:

            field = DataObj(input_dir=input_dir, tiles=src_mosaic.gridtiles,
                            datafile=input_file, variable=variable)

            #set tgt information
            field.tgt.dims.nx = domain.xsize_g
            field.tgt.dims.ny = domain.ysize_g
            field.tgt.attributes["interp_method"] = f"conserve_order{order}"
            field.tgt.set_xy_coords(tgt_grid.xt, tgt_grid.yt)

            scale_area = {}
            if field.area_averaged:
                for src_tile in src_tiles:
                    scale_area[src_tile] = field.static_area[src_tile]/fms_areas[src_tile]

            times = list(range(field.dims.ntime)) if field.dims.has_t else [None]
            klevels = list(range(field.dims.nz)) if field.dims.has_z else [None]

            # only if t and z exists
            new_t_start, new_z_start = field.dims.has_t_and_z, False

            for itime in times:
                new_t, new_z = new_t_start, new_z_start  # add to t axis
                for k in klevels:
                    remapped_data = call_horiz_interp(interp_ids, field, scale_area, k=k, itime=itime)
                    gathered = pyfms.mpp.gather(domain, remapped_data, convert_cf_order=False)
                    if is_root_pe:
                        field.tgt.save(gathered, new_t=new_t, new_z=new_z)
                    new_t, new_z = False, True  # add to z axis

            if is_root_pe:
                print(f"remapped {variable}", flush=True)
                fields[variable] = field.tgt.complete()

        if is_root_pe:
            if output_file is None:
                output_file = input_file + ".nc"
            xr.Dataset(data_vars=fields).to_netcdf(Path(output_dir)/output_file, unlimited_dims=["time"])

    pyfms.fms.end()
    
    
if __name__ == "__main__":
    remap()
