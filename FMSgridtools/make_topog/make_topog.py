#!/home/Ryan.Mulhall/.conda/envs/dev/bin/python3
# make_topog entrypoint script

import click
from typing import Optional

from FMSgridtools import TopogObj, MosaicObj
from FMSgridtools import get_provenance_attrs, check_file_is_there

MOSAIC_FILE_OPT_HELP="Specify the mosaic file where topography data will be located."
TOPOG_TYPE_OPT_HELP="""
Specifies how topography output data is generated, possible values are:

"""
TOPOG_FILE_OPT_HELP="Only used for 'realistic' option; Path to a topography data file"
TOPOG_FIELD_OPT_HELP="""Only used for 'realistic' option; Name of the field/variable
containing topography data in the given topography_data file
"""
REFINEMENT_OPT_HELP="""The refinement ratio of model grid vs supergrid in the x or y direction.
(ie. for the default refinement of 2, topograpgy generated will have half the number of x/y points)"""
OUTPUT_OPT_HELP="Name to write for the output topography file"
BOTTOM_DEPTH_HELP="Maximum depth of the ocean used by the given topog_type method. If using rectangular_basin, this depth will be uniform."
MIN_DEPTH_HELP="Minimum depth of the ocean"
SCALE_FACTOR_HELP="Scaling factor for topography data (ie. -1 to flip sign or 0.01 to convert to centimeters)."
NUM_FILTER_PASS_HELP="Number of passes of spatial filter"
FLAT_BOTTOM_HELP="Generate flat bottom over ocean points"
FILL_FIRST_ROW_HELP="Make first row of ocean model all land points for ice model"
FILTER_TOPOG_HELP="Apply filter to topography"
ROUND_SHALLOW_HELP="Make cells land if the depth is less than 1/2 minimum depth, otherwise make ocean"
FILL_SHALLOW_HELP="Make cells land if less than minimum depth"
DEEPEN_SHALLOW_HELP="Make cells less than minimum depth equal to minimum depth"
SMOOTH_TOPO_ALLOW_DEEPENING_HELP="Allow filter to deepen cells"
VGRID_FILE_HELP="""Path to a vertical grid file. When a vgrid file is specified, an additional output variable
'num_levels' will be written out to provide the number of vertical T-cells, and depth data 
These following optional arguments are specific to when a vgrid file is provided:
    --dont_adjust_topo, --dont_fill_isolated_cells, --full_cell, --dont_open_very_this_cell, --flat_bottom
    --fraction_full_cell, --minimum_thickness, --dont_change_landmask, --kmt_min, --round_shallow, --fill_shallow,
    --deepen_shallow
"""
FULL_CELL_HELP="Do not generate partial bottom cells"
DONT_FILL_ISOLATED_CELLS_HELP="Allow non-advective tracer cells (strongly not recommended)"
ON_GRID_HELP="Assume that the topography is already on a model grid, preventing interpolation"
DONT_CHANGE_LANDMASK_HELP="Do not change the land/sea mask when filling isolated cells"
KMT_MIN_HELP="Minimum number of vertical levels"
DONT_ADJUST_TOPO_HELP="Don't adjust topography for vgrid by enforcing minimumm depth, removing isolated cells, and restricting partial cells. (strongly not recommended)"
FRACTION_FULL_CELL_HELP="""Fraction of the associated full cell that a corresponding
partial cell thickness is no smaller than.
"""
DONT_OPEN_VERY_THIS_CELL_HELP="Disables opening/closing cells based on the the size of the effect in depth value"
MIN_THICKNESS_HELP="Minimum vertical thickness allowed"
ROTATE_POLY_HELP="""Calculate polar polygon areas by calculating the area of a copy
of the polygon, with the copy being rotated far away from the pole
"""
# TODO add rest of the help descriptions

@click.command()
# required args regardless of topog_type
@click.option("-m",
              "--mosaic",
              type = str,
              help = MOSAIC_FILE_OPT_HELP,
              required = True)
