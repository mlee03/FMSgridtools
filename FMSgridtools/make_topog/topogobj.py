from typing import List
import xarray as xr
import numpy as np
import numpy.typing as npt
import dataclasses

# represents topography output file created by make_topog
# contains parameters for topography generation that aren't tied to a specific topography type
# and depth values from specified topog_type algorithm once generated.
# if multiple tiles are used, the third index of depth will be the the tile number
@dataclasses.dataclass
class TopogObj():
    output_name: str = None
    ntiles: int = None
    nx: int = None
    ny: int = None
    x_refine: int = None
    y_refine: int = None
    scale_factor: float = None
    depth: npt.NDArray[np.float64] = None
    dataset: xr.Dataset = None
    __data_is_generated: bool = False

    # sets up dataset variables
    def __post_init__(self):
        depth_vars = dict()
        depth_attrs = dict()
        depth_attrs["standard_name"] = "topographic depth at T-cell centers"
        depth_attrs["units"] = "meters"
        depth_coords = xr.Coordinates( {'ny': np.empty(self.ny), 'nx': np.empty(self.nx)} )
        # TODO check dims of depth
        # if single tile exclude tile number in variable name
        if (self.ntiles == 1):
            depth_vars["depth"]= xr.DataArray(
                coords=depth_coords,
                dims=["ny", "nx"],
                attrs=depth_attrs,
            )
        # loop through ntiles and add depth_tile<n> variable for each
        else:
            for i in range(1,self.ntiles+1):
                depthVarName = "depth_tile" + str(i)
                depth_vars[depthVarName] = xr.DataArray(
                    coords=depth_coords,
                    dims=["ny", "nx"],
                    attrs=depth_attrs,
                )
        # create dataset from vars
        self.ds = xr.Dataset(
            data_vars = depth_vars,
        )
        self.ds = self.ds.expand_dims({'ntiles': self.ntiles})
        self.ds = self.ds.drop_vars(['ny', 'nx'])
        # TODO add global attrs

    # just writes out the file
    def write_topog_file(self):
        if(not self.__data_is_generated):
            print("Warning: write routine called but depth data not yet generated")
        self.ds.to_netcdf(self.output_name)

    def make_topog_realistic( self,
        topog_file: str = None,
        topog_field: str = None,
        vgrid_file: str = None,
        num_filter_pass: int = None,
        kmt_min: int = None,
        min_depth: float = None,
        min_thickness: float = None,
        fraction_full_cell: float = None,
        flat_bottom: bool = None,
        fill_first_row: bool = None,
        filter_topog: bool = None,
        round_shallow: bool = None,
        fill_shallow: bool = None,
        deepen_shallow: bool = None,
        smooth_topo_allow_deepening: bool = None,
        full_cell: bool = None,
        dont_fill_isolated_cells: bool = None,
        on_grid: bool = None,
        dont_change_landmask: bool = None,
        dont_adjust_topo: bool = None,
        dont_open_very_this_cell: bool = None):
        pass

    def make_rectangular_basin(self, bottom_depth: float = None):
        pass

    def make_topog_gaussian(self,
        gauss_scale: float = None,
        gauss_amp: float = None,
        slope_x: float = None,
        slope_y: float = None):
        pass

    def make_topog_bowl(self,
        bottom_depth: float = None,
        min_depth: float = None,
        bowl_south: float = None,
        bowl_north: float = None,
        bowl_west: float = None,
        bowl_east: float = None):
        pass

    def make_topog_box_idealized(self,
        bottom_depth: float = None,
        min_depth: float = None):
        pass

    def make_topog_box_channel(self,
        jwest_south: int = None,
        jwest_north: int = None,
        ieast_south: int = None,
        ieast_north: int = None,
        bottom_depth: float = None):
        pass

    def make_topog_dome(self,
        dome_slope: float = None,
        dome_bottom: float = None,
        dome_embayment_west: float = None,
        dome_embayment_east: float = None,
        dome_embayment_south: float = None,
        dome_embayment_depth: float = None):
        pass
