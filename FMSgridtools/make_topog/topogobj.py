from typing import List
import xarray as xr
import numpy as np
import numpy.typing as npt
import dataclasses
import itertools

# represents topography output file created by make_topog
# contains parameters for topography generation that aren't tied to a specific topography type
# and depth values from specified topog_type algorithm once generated.
# if multiple tiles are used, the third index of depth will be the the tile number
@dataclasses.dataclass
class TopogObj():
    output_name: str = None
    ntiles: int = None
    nx: dict = dataclasses.field(default_factory=dict) 
    ny: dict = dataclasses.field(default_factory=dict)
    x_refine: int = None
    y_refine: int = None
    scale_factor: float = None
    depth_vars: dict = dataclasses.field(default_factory=dict)
    depth_vals: dict = dataclasses.field(default_factory=dict)
    dataset: xr.Dataset = None
    __data_is_generated: bool = False
    global_attrs: dict = dataclasses.field(default_factory=dict)
    dims: dict = dataclasses.field(default_factory=dict)

    # applies any scaling factors or refinements given 
    def __post_init__(self):
        self.depth_vars = dict()
        self.depth_attrs = dict()
        self.depth_attrs["standard_name"] = "topographic depth at T-cell centers"
        self.depth_attrs["units"] = "meters"

        # make sure nx/ny dicts are given
        if self.nx is None or self.ny is None:
            raise ValueError("No nx/ny dictionaries provided, cannot construct TopogObj")

        # adjust nx/ny for refinements and scaling factor
        if self.x_refine is not None:
            print(f"updating nx for x refine value of {self.x_refine}")
            self.nx.update((tname, val/self.x_refine) for tname, val in self.nx.items()) 
        if self.y_refine is not None:
            print(f"updating ny for y refine value of {self.y_refine}")
            self.ny.update((tname, val/self.y_refine) for tname, val in self.ny.items()) 
        if self.scale_factor is not None:
            print(f"updating nx/ny for scale factor value of {self.scale_factor}")
            self.nx.update((tname, val*self.scale_factor) for tname, val in self.nx.items()) 
            self.ny.update((tname, val*self.scale_factor) for tname, val in self.ny.items()) 

        # set up coordinates and dimensions based off tile count and nx/ny values
        # if single tile exclude tile number in variable name
        if self.ntiles == 1:
            self.dims = ['ny', 'nx']
        # loop through ntiles and add depth_tile<n> variable for each
        else:
            self.dims = []
            for i in range(1,self.ntiles+1):
                self.dims.append("ny_tile"+str(i))
                self.dims.append("nx_tile"+str(i))

    # writes out the file
    def write_topog_file(self):
        if(not self.__data_is_generated):
            print("Warning: write routine called but depth data not yet generated")

        # create xarray DataArrays for each output variable
        # single tile
        if self.ntiles == 1:
            self.depth_vars['depth'] = xr.DataArray(
                data = self.depth_vals['depth_tile1'],
                dims = self.dims,
                attrs = self.depth_attrs)
        # multi-tile 
        else:
            for i in range(1,self.ntiles+1):
                self.depth_vars['depth_tile'+str(i)] = xr.DataArray(
                    data = self.depth_vals['depth_tile'+str(i)], 
                    dims = self.dims[(i-1)*2:(i-1)*2+2],
                    attrs = self.depth_attrs)

        # create dataset (this excludes ntiles, since it is not used in a variable)
        self.dataset = xr.Dataset( data_vars=self.depth_vars )
        
        # add any global attributes
        if self.global_attrs is not None:
            self.dataset.attrs = self.global_attrs
        # write to file
        self.dataset.to_netcdf(self.output_name)

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
        self.depth_vals = {}
        for tileName in list(self.nx.keys()):
            self.depth_vals[f"depth_{tileName}"] = np.full( (int(self.ny[tileName]), int(self.nx[tileName])), bottom_depth)
        self.__data_is_generated = True


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
