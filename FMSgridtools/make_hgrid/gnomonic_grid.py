import sys
import numpy as np

from FMSgridtools.make_hgrid.hgridobj import HGridObj
import pyfrenctools

def make(
    nlon: str,
    shift_fac: float,
    stretch_factor: float,
    target_lon: float,
    target_lat: float,
    nest_grids: int,
    parent_tile: str,
    refine_ratio: str,
    istart_nest: str,
    iend_nest: str,
    jstart_nest: str,
    jend_nest: str,
    halo: int,
    out_halo: int,
    grid_name: str,
    output_length_angle: bool,
    do_schmidt: bool,
    do_cube_transform: bool,
    verbose: bool,
):
    
    if do_cube_transform and do_schmidt:
        raise RuntimeError("make_hgrid: both --do_cube_transform and --do_schmidt are set")
    
    grid_obj = HGridObj()

    if nlon is not None:
        nlon = np.fromstring(nlon, dtype=np.int32, sep=',')
    else:
        nlon = np.empty(shape=99, dtype=np.int32)

    if parent_tile is not None:
        parent_tile = np.fromstring(parent_tile, dtype=np.int32, sep=',')
    else:
        parent_tile = np.zeros(shape=128, dtype=np.int32)

    if refine_ratio is not None:
        refine_ratio = np.fromstring(refine_ratio, dtype=np.int32, sep=',')
    else:
        refine_ratio = np.zeros(shape=128, dtype=np.int32)
    
    if istart_nest is not None:
        istart_nest = np.fromstring(istart_nest, dtype=np.int32, sep=',')
    else:
        istart_nest = np.zeros(shape=128, dtype=np.int32)

    if iend_nest is not None:
        iend_nest = np.fromstring(iend_nest, dtype=np.int32, sep=',')
    else:
        iend_nest = np.zeros(shape=128, dtype=np.int32)
    
    if jstart_nest is not None:
        jstart_nest = np.fromstring(jstart_nest, dtype=np.int32, sep=',')
    else:
        jstart_nest = np.zeros(shape=128, dtype=np.int32)

    if jend_nest is not None:
        jend_nest = np.fromstring(jend_nest, dtype=np.int32, sep=',')
    else:
        jend_nest = np.zeros(shape=128, dtype=np.int32)

    ntiles = 6
    ntiles_global = 6

    projection = "cube_gnomonic"
    conformal = False

    if do_schmidt or do_cube_transform:
        raise RuntimeError("make_hgrid: grid type is 'gnomonic_ed, --stretch_factor, --target_lon\
                  and --target_lat must be set when --do_schmidt or --do_cube_transform is set")
    
    for n in range(nest_grids):
        if refine_ratio[n] == 0:
            raise RuntimeError("make_hgrid: --refine_ratio must be set when --nest_grids is set")
        if parent_tile[n] == 0:
            print(f"NOTE from make_hgrid: parent_tile is 0, the output grid will have resolution refine_ration*nlon\n", file=sys.stderr)
        else:
            if istart_nest[n] == 0:
                raise RuntimeError("make_hgrid: --istart_nest must be set when --nest_grids is set")
            if iend_nest[n] == 0:
                raise RuntimeError("make_hgrid: --iend_nest must be set when --nest_grids is set")
            if jstart_nest[n] == 0:
                raise RuntimeError("make_hgrid: --jstart_nest must be set when --nest_grids is set")
            if jend_nest[n] == 0:
                raise RuntimeError("make_hgrid: --jend_nest must be set when --nest_grids is set")
            if halo == 0:
                raise RuntimeError("make_hgrid: --halo must be set when --nest_grids is set")
            ntiles += 1
            if verbose:
                print(f"Configuration for nest {ntiles} validated\n", file=sys.stderr)

    if verbose:
        print(f"Updated number of tiles, including nests (ntiles): {ntiles}\n", file=sys.stderr)

    grid_obj.make_grid_info(
        nlon=nlon,
        ntiles=ntiles,
        ntiles_global=ntiles_global,
        nest_grids=nest_grids,
        parent_tile=parent_tile,
        refine_ratio=refine_ratio,
        istart_nest=istart_nest,
        iend_nest=iend_nest,
        jstart_nest=jstart_nest,
        jend_nest=jend_nest,
        grid_type="GNOMONIC_ED",
        conformal=conformal,
        output_length_angle=output_length_angle,
        verbose=verbose,
    )

    # if nest_grids == 1 and parent_tile[0] == 0:
    #     pyfrenctools.make_hgrid_wrappers.create_gnomonic_cubic_grid_GR(
    #         grid_type=grid_type,
    #         nxl=grid_obj.nxl,
    #         nyl=grid_obj.nyl,
    #         x=grid_obj.x,
    #         y=grid_obj.y,
    #         dx=grid_obj.dx,
    #         dy=grid_obj.dy,
    #         area=grid_obj.area,
    #         angle_dx=grid_obj.angle_dx,
    #         angle_dy=grid_obj.angle_dy,
    #         shift_fac=shift_fac,
    #         do_schmidt=do_schmidt,
    #         do_cube_transform=do_cube_transform,
    #         stretch_factor=stretch_factor,
    #         target_lon=target_lon,
    #         target_lat=target_lat,
    #         nest_grids=nest_grids,
    #         parent_tile=parent_tile[0],
    #         refine_ratio=refine_ratio[0],
    #         istart_nest=istart_nest[0],
    #         iend_nest=iend_nest[0],
    #         jstart_nest=jstart_nest[0],
    #         jend_nest=jend_nest[0],
    #         halo=halo,
    #         output_length_angle=output_length_angle,
    #     )
    # else:
    #     pyfrenctools.make_hgrid_wrappers.create_gnomonic_cubic_grid(
    #         grid_type=grid_type,
    #         nxl=grid_obj.nxl,
    #         nyl=grid_obj.nyl,
    #         x=grid_obj.x,
    #         y=grid_obj.y,
    #         dx=grid_obj.dx,
    #         dy=grid_obj.dy,
    #         area=grid_obj.area,
    #         angle_dx=grid_obj.angle_dx,
    #         angle_dy=grid_obj.angle_dy,
    #         shift_fac=shift_fac,
    #         do_schmidt=do_schmidt,
    #         do_cube_transform=do_cube_transform,
    #         stretch_factor=stretch_factor,
    #         target_lon=target_lon,
    #         target_lat=target_lat,
    #         nest_grids=nest_grids,
    #         parent_tile=parent_tile,
    #         refine_ratio=refine_ratio,
    #         istart_nest=istart_nest,
    #         iend_nest=iend_nest,
    #         jstart_nest=jstart_nest,
    #         jend_nest=jend_nest,
    #         halo=halo,
    #         output_length_angle=output_length_angle,
    #     )

    # grid_obj.write_out_hgrid(
    #     grid_type="gnomonic_ed",
    #     grid_name=grid_name,
    #     ntiles=ntiles,
    #     projection=projection,
    #     conformal=conformal,
    #     out_halo=out_halo,
    #     output_length_angle=output_length_angle,
    #     verbose=verbose,
    # )