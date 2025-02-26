import xarray as xr
import numpy as np
import numpy.typing as npt
import dataclasses
import itertools
import ctypes

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

        # first load the C library (this will be replaced with a different method)
        frenct_lib = ctypes.cdll.LoadLibrary("./FREnctools_lib/cfrenctools/c_build/clib.so")
        # get the C function we need
        generate_realistic_c = frenct_lib.create_realistic_topog
        # TODO init pyFMS, create object, create mpp object based on shared object file
        

        
        ## py
        # void create_realistic_topog(int nx_dst, int ny_dst, const double *x_dst, const double *y_dst, const char *vgrid_file,
			    #const char* topog_file, const char* topog_field, double scale_factor,
			    #int tripolar_grid, int cyclic_x, int cyclic_y,
			    #int fill_first_row, int filter_topog, int num_filter_pass,
			    #int smooth_topo_allow_deepening, int round_shallow, int fill_shallow,
			    #int deepen_shallow, int full_cell, int flat_bottom, int adjust_topo,
			    #int fill_isolated_cells, int dont_change_landmask, int kmt_min, double min_thickness,
			    #int open_very_this_cell, double fraction_full_cell, double *depth,
			    #int *num_levels, domain2D domain, int debug, int use_great_circle_algorithm,
                #int on_grid )
        generate_realistic_c.argtypes = [ ctypes.c_int, ctypes.c_int,                        # nx_dst, ny_dst
                                          ctypes.c_void_p, ctypes.c_void_p,                  # x_dst, y_dst
                                          ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, # vgrid_file, topog_file, topog_field
                                          ctypes.c_double, ctypes.c_int,                     # scale_factor, tripolar_grid, 
                                          ctypes.c_int, ctypes.c_int,                        # cyclic_x, cyclic_y
                                          ctypes.c_int, ctypes.c_int, ctypes.c_int,          # fill_first_row, filter_topog, num_filter_pass
                                          ctypes.c_int, ctypes.c_int, ctypes.c_int,          # smooth_topo_allow_deepening, round_shallow, fill_shallow
                                          ctypes.c_int, ctypes.c_int, ctypes.c_int,          # deepen_shallow, full_cell, flat_bottom,
                                          ctypes.c_int, ctypes.c_int, ctypes.c_int,          # adjust_topo, fill_isolated_cells, dont_change_landmask
                                          ctypes.c_int, ctypes.c_double, ctypes.c_int,       # kmt_min, min_thickness, open_very_this_cell,
                                          ctypes.c_double, ctypes.c_void_p, ctypes.c_void_p, # fraction_full_cell, depth, num_levels
                                          ctypes.c_void_p, ctypes.c_int, ctypes.c_int,       # domain, debug, use_great_circle_algo 
                                          ctypes.c_int ]                                     # on_grid
                                          
        # TODO io done in C for now
        # if optional vgrid file is provided, read in the dimension and zeta values
        #if(vgrid_file is not None):
            #check_file_is_there(vgrid_file)
            #with xr.open_dataset(vgrid_file) as ds:
                #varlist = list(ds.data_vars)
                #if "zeta" in varlist:
                    #nzv = ds.zeta.shape[0]
                    #zeta = np.ascontiguousarray(ds.zeta.values)
                #else:
                    #raise ValueError("zeta argument must be present in provided vgrid file")
            #if (nzv-1)%2 == 1:
                #raise ValueError("topog: size of dimension nzv should be 2*nk+1, where nk is the number of model vertical level");
            #nk = (nzv-1)/2
            ## allocate zw[nk]
            #zw = [None] * nk 
            ## read in zeta value from file 
            ##for(k=0; k<nk; k++) zw[k] = zeta[2*(k+1)];
            #for k in range(nk):
                #zw[k] = zeta[2*(k+1)]

        ## check required arguments 
        if topog_file is None:
            raise ValueError("No argument given for topog_file") 
        check_file_is_there(topog_file)
        if topog_field is None:
            raise ValueError("No argument given for topog_field")
        
        # generate data for each tile
        self.depth_vals = {}
        for tileName in list(self.nx.keys()):
            # placeholder data for now
            self.depth_vals[f"depth_{tileName}"] = np.full( (int(self.ny[tileName]), int(self.nx[tileName])), bottom_depth)

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
