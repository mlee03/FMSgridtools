import click
import logging

from fmsgridtools.remap import _options
from fmsgridtools.utils import setlogger
from fmsgridtools.remap import conservative

logger = logging.getLogger(__name__)

@click.command()
@_options.common_options
@click.option("--order",
              type = int,
              default = 1,
              help =
              """
              Only 1 or 2 order is supported for conservative interpolation
              """
)
@click.option("--check_conserve",
              type = bool,
              help =
              """
              If true, output grid area conservative will be checked
              """
)
def conservative_method(input_dir, output_dir, input_file, output_file, #common_options
                        src_mosaic, tgt_mosaic, tgt_nlon, tgt_nlat,     #common_options
                        scalar_variables, lon_bounds, lat_bounds, 
                        kbounds, tbounds, debug, order, check_conserve):
    
    setlogger.setconfig("remap.log", debug)
    logger.info("Starting conservative remapping")
    
    #create an xgrid object
    xgrid = XGridObj(input_dir, src_mosaic_file=src_mosaic, tgt_mosaic_file=tgt_mosaic)
    xgrid.create_xgrid()

    xgrid = conservative.remap(xgrid, input_dir, output_dir, input_file, output_file,
                               scalar_variables, lon_bounds, lat_bounds, kbounds, tbounds,
                               order, check_conserve)    
