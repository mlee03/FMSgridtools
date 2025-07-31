import numpy as np
import xarray as xr 

adir = "./FRE-NCTools/Test03-output/"

thesefiles = {}
for itile in range(1,7):
  name = f"C48_mosaic_tile{itile}Xocean_mosaic_tile1.nc"
  thesefiles[f"{name}"] = f"{adir}{name}"

for itile in range(1,7):
  name = f"C48_mosaic_tile{itile}XC48_mosaic_tile{itile}.nc"
  thesefiles[f"{name}"] = f"{adir}{name}"

for ikey in thesefiles:
  testme = xr.load_dataset(ikey)
  answer = xr.load_dataset(thesefiles[ikey])
  print(ikey)
  
  for i in range(testme.sizes["nxcells"]):
    if testme["src_ij"][i][0] != answer["tile1_cell"][i][0]: print(i, testme["src_ij"][i], testme["tile1_cell"][i])
    if testme["tgt_ij"][i][1] != answer["tile2_cell"][i][1]: print(i, testme["src_ij"][i], testme["tile1_cell"][i])    
  
  print("tgt_ij", np.all(testme["tgt_ij"].values == answer["tile2_cell"].values))
  print("src_ij", np.all(testme["src_ij"].values == answer["tile1_cell"].values))

  thismax = np.absolute(testme['xarea'].values - answer['xgrid_area'].values)
  print('xarea', np.max(thismax))

print()

#test mask
testme = xr.load_dataset("ocean_mask.nc")
answer = xr.load_dataset(f"{adir}ocean_mask.nc")

#ocn mask
for key in ["mask", "areaO", "areaX"]:
  answer_max = np.max(answer[key].values)
  diff = np.max(np.absolute(testme[key].values - answer[key].values))
  print(key, answer_max, diff, diff/answer_max)

  
print()

  
#lnd mask
for itile in range(1,7):
  name = f"land_mask_tile{itile}.nc"
  testme = xr.load_dataset(name)
  answer = xr.load_dataset(f"{adir}{name}")

  for key in ["mask", "area_atm", "area_lnd", "l_area"]:
    answer_max = np.max(answer[key].values)
    diff = np.max(np.absolute(testme[key].values - answer[key].values))
    print(key, answer_max, diff, diff/answer_max)

    
  

  
