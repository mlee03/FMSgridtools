import click
import functools

def common_options(func):
    @click.option("--input_dir",
                  default = "./",
                  type = click.Path(exists=True),
                  help =
                  """
                  Directory containing the input files such as
                  the mosaic and input field files.
                  """
    )
    @click.option("--output_dir",
                  default = "./",
                  type = click.Path(exists=True),
                  help =
                  """
                  Directory to write output files such as
                  the output field files and the remap file.
                  """
    )
    @click.option("--input_mosaic_dir",
                  default = "./",
                  type = click.Path(exists=True),
                  help =
                  """
                  Directory containing the input mosaic file.
                  """
    )
    @click.option("--output_mosaic_dir",
                  default = "./",
                  type = click.Path(exists=True),
                  help =
                  """
                  Directory containing the output mosaic file.
                  """
    )
    @click.option("--input_file",
                  #type = click.File(),
                  help =
                  """
                  Input file with field data that will be remapped.
                  For a multi-tile source grid, the suffix 'tile#.nc'
                  should be ommitted.  The directory path to the
                  input files should be specified with input_dir.
                  Else, the current directory will be set as input_dir
                  """
    )
    @click.option("--output_file",
                  type = str,
                  help =
                  """
                  Name of the output files that will be outputted with
                  remapped data.  If output_file is not specified, the output
                  file will take the prefix of the input_file.  For a
                  multi-tile target grid, the suffix 'tile#.nc' should
                  be ommitted
                  """
    )
    @click.option("--src_mosaic",
                  #type = click.File(),
                  help =
                  """
                  Mosaic file for the source grid
                  """
    )
    @click.option("--tgt_mosaic",
                  #type = click.File(),
                  help =
                  """
                  Mosaic file for the target grid.
                  If target mosaic is not provided, remap will generate a lat-lon
                  target grid on-the-fly.  For this case, users must provide the
                  dimensions of the lat/lon grid via tgt_nlon and tgt_nlat
                  """
    )
    @click.option("--scalar_variables",
                  type = list[str],
                  help =
                  """
                  List of scalar variables to rempap
                  """
    )
    @click.option("--tgt_nlon",
                  type = int,
                  help =
                  """
                  Number of grid cells in x-direction for a lat-lon grid.
                  This value must be provided if target mosaic is not
                  provided.
                  """
    )
    @click.option("--tgt_nlat",
                  type = int,
                  help =
                  """
                  Number of grid cells in y-direction for a lat-lon grid.
                  This value must be provided if target mosaic is not
                  provided.
                  """
    )
    @click.option("--lon_bounds",
                  type = float,
                  nargs = 2,
                  help =
                  """
                  Bouding longitudinal points (in degrees) on the target grid
                  on which the remapping is desired.  A pair of values must
                  be provided.  For example, --tgt_lonbounds 0 45 will remap
                  data only for the longitudinal region between 0 and 45 degrees
                  """
    )
    @click.option("--lat_bounds",
                  type = float,
                  nargs = 2,
                  help =
                  """
                  Bouding latitudinal points (in degrees) on the target grid
                  on which remapping is desired.  A pair of values must
                  be provided.  For example, --lat_bounds 0 45 will remap
                  data only for the latitudinal region between 0 and 45 degrees
                  """
    )
    @click.option("--kbounds",
                  type = int,
                  nargs = 2,
                  help =
                  """
                  bounding vertical levels on which remapping is desired.
                  For example, --kbounds 1 10 wil remap data only
                  for vertical levels ranging from 1 to 10
                  """
    )
    @click.option("--tbounds",
                  type = int,
                  nargs = 2,
                  help =
                  """
                  bounding timesteps on which remapping is desired.
                  For example, --tbounds 1 5 will remap data
                  for timepoints 1 to 5
                  """
    )
    @click.option("--debug", is_flag=True, default=False)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
