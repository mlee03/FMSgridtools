import ctypes
import numpy as np
from typing import List
import xarray as xr

import pyfrenctools
from fmsgridtools.shared.mosaicobj import MosaicObj
from fmsgridtools.shared.xgridobj import XGridObj
from fmsgridtools.shared.gridobj import GridObj


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
        

def get_ocn_mask(ocn_mosaic: type(MosaicObj), topog_file: dict() = None, sea_level: type(np.float64) = np.float64(0.0)):

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


def get_atmxlnd(atmxocn_landpart: type[XGridObj], atm_mosaic: type[MosaicObj] = None, atm_area = None):
    
    for otile in atmxocn_landpart.datadict:

        atmxlnd = {}

        for atmtile in atmxocn_landpart.datadict[otile]:
            
            #get atm area
            nx, ny = atm_mosaic.grid[atmtile].nx, atm_mosaic.grid[atmtile].ny
            atm_area = pyfrenctools.grid_utils.get_grid_area(atm_mosaic.grid[atmtile].x,
                                                             atm_mosaic.grid[atmtile].y).reshape(ny, nx)

            lnd_x_area = np.zeros((ny,nx), dtype=np.float64)
            
            datadict = atmxocn_landpart.datadict[otile][atmtile]            

            i_before, j_before = -99, -99
            atm_i, atm_j, xarea = [], [], []

            for ij in range(datadict["nxcells"]):
            
                this_i = datadict["src_i"][ij]
                this_j = datadict["src_j"][ij]
                this_xarea = datadict["xarea"][ij]
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
            atmxlnd[atmtile] = dict(nxcells = nxcells,
                                    src_i = np.array(atm_i),
                                    src_j = np.array(atm_j),
                                    tgt_i = np.array(atm_i),
                                    tgt_j = np.array(atm_j),
                                    xarea = np.array(xarea, dtype=np.float64))


            #get mask
            i, j = atm_i, atm_j
            for ix in range(nxcells): lnd_x_area[j[ix]][i[ix]] += xarea[ix]

            mask = lnd_x_area / atm_area

            mask = xr.DataArray(mask,
                                dims=["ny", "nx"],
                                attrs={"standard_name": "land fraction at T-cell centers"}
            )
            area_atm = xr.DataArray(atm_area,
                                    dims=["ny", "nx"],
                                    attrs={"standard_name": "area atm"}
            )
            area_lnd = xr.DataArray(atm_area,
                                    dims=["ny", "nx"],
                                    attrs={"standard_name": "area atm"}
            )
            l_area = xr.DataArray(lnd_x_area,
                                  dims=["ny", "nx"],
                                  attrs={"standard_name": "land x area"}
            )            
            xr.Dataset(data_vars={"mask":mask,
                                  "area_atm":area_atm,
                                  "area_lnd":area_atm,
                                  "l_area":l_area}).to_netcdf(f"land_mask_{atmtile}.nc")

    return atmxlnd
    

def write_ocn_mask(ocn_mosaic, atmxocn):

    for ocntile in atmxocn.datadict:
        
        ocn_nlon = ocn_mosaic.grid[ocntile].nx
        ocn_nlat = ocn_mosaic.grid[ocntile].ny
        
        ocn_area = pyfrenctools.grid_utils.get_grid_area(ocn_mosaic.grid[ocntile].x,
                                                         ocn_mosaic.grid[ocntile].y).reshape(ocn_nlat, ocn_nlon)

        ocn_x_area = np.zeros((ocn_nlat,ocn_nlon), dtype=np.float64)
        
        for atmtile in atmxocn.datadict[ocntile]:

            xgrid = atmxocn.datadict[ocntile][atmtile]
            nxcells = xgrid["nxcells"]

            i, j = xgrid["tgt_i"], xgrid["tgt_j"]

            for ix in range(nxcells): ocn_x_area[j[ix]][i[ix]] += xgrid["xarea"][ix]
            
        xgrid["ocn_mask"] = ocn_x_area/ocn_area
            
        mask = xr.DataArray(xgrid["ocn_mask"],
                            dims=["ny", "nx"],
                            attrs={"standard_name": "ocean fraction at T-cell centers"}
        )

        areaO = xr.DataArray(ocn_area,
                             dims=["ny", "nx"],
                             attrs={"standard_name": "ocean grid area"}
        )
        
        areaX = xr.DataArray(ocn_x_area,
                             dims=["ny", "nx"],
                             attrs={"standard_name": "ocean exchange grid area"}
        )
        xr.Dataset(data_vars={"mask": mask, "areaO": areaO, "areaX": areaX}).to_netcdf("ocean_mask.nc")



def make_coupler_mosaic(atm_mosaic_file: str, lnd_mosaic_file: str, ocn_mosaic_file: str,
                        input_dir: str = './', topog_file: dict() = None):

    #read in mosaic files
    atm_mosaic = MosaicObj(input_dir=input_dir, mosaic_name=atm_mosaic_file).read()
    lnd_mosaic = MosaicObj(input_dir=input_dir, mosaic_name=lnd_mosaic_file).read()
    ocn_mosaic = MosaicObj(input_dir=input_dir, mosaic_name=ocn_mosaic_file).read()

    #read in grids
    atm_mosaic.get_grid(toradians=True, agrid=True, free_dataset=True)
    lnd_mosaic.get_grid(toradians=True, agrid=True, free_dataset=True)
    ocn_mosaic.get_grid(toradians=True, agrid=True, free_dataset=True)
    
    #get ocean mask
    topogfile_dict = {'tile1': input_dir + '/' + topog_file}
    extended_grid = extend_ocn_grid_south(ocn_mosaic)    
    ocn_mask = get_ocn_mask(ocn_mosaic=ocn_mosaic, topog_file=topogfile_dict)

    #atmxocn
    atmxocn = XGridObj(src_grid=atm_mosaic.grid, tgt_grid=extended_grid)
    atmxocn.create_xgrid(tgt_mask=ocn_mask)

    #undo extra ocn dimension
    for ocntile in atmxocn.datadict:
        for atmtile in atmxocn.datadict[ocntile]:
            atmxocn.datadict[ocntile][atmtile]['tgt_j'] -= ocn_mosaic.extended_south
    
    #write
    for ocntile in atmxocn.datadict:
        tmpdict = {}
        for atmtile in atmxocn.datadict[ocntile]:
            tmpdict[ocntile] = {}
            tmpdict[ocntile][atmtile] = atmxocn.datadict[ocntile][atmtile]
            outfile = f"{atm_mosaic.mosaic_name[:-3]}_{atmtile}X{ocn_mosaic.mosaic_name[:-3]}_{ocntile}.nc"
            atmxocn.write(datadict=tmpdict, outfile=outfile)

    #ocn mask for lnd    
    for itile in ocn_mask: ocn_mask[itile] = 1.0 - ocn_mask[itile]

    #atmxocn the land part 
    atmxocn_landpart = XGridObj(src_grid=atm_mosaic.grid, tgt_grid=extended_grid)
    atmxocn_landpart.create_xgrid(tgt_mask=ocn_mask)
    
    #atmxlnd
    atmxlnd = get_atmxlnd(atmxocn_landpart, atm_mosaic=atm_mosaic)
    for atmtile in atmxlnd:
        tmpdict = {atmtile:{atmtile:atmxlnd[atmtile]}}
        outfile = f"{atm_mosaic.mosaic_name[:-3]}_{atmtile}X{atm_mosaic.mosaic_name[:-3]}_{atmtile}.nc"
        atmxocn.write(datadict=tmpdict, outfile=outfile)


    write_ocn_mask(ocn_mosaic, atmxocn)