@click.option("-t",
              "--topog_type",
              type = str,
              help = TOPOG_TYPE_OPT_HELP,
              required = True)
# not specific to a type
@click.option("--x_refine",
              type = int,
              default = 2,
              help = REFINEMENT_OPT_HELP)
@click.option("--y_refine",
              type = int,
              default = 2,
              help = REFINEMENT_OPT_HELP)
@click.option("--output",
              type = str,
              default = "topog.nc",
              help = OUTPUT_OPT_HELP)
@click.option("--verbose",
              is_flag = True,
              help = "Enable debug output")
# shared between topog type opts
@click.option("--bottom_depth",
              type = float,
              default = 5000.0,
              help = BOTTOM_DEPTH_HELP)
@click.option("--min_depth",
              type = float,
              default = 10.0,
              help = MIN_DEPTH_HELP)
@click.option("--scale_factor",
              type = float,
              default = 1.0,
              help = SCALE_FACTOR_HELP)
# realistic
@click.option("--topog_file",
              type = str,
              help = TOPOG_FILE_OPT_HELP,
              required = False)
@click.option("--topog_field",
              type = str,
              help = TOPOG_FIELD_OPT_HELP,
              required = False)
@click.option("--num_filter_pass",
              type = int,
              default = 1,
              help = NUM_FILTER_PASS_HELP)
@click.option("--flat_bottom",
              is_flag = True,
              help = FLAT_BOTTOM_HELP)
@click.option("--fill_first_row",
              is_flag = True,
              help = FILL_FIRST_ROW_HELP)
@click.option("--filter_topog",
              is_flag = True,
              help = FILTER_TOPOG_HELP)
@click.option("--full_cell",
              is_flag = True,
              help = FULL_CELL_HELP)
@click.option("--dont_fill_isolated_cells",
              is_flag = True,
              help = DONT_FILL_ISOLATED_CELLS_HELP)
@click.option("--dont_change_landmask",
              is_flag = True,
              help = DONT_CHANGE_LANDMASK_HELP)
@click.option("--kmt_min",
              type = int,
              default = 2,
              help = KMT_MIN_HELP)
@click.option("--dont_adjust_topo",
              is_flag = True,
              help = DONT_ADJUST_TOPO_HELP)
@click.option("--fraction_full_cell",
              type = float,
              default = 0.2,
              help = FRACTION_FULL_CELL_HELP)
@click.option("--open_very_this_cell",
              is_flag = True,
              help = DONT_OPEN_VERY_THIS_CELL_HELP)
@click.option("--min_thickness",
              type = float,
              default = 0.1,
              help = MIN_THICKNESS_HELP)
@click.option("--rotate_poly",
              is_flag = True,
              help = ROTATE_POLY_HELP)
@click.option("--on_grid",
              is_flag = True,
              help = ON_GRID_HELP)
@click.option("--round_shallow",
              is_flag = True,
              help = ROUND_SHALLOW_HELP)
@click.option("--fill_shallow",
              is_flag = True,
              help = FILL_SHALLOW_HELP)
@click.option("--deepen_shallow",
              is_flag = True,
              help = DEEPEN_SHALLOW_HELP)
@click.option("--smooth_topo_allow_deepening",
              is_flag = True,
              help = SMOOTH_TOPO_ALLOW_DEEPENING_HELP)
@click.option("--vgrid_file",
              type = str,
              required = False,
              help = VGRID_FILE_HELP)
# gaussian
@click.option("--gauss_amp",
              type = float,
              default = 0.5,
              help = "")
@click.option("--gauss_scale",
              type = float,
              default = 0.25,
              help = "")
@click.option("--slope_x",
              type = float,
              default = 0,
              help = "")
@click.option("--slope_y",
              type = float,
              default = 0,
              help = "")
# bowl
@click.option("--bowl_south",
              type = float,
              default = 60,
              help = "")
@click.option("--bowl_north",
              type = float,
              default = 70,
              help = "")
@click.option("--bowl_west",
              type = float,
              default = 0,
              help = "")
@click.option("--bowl_east",
              type = float,
              default = 20,
              help = "")
# box channel
# these are supposed to be ints
@click.option("--jwest_south",
              type = int,
              default = 0,
              help = "")
@click.option("--jwest_north",
              type = int,
              default = 0,
              help = "")
@click.option("--ieast_south",
              type = int,
              default = 0,
              help = "")
@click.option("--ieast_north",
              type = int,
              default = 0,
              help = "")
# dome
@click.option("--dome_slope",
              type = float,
              default = 0,
              help = "")
@click.option("--dome_bottom",
              type = float,
              default = 0,
              help = "")
@click.option("--dome_embayment_west",
              type = float,
              default = 0,
              help = "")
@click.option("--dome_embayment_east",
              type = float,
              default = 0,
              help = "")
@click.option("--dome_embayment_south",
              type = float,
              default = 0,
              help = "")
@click.option("--dome_embayment_depth",
              type = float,
              default = 0,
              help = "")
def make_topog(
    mosaic : str = None,
    topog_type : str = None,
    x_refine : Optional[int] = None,
    y_refine : Optional[int] = None,
    bottom_depth : Optional[int] = None,
    min_depth : Optional[int] = None,
    scale_factor : Optional[int] = None,
    topog_file : Optional[str] = None,
    topog_field : Optional[str] = None,
    num_filter_pass : Optional[int] = None,
    flat_bottom : Optional[bool] = None,
    fill_first_row : Optional[bool] = None,
    filter_topog : Optional[bool] = None,
    full_cell : Optional[bool] = None,
    dont_fill_isolated_cells : Optional[bool] = None,
    dont_change_landmask : Optional[bool] = None,
    kmt_min : Optional[int] = None,
    dont_adjust_topo : Optional[bool] = None,
    fraction_full_cell : Optional[float] = None,
    open_very_this_cell : Optional[bool] = None,
    min_thickness : Optional[float] = None,
    rotate_poly : Optional[bool] = None,
    on_grid : Optional[bool] = None,
    round_shallow : Optional[bool] = None,
    fill_shallow : Optional[bool] = None,
    deepen_shallow : Optional[bool] = None,
    smooth_topo_allow_deepening : Optional[bool] = None,
    vgrid_file : Optional[str] = None,
    gauss_amp : Optional[float] = None,
    gauss_scale : Optional[float] = None,
    slope_x : Optional[float] = None,
    slope_y : Optional[float] = None,
    bowl_south : Optional[float] = None,
    bowl_north : Optional[float] = None,
    bowl_west : Optional[float] = None,
    bowl_east : Optional[float] = None,
    jwest_south : Optional[int] = None,
    jwest_north : Optional[int] = None,
    ieast_south : Optional[int] = None,
    ieast_north : Optional[int] = None,
    dome_slope : Optional[float] = None,
    dome_bottom : Optional[float] = None,
    dome_embayment_west : Optional[float] = None,
    dome_embayment_east : Optional[float] = None,
    dome_embayment_south : Optional[float] = None,
    dome_embayment_depth : Optional[float] = None,
    output : Optional[str] = None,
    verbose : Optional[bool] = None):
    """
make_topog can generate topography for any Mosaic. The output file
will contain the topography for each tile in the Mosaic. The field name in
the output topography file will be "depth_tile#" if multi-tile, "depth" if single tile and it is positive down.
The topography data will be defined on model grid, the model grid size will be
supergrid grid size divided by refinement (x_refine, y_refine, default is 2).
--mosaic is a required option and all other options are optional, but
some options are required depending on the choice of topog_type.
More details on the topog_type options are below.

'realistic':  Remap the topography onto the current grid from some source data file.

              This is the default value if no --topog_type is provided. 

              --topog_file and --topog_field must be specified.

              Optional arguments are:

              --min_depth --scale_factor --num_filter_pass --flat_bottom --min_thickness
              --fill_first_row  --filter_topog --round_shallow --fill_shallow --deepen_shallow
              --smooth_topo_allow_deepening --vgrid_file --full_cell --dont_fill_isolated_cells --on_grid
              --dont_change_landmask --kmt_min  --dont_adjust_topo --fraction_full_cell --dont_open_very_this_cell

              Realistic currently only supports single-tile grids, and x/y_refinement values of 2.

'rectangular_basin': Constructs a rectangular basin with a flat bottom.
                     --bottom_depth is its optional argument. Set bottom_depth
                     to 0 to get all land topography.

'gaussian':          Construct gaussian bump on a sloping bottom.
                     --bottom_depth, --min_depth --gauss_amp, --gauss_scale,
                     --slope_x, --slope_y are optional arguments.

'bowl':              --bottom_depth, --min_depth, --bowl_south, --bowl_north,
                     --bowl_west, --bowl_east are optional arguments.

'idealized':          Generates an 'idealized' not very realistic topography.
                      --bottom_depth, --min_depth are optional arguments.

'box_channel':        Generate a box_channel topography. The interior of the
                      grid box is a flat bottom. The boundary of the grid
                      box is land except points [jwest_south:jwest_north]
                      and [ieast_south:ieast_north]. --jwest_south, jwest_north,
                      --ieast_south and ieast_north need to be specified.
                      --bottom_depth are optional arguments.

'dome':               similar (not identical) to DOME configuration of
                      Legg etal Ocean Modelling (2005).  --dome_slope,
                      --dome_bottom, --dome_embayment_west,
                      --dome_embayment_east, --dome_embayment_south and
                      --dome_embayment_depth are optional arguments.
    """

    # get provenance data
    prov_attrs = get_provenance_attrs()

    # read in object fields from file
    inputMosaicObj = MosaicObj(mosaic_file=mosaic) 

    # get number of tiles and create dicts for x/y data 
    _ntiles = inputMosaicObj.get_ntiles()
    inputMosaicObj.griddict()
    x_tile = {}
    y_tile = {}
    for tileName in inputMosaicObj.grid_dict.keys():
        x_tile[tileName] = inputMosaicObj.grid_dict[tileName].x
        y_tile[tileName] = inputMosaicObj.grid_dict[tileName].y

    # create new TopogStruct for output
    topogOut = TopogObj(mosaic_filename=mosaic, output_name=output, ntiles=_ntiles, global_attrs=prov_attrs,
                        x_tile = x_tile, y_tile = y_tile, x_refine=x_refine, y_refine=y_refine,
                        scale_factor=scale_factor, debug=verbose)

    # generate the topography data using the given topog_type algorithm 
    if (topog_type == "realistic"):
        topogOut.make_topog_realistic(
            x_tile, y_tile, topog_file, topog_field, vgrid_file,
            num_filter_pass, kmt_min, min_thickness, fraction_full_cell, 
            flat_bottom, fill_first_row, filter_topog, round_shallow, fill_shallow,
            deepen_shallow, smooth_topo_allow_deepening, full_cell, dont_fill_isolated_cells,
            on_grid, dont_change_landmask, dont_adjust_topo, open_very_this_cell, inputMosaicObj.gridfiles)
    elif (topog_type == "rectangular_basin"):
        topogOut.make_rectangular_basin(bottom_depth)
    elif (topog_type == "gaussian"):
        topogOut.make_topog_gaussian()
    elif (topog_type == "bowl"):
        topogOut.make_topog_bowl()
    elif (topog_type == "idealized"):
        topogOut.make_topog_idealized()
    elif (topog_type == "box_channel"):
        topogOut.make_topog_box_channel()
    elif (topog_type == "dome"):
        topogOut.make_topog_dome()
    else:
        print("Error: invalid topog_type argument given, must be one of [realistic, gaussian, bowl, box_channel, dome]")
        exit(1)

    # write out the result
    topogOut.write_topog_file()

if __name__ == "__main__":
    make_topog()
