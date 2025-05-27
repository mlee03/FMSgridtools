import click
import logging

from . import _options
from ..utils import setlogger
from . import conservative

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
@click.option("--static_file",
              type = click.Path(exists=True),
              help =
              """
              To remap data where cell_methods = CELL_METHODS_MEAN, the static_file
              will src grid cell areas should be provided
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
                        lon_bounds, lat_bounds, kbounds, tbounds,       #common_options
                        debug, order, static_file, check_conserve):
    
    setlogger.setconfig("remap.log", debug)
    logger.info("Starting conservative remapping")
    
    conservative.remap(src_mosaic, input_dir, output_dir, input_file,
                       output_file, tgt_mosaic, tgt_nlon, tgt_nlat,
                       lon_bounds, lat_bounds, kbounds, tbounds,
                       order, static_file, check_conserve)    
