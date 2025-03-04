import xarray as xr
import numpy as np
import numpy.typing as npt
import dataclasses
import itertools
import ctypes

# macro value from tool_util.h
VERSION_2 = 2
# verbosity switch
debug = True

# represents topography output file created by make_topog
# contains parameters for topography generation that aren't tied to a specific topography type
# and depth values from specified topog_type algorithm once generated.
# if multiple tiles are used, the third index of depth will be the the tile number
@dataclasses.dataclass
class TopogObj():
    mosaic_filename: str = None
    output_name: str = None
    ntiles: int = None
    x_tile: dict = dataclasses.field(default_factory=dict) 
    y_tile: dict = dataclasses.field(default_factory=dict)
    nx_tile: dict = dataclasses.field(default_factory=dict) 
    ny_tile: dict = dataclasses.field(default_factory=dict)
    x_refine: int = None
    y_refine: int = None
    scale_factor: float = None
    depth_vars: dict = dataclasses.field(default_factory=dict)
    depth_vals: dict = dataclasses.field(default_factory=dict)
    dataset: xr.Dataset = None
    __data_is_generated: bool = False
    global_attrs: dict = dataclasses.field(default_factory=dict)
    dims: dict = dataclasses.field(default_factory=dict)
    num_levels: dict = dataclasses.field(default_factory=dict)

    # applies any scaling factors or refinements given 
    def __post_init__(self):
        self.depth_vars = dict()
        self.depth_attrs = dict()
        self.depth_attrs["standard_name"] = "topographic depth at T-cell centers"
        self.depth_attrs["units"] = "meters"

        # make sure nx/ny dicts are given
        if self.x_tile is None or self.y_tile is None:
            raise ValueError("No nx/ny dictionaries provided, cannot construct TopogObj")
        # get number of x/y points
        for tileName in self.x_tile.keys():
            self.nx_tile[tileName] = self.x_tile[tileName].shape[1] - 1
            self.ny_tile[tileName] = self.x_tile[tileName].shape[0] - 1

        # adjust nx/ny for refinements and scaling factor
        # TODO usage of mpp domains for indices makes this hard to adjust outside the C code
        # maybe this can done in python eventually
        #if self.x_refine is not None:
        #    print(f"updating nx for x refine value of {self.x_refine}")
        #    self.nx_tile.update((tname, int(val/self.x_refine)) for tname, val in self.nx_tile.items()) 
        #if self.y_refine is not None:
        #    print(f"updating y for y refine value of {self.y_refine}")
        #    self.ny_tile.update((tname, int(val/self.y_refine)) for tname, val in self.ny_tile.items()) 
        #if self.scale_factor is not None:
        #    print(f"updating x/y for scale factor value of {self.scale_factor}")
        #    self.nx_tile.update((tname, int(val*self.scale_factor)) for tname, val in self.nx_tile.items()) 
        #    self.ny_tile.update((tname, int(val*self.scale_factor)) for tname, val in self.ny_tile.items())

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

        # TODO this needs to be updates to add num_levels as an output variable, it will only be added if vgrid file is used

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

    # 'realistic' option requires a data file (topog_file) and the topography data's variable name (topog_field)
    # and then interpolates the read in data as depth values onto the output grid.
    # It can also take a vertical grid file as input, in which case it will also add another variable 'num_levels'
    def make_topog_realistic( self,
        x_vals_tile: dict = None,
        y_vals_tile: dict = None,
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
        open_very_this_cell: bool = None,
        grid_filenames: str = None):

        # first load the C library (this will be replaced with a different method eventually)
        frenct_lib = ctypes.cdll.LoadLibrary("./FREnctools_lib/cfrenctools/c_build/clib.so")
        # get the C functions we need and set their arg types
        generate_realistic_c = frenct_lib.create_realistic_topog_wrapper
        get_boundary_type_c = frenct_lib.get_boundary_type
        generate_realistic_c.argtypes = [ ctypes.c_int, ctypes.c_int,                        # nx_dst, ny_dst
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),                  # x_dst, y_dst
                                          ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, # vgrid_file, topog_file, topog_field
                                          ctypes.c_double, ctypes.c_int,                     # scale_factor, tripolar_grid, 
                                          ctypes.c_int, ctypes.c_int,                        # cyclic_x, cyclic_y
                                          ctypes.c_int, ctypes.c_int, ctypes.c_int,          # fill_first_row, filter_topog, num_filter_pass
                                          ctypes.c_int, ctypes.c_int, ctypes.c_int,          # smooth_topo_allow_deepening, round_shallow, fill_shallow
                                          ctypes.c_int, ctypes.c_int, ctypes.c_int,          # deepen_shallow, full_cell, flat_bottom,
                                          ctypes.c_int, ctypes.c_int, ctypes.c_int,          # adjust_topo, fill_isolated_cells, dont_change_landmask
                                          ctypes.c_int, ctypes.c_double, ctypes.c_int,       # kmt_min, min_thickness, open_very_this_cell,
                                          ctypes.c_double, ctypes.c_void_p, ctypes.c_void_p, # fraction_full_cell, depth, num_levels
                                          ctypes.c_int, ctypes.c_int,                        # debug, use_great_circle_algo 
                                          ctypes.c_int, ctypes.c_int, ctypes.c_int,          # on_grid, x_refine, y_refine
                                          ctypes.c_char_p ]                                  # tile_names
        get_boundary_type_c.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int),
                                        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
                                          
        # TODO (done in c for now)
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
        #check_file_is_there(topog_file) todo import error
        if topog_field is None:
            raise ValueError("No argument given for topog_field")

        # set boundary type arguments based on the mosaic 
        cyclic_x = ctypes.c_int(0)
        cyclic_y = ctypes.c_int(0)
        tripolar_grid = ctypes.c_int(0)
        get_boundary_type_c(self.mosaic_filename.encode('utf-8'), VERSION_2, ctypes.byref(cyclic_x), ctypes.byref(cyclic_y),
                            ctypes.byref(tripolar_grid))
        if(debug):
            print(f"boundary type vals: {cyclic_x} {cyclic_y} {tripolar_grid}")

        # TODO check if using great circle algorithm in all grid files
        
        # generate data for each tile
        self.depth_vals = {}
        i = 0
        for tileName in list(self.nx_tile.keys()):
            # create temp array for depth output 
            _depth_temp = np.zeros( (self.ny_tile[tileName], self.nx_tile[tileName]) )
            # number of grid points
            _nx_dst = self.nx_tile[tileName]
            _ny_dst = self.ny_tile[tileName]
            # get x/y values from grid objs
            _x_dst = self.x_tile[tileName] 
            _y_dst = self.y_tile[tileName] 
            # set by 'get_boundary_type' call above
            _tripolar_grid = tripolar_grid 
            _cyclic_x = cyclic_x
            _cyclic_y = cyclic_y
            # passed in flags (convert to ints) 
            _fill_first_row = bool_to_int(fill_first_row)
            _filter_topog = bool_to_int(filter_topog)
            _num_filter_pass = bool_to_int(num_filter_pass)
            _smooth_topo_allow_deepening = bool_to_int(smooth_topo_allow_deepening)
            _round_shallow = bool_to_int(round_shallow)
            _fill_shadow = bool_to_int(fill_shallow)
            _deepen_shallow = bool_to_int(deepen_shallow)
            _full_cell = bool_to_int(full_cell)
            _flat_bottom = bool_to_int(flat_bottom)
            _dont_adjust_topo = bool_to_int(dont_adjust_topo)
            _dont_fill_isolated_cells = bool_to_int(dont_fill_isolated_cells)
            _dont_change_landmask = bool_to_int(dont_change_landmask)
            _open_very_this_cell = bool_to_int(open_very_this_cell)
            _on_grid = bool_to_int(on_grid)
            # anything else
            _kmt_min = 0 if kmt_min is None else kmt_min
            _min_thickness = 0 if min_thickness is None else min_thickness
            _fraction_full_cell = fraction_full_cell # double
            _debug = bool_to_int(True)
            _vgrid_file = None if vgrid_file is None else vgrid_file.encode('utf-8')
            # get the name of the grid file for the current tile
            _grid_filename = grid_filenames[i].encode('utf-8') 
            i = i + 1
            # TODO might be able to get rid of this as an arg
            # this should be determined by the grid files 
            _use_great_circle_algorithm = bool_to_int(False)
            # init return values for output arrays
            _depth = np.zeros( (int(_ny_dst/self.y_refine), int(_nx_dst/self.x_refine)) )
            _num_levels = np.zeros( (int(_ny_dst/self.y_refine), int(_nx_dst/self.x_refine)), dtype=int)

            print(f"Calling generate_realistic with nx: {self.nx_tile[tileName]}, ny: {self.ny_tile[tileName]}")
            generate_realistic_c( _nx_dst, _ny_dst,
                                  _x_dst.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
                                  _y_dst.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
                                  _vgrid_file, topog_file.encode('utf-8'), topog_field.encode('utf-8'),
                                  self.scale_factor,
                                  _tripolar_grid, _cyclic_x, _cyclic_y,
                                  _fill_first_row, _filter_topog, _num_filter_pass,
                                  _smooth_topo_allow_deepening, _round_shallow, _fill_shadow,
                                  _deepen_shallow, _full_cell, _flat_bottom,
                                  _dont_adjust_topo, _dont_fill_isolated_cells, _dont_change_landmask,
                                  _kmt_min, _min_thickness, _open_very_this_cell,
                                  _fraction_full_cell, _depth.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                  _num_levels.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
                                   _debug, _use_great_circle_algorithm, on_grid, self.x_refine, self.y_refine,
                                   _grid_filename)
                
            self.depth_vals[f"depth_{tileName}"] = _depth 
        self.__data_is_generated = True

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
    

def bool_to_int(bool_val):
    if(bool_val):
        return 1
    else:
        return 0