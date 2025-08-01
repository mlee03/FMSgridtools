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

  print("tgt_cell", np.all(testme["tgt_cell"].values == answer["tile2_cell"].values))
  print("src_cell", np.all(testme["src_cell"].values == answer["tile1_cell"].values))
  print("contacts", testme["contact"].values == answer["contact"].values)
  
  thismax = np.absolute(testme['xarea'].values - answer['xgrid_area'].values)
  print('max xarea diff', np.max(thismax), np.max(answer["xgrid_area"].values))
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
  print()

    
  
 
  
