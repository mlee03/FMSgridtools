import pandas as pd
import xarray as xr

#testfile = "/home/Mikyung.Lee/FRE-NCTools/DONOTDELETEME_DATA/TESTS/TESTS_INPUT/Testa-input/00010101.atmos_month_aer.tile1.nc"
# with xr.open_dataset(testfile, decode_cf=False) as dataset:
#     for coord in dataset.coords:
#         print(dataset[coord].attrs.get("axis"))
#         print(dataset[coord].size)
#         exit()

ntimes = 4
nz = 5
ny = 3
nx = 2
for time in range(ntimes):
    for z in range(nz):
        this = np.zeros((ny, nx), dtype=np.float64)
