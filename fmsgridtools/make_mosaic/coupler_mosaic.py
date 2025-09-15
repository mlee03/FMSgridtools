import ctypes
import numpy as np
from typing import List
import xarray as xr

import pyfrenctools
from fmsgridtools.shared.mosaicobj import MosaicObj
from fmsgridtools.shared.xgridobj import XGridObj
from fmsgridtools.shared.gridobj import GridObj

sea_level = np.float64(1.0)
area_ratio_thresh = np.float64(1.e-12)
interp_order = "conserve_order1"
rotate_poly = False

def set_parameters(sea_level_in: np.float64 = None,
                   area_ratio_thresh_in: np.float64 = None,
                   interp_order_in: str = "conserve_order1",
                   rotate_poly_in: bool = False):

    global sea_level, area_ratio_thresh, interp_order, rotate_poly

    if sea_level_in is not None: sea_level = sea_level_in
    if area_ratio_thresh is not None: area_ratio_thresh = area_ratio_thresh_in
    if interp_order_in is not None: interp_order = interp_order_in
    if rotate_poly_in is not None: rotate_poly = rotate_poly_in
    

def extend_ocn_grid_south(ocn_mosaic: MosaicObj):

    tiny_value = np.float64(1.e-7)
    min_atm_lat = np.radians(-90.0, dtype=np.float64)

    extended_grid = {}
    
    if ocn_mosaic.grid['tile1'].y[0][0] > min_atm_lat + tiny_value:
        #extend
        for itile in ocn_mosaic.gridtiles:

            extended_grid[itile] = GridObj()
            
            nxp = ocn_mosaic.grid[itile].nxp
            x = ocn_mosaic.grid[itile].x
            y = ocn_mosaic.grid[itile].y
            
            extended_grid[itile].x = np.concatenate(([x[0]], x))
            extended_grid[itile].y = np.concatenate((np.full((1,nxp), min_atm_lat, dtype=np.float64), y))

            extended_grid[itile].nx = ocn_mosaic.grid[itile].nx
            extended_grid[itile].ny = ocn_mosaic.grid[itile].ny + 1
        ocn_mosaic.extended_south = 1
    else:
        ocn_mosaic.extended_south = 0

    return extended_grid
        

def get_ocn_mask(ocn_mosaic: type(MosaicObj), topog_file: dict() = None):

    nx = ocn_mosaic.grid['tile1'].nx 
    ny = ocn_mosaic.grid['tile1'].ny

    ocn_mask = {}
    if topog_file is None:
        for itile in ocn_mosaic.gridtiles:
            ocn_mask[itile] = np.ones((ny,nx), dtype=np.float64)
        return mask    

    for itile in ocn_mosaic.gridtiles:
        topog = xr.load_dataset(topog_file[itile])['depth'].values

        one, zero = np.float64(1.0), np.float64(0.0)
        imask = np.where(topog>sea_level, one, zero)
            
        if ocn_mosaic.extended_south > 0 :
            ocn_mask[itile] = np.concatenate(([np.zeros(nx, dtype=np.float64)], imask))
        else:
            ocn_mask[itile] = imask

    return ocn_mask


