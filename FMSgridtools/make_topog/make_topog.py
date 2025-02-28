#!/home/Ryan.Mulhall/.conda/envs/dev/bin/python3
# make_topog entrypoint script

import click
import xarray
from pathlib import Path
from typing import Optional

from FMSgridtools import TopogObj, GridObj, MosaicObj
from FMSgridtools import get_provenance_attrs, check_file_is_there

MOSAIC_FILE_OPT_HELP="Path to a netCDF mosaic grid file to create a topography for"
TOPOG_TYPE_OPT_HELP="Specify 'type' of topography to generate, determines which algorithm is used to populate data."
TOPOG_FILE_OPT_HELP="Specific to 'realistic' topog_type option; path to a netCDF file containing topography data or realistic topography option"
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
              help = "")
@click.option("--y_refine",
              type = int,
              default = 2,
              help = "")
@click.option("--output",
              type = str,
              default = "topog.nc",
              help = "The name of the created netCDF file that contains mosaic topography. Default value is topog.nc")
# shared between topog type opts
# TODO change one of these args to either min/max depth or top/bottom depth
@click.option("--bottom_depth",
              type = float,
              default = 5000,
              help = "")
@click.option("--min_depth",
              type = float,
              default = 10,
              help = "")
@click.option("--scale_factor",
              type = float,
              default = 1,
              help = "")
# realistic
@click.option("--topog_file",
              type = str,
              help = "",
              required = False)
@click.option("--topog_field",
              type = str,
              help = "",
              required = False)
@click.option("--num_filter_pass",
              type = int,
              default = 1,
              help = "")
@click.option("--flat_bottom",
              is_flag = True,
              help = "")
@click.option("--fill_first_row",
              is_flag = True,
              help = "")
@click.option("--filter_topog",
              is_flag = True,
              help = "")
@click.option("--full_cell",
              is_flag = True,
              help = "")
@click.option("--dont_fill_isolated_cells",
              is_flag = True,
              help = "")
@click.option("--dont_change_landmask",
              is_flag = True,
              help = "")
@click.option("--kmt_min",
              type = int,
              default = 2,
              help = "Minimum number of vertical levels")
@click.option("--dont_adjust_topo",
              is_flag = True,
              help = "")
@click.option("--fraction_full_cell",
              type = float,
              default = 0.2,
              help = "")
@click.option("--open_very_this_cell",
              is_flag = True,
              help = "")
@click.option("--min_thickness",
              type = float,
              default = 0.1,
              help = "Minimum vertical thickness allowed")
@click.option("--rotate_poly",
              is_flag = True,
              help = "")
@click.option("--on_grid",
              is_flag = True,
              help = "")
@click.option("--round_shallow",
              is_flag = True,
              help = "")
@click.option("--fill_shallow",
              is_flag = True,
              help = "")
@click.option("--deepen_shallow",
              is_flag = True,
              help = "")
@click.option("--smooth_topo_allow_deepening",
              is_flag = True,
              help = "")
@click.option("--vgrid_file",
              type = str,
              required = False,
              help = "")
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
    output : Optional[str] = None):

    # get provenance data
    prov_attrs = get_provenance_attrs()

    # read in object fields from file
    inputMosaicObj = MosaicObj(mosaic_file=mosaic) 

    # get all the data we need to generate topographies
    _ntiles = inputMosaicObj.get_ntiles()
    inputMosaicObj.griddict()
    x_tile = {}
    y_tile = {}
    for tileName in inputMosaicObj.grid_dict.keys():
        x_tile[tileName] = inputMosaicObj.grid_dict[tileName].x
        y_tile[tileName] = inputMosaicObj.grid_dict[tileName].y

    # create new TopogStruct for output
    topogOut = TopogObj(output_name=output, ntiles=_ntiles, global_attrs=prov_attrs, x_tile = x_tile, y_tile = y_tile,
                        x_refine=x_refine, y_refine=y_refine, scale_factor=scale_factor)

    if (topog_type == "realistic"):
        topogOut.make_topog_realistic(
            x_tile, y_tile, topog_file, topog_field, vgrid_file,
            num_filter_pass, kmt_min, min_depth, min_thickness, fraction_full_cell, 
            flat_bottom, fill_first_row, filter_topog, round_shallow, fill_shallow,
            deepen_shallow, smooth_topo_allow_deepening, full_cell, dont_fill_isolated_cells,
            on_grid, dont_change_landmask, dont_adjust_topo, open_very_this_cell)
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