def write_ocn_mask(ocn_mosaic, atmxocn):

    for ocntile in atmxocn.datadict:
        
        ocn_nlon, ocn_nlat = ocn_mosaic.grid[ocntile].nx, ocn_mosaic.grid[ocntile].ny
        
        ocn_area = pyfrenctools.grid_utils.get_grid_area(ocn_mosaic.grid[ocntile].x,
                                                         ocn_mosaic.grid[ocntile].y).reshape(ocn_nlat, ocn_nlon)

        ocn_x_area = np.zeros((ocn_nlat,ocn_nlon), dtype=np.float64)
        
        for atmtile in atmxocn.datadict[ocntile]:

            xgrid = atmxocn.datadict[ocntile][atmtile]
            nxcells = xgrid["nxcells"]

            i, j = xgrid["tgt_i"], xgrid["tgt_j"]
            for ix in range(nxcells): ocn_x_area[j[ix]][i[ix]] += xgrid["xarea"][ix]

        mask = xr.Dataset()
        mask["mask"] = xr.DataArray(ocn_x_area/ocn_area,
                                    dims=["ny", "nx"],
                                    attrs={"standard_name": "ocean fraction at T-cell centers"}
        )
        mask["areaO"] = xr.DataArray(ocn_area,
                                     dims=["ny", "nx"],
                                     attrs={"standard_name": "ocean grid area"}
        )        
        mask["areaX"] = xr.DataArray(ocn_x_area,
                                     dims=["ny", "nx"],
                                     attrs={"standard_name": "ocean exchange grid area"}
        )
        mask.to_netcdf("ocean_mask.nc")

        
def write_lnd_mask(atm_area, atmxlnd, itile):

    #get mask
    i, j, xarea = atmxlnd["src_i"], atmxlnd["src_j"], atmxlnd["xarea"]
    lnd_x_area = np.zeros(atm_area.shape, dtype=np.float64)
    for ix in range(atmxlnd["nxcells"]): lnd_x_area[j[ix]][i[ix]] += xarea[ix]

    mask = xr.Dataset()
    
    mask["mask"] = xr.DataArray(lnd_x_area/atm_area,
                                dims=["ny", "nx"],
                                attrs={"standard_name": "land fraction at T-cell centers"}
    )
    mask["area_atm"] = xr.DataArray(atm_area,
                                    dims=["ny", "nx"],
                                    attrs={"standard_name": "area atm"}
    )
    mask["area_lnd"] = xr.DataArray(atm_area,
                                    dims=["ny", "nx"],
                                    attrs={"standard_name": "area atm"}
    )
    mask["l_area"] = xr.DataArray(lnd_x_area,
                                  dims=["ny", "nx"],
                                  attrs={"standard_name": "land x area"}
    )
    mask.to_netcdf(f"land_mask_{itile}.nc")
        

def get_atmxlnd(atmxocn_landpart: type[XGridObj], atm_mosaic: type[MosaicObj] = None, atm_area = None):
    
    for otile in atmxocn_landpart.datadict:

        atmxlnd = {}

        for atmtile in atmxocn_landpart.datadict[otile]:

            atmxlnd[atmtile] = {}
            datadict = atmxocn_landpart.datadict[otile][atmtile]

            #get atm area
            nx, ny = atm_mosaic.grid[atmtile].nx, atm_mosaic.grid[atmtile].ny
            atm_area = pyfrenctools.grid_utils.get_grid_area(atm_mosaic.grid[atmtile].x,
                                                             atm_mosaic.grid[atmtile].y).reshape(ny, nx)
            i_before, j_before = -99, -99
            atm_i, atm_j, xarea = [], [], []

            for ij in range(datadict["nxcells"]):
            
                this_i, this_j, this_xarea = datadict["src_i"][ij], datadict["src_j"][ij], datadict["xarea"][ij]
                this_atm_area = atm_area[this_j][this_i]

                if this_xarea/this_atm_area > np.float64(1.e-6):  
                    if this_i == i_before and this_j == j_before:                    
                        xarea[-1] += this_xarea
                    else:
                        i_before, j_before = this_i, this_j
                        xarea.append(this_xarea)
                        atm_i.append(this_i)
                        atm_j.append(this_j)

            nxcells = len(atm_i)
            atmxlnd[atmtile] = {atmtile: dict(nxcells = len(atm_i),
                                              src_i = np.array(atm_i),
                                              src_j = np.array(atm_j),
                                              tgt_i = np.array(atm_i),
                                              tgt_j = np.array(atm_j),
                                              xarea = np.array(xarea, dtype=np.float64))
            }

            write_lnd_mask(atm_area, atmxlnd[atmtile][atmtile], atmtile)

    return XGridObj(datadict=atmxlnd)
    

def make(atm_mosaic_file: str, lnd_mosaic_file: str, ocn_mosaic_file: str,
         topog_file: str, input_dir: str = "./", on_gpu: bool = False):    
    
    #read in mosaic files
    atm_mosaic = MosaicObj(input_dir=input_dir, mosaic_file=atm_mosaic_file).read()
    lnd_mosaic = MosaicObj(input_dir=input_dir, mosaic_file=lnd_mosaic_file).read()
    ocn_mosaic = MosaicObj(input_dir=input_dir, mosaic_file=ocn_mosaic_file).read()

    #read in grids
    atm_mosaic.get_grid(toradians=True, agrid=True, free_dataset=True)
    lnd_mosaic.get_grid(toradians=True, agrid=True, free_dataset=True)
    ocn_mosaic.get_grid(toradians=True, agrid=True, free_dataset=True)
    
    #get ocean mask
    topogfile_dict = {'tile1': input_dir + '/' + topog_file}
    extended_grid = extend_ocn_grid_south(ocn_mosaic)    
    ocn_mask = get_ocn_mask(ocn_mosaic=ocn_mosaic, topog_file=topogfile_dict)

    #atmxocn
    atmxocn = XGridObj(src_grid=atm_mosaic.grid, tgt_grid=extended_grid, on_gpu=on_gpu)
    atmxocn.create_xgrid(tgt_mask=ocn_mask)

    #undo extra ocn dimension
    for ocntile in atmxocn.datadict:
        for atmtile in atmxocn.datadict[ocntile]:
            atmxocn.datadict[ocntile][atmtile]['tgt_j'] -= ocn_mosaic.extended_south

    #ocn mask for lnd    
    for itile in ocn_mask: ocn_mask[itile] = np.float64(1.0) - ocn_mask[itile]
            
    #atmxocn the land part 
    atmxocn_landpart = XGridObj(src_grid=atm_mosaic.grid, tgt_grid=extended_grid, on_gpu=on_gpu)
    atmxocn_landpart.create_xgrid(tgt_mask=ocn_mask)
    atmxlnd = get_atmxlnd(atmxocn_landpart, atm_mosaic=atm_mosaic)
            
    #write
    contact_attrs = {"standard_name": "grid_contact_spec",
                     "contact_type": "exchange",
                     "parent1_cell": "src_ij",
                     "parent2_cell": "tgt_ij",
                     "xgrid_area": "xarea",
                     "distance_to_parent1_centroid": "tile1_distance",
                     "distance_to_parent2_centroid": "tile2_distance"
    }

    #write atmxocn
    atmxocn.to_dataset()
    for ocntile in atmxocn.dataset:
        for atmtile in atmxocn.dataset[ocntile]:
            dataset = atmxocn.dataset[ocntile][atmtile]
            dataset["contact"] = xr.DataArray(f"{atm_mosaic.name}:{atmtile}::{ocn_mosaic.name}:{ocntile}",
                                              attrs=contact_attrs
            )
            print(f"{atm_mosaic.name}_{atmtile}X{ocn_mosaic.name}_{ocntile}.nc")
            dataset.to_netcdf(f"{atm_mosaic.name}_{atmtile}X{ocn_mosaic.name}_{ocntile}.nc")
    write_ocn_mask(ocn_mosaic, atmxocn)
    
    #write atmxlnd
    atmxlnd.to_dataset()    
    for atmtile in atmxlnd.dataset:
        dataset = atmxlnd.dataset[atmtile][atmtile]
        dataset["contact"] = xr.DataArray(f"atm_mosaic:{atmtile}::atm_mosaic:{atmtile}",
                                          attrs=contact_attrs
        )
        dataset.to_netcdf(f"{atm_mosaic.name}_{atmtile}X{lnd_mosaic.mosaic}_{atmtile}.nc")


