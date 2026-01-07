"""
test functionalities in xgridobj
"""

from types import SimpleNamespace

import numpy as np

import pyfms
import fmsgridtools

src = SimpleNamespace(
    ntiles=6,
    nx=12,
    ny=24,
    dxy=1.0,
    mosaicfile="src_mosaic.nc",
    gridfile="src_grid"
)
tgt = SimpleNamespace(
    ntiles=1,
    nx=src.nx * 2,
    ny=src.ny * 2,
    dxy=src.dxy / 2.0,
    mosaicfile="tgt_mosaic.nc",
    gridfile="tgt_grid"
)

nxgrid_per_tile = tgt.nx//2 * tgt.ny//2
nxgrid = nxgrid_per_tile * 6
remapfile = "test_remap.nc"

def make_testfiles():

    """
    make mosaic and grid files for testing
    """

<<<<<<< HEAD
    # write mosaic
    for parent in [src, tgt]:
        fmsgridtools.MosaicObj(
            gridtiles=[f"tile{i}" for i in range(1, parent.ntiles+1)],
            gridfiles=[f"{parent.gridfile}.tile{i}.nc" for i in range(1, parent.ntiles+1)]
        ).write(parent.mosaicfile)
=======
    x_tgt = np.linspace(xstart, xend, nx*refine+1)
    y_tgt = np.linspace(ystart, yend, ny*refine+1)
    x_tgt, y_tgt = np.meshgrid(x_tgt, y_tgt)

    area_src = np.ones((ny, nx), dtype=np.float64)
    area_tgt = np.ones((ny*refine, nx*refine), dtype=np.float64)
>>>>>>> origin/main

    # write grid
    for parent in [src, tgt]:
        for itile in range(1, parent.ntiles+1):
            x1 = np.array([i*parent.dxy for i in range(parent.nx+1)], dtype=np.float64)
            y1 = np.array([j*parent.dxy for j in range(parent.ny+1)], dtype=np.float64)
            x, y = np.meshgrid(x1, y1)
            fmsgridtools.GridObj(x=x, y=y).write(parent.gridfile + f".tile{itile}.nc")


#@pytest.mark.parametrize("on_gpu", [False, True])
def xgridobj_test(on_gpu: bool = False):

    """
    tests generating the exchange grid
    tests reading and write exchange grid
    """

    pyfms.fms.init(ndomain=None if on_gpu else 4)
    pyfms.horiz_interp.init(ninterp=src.ntiles*2)

    if on_gpu:
        domain = None
    else:
        domain = pyfms.mpp_domains.define_domains([0, tgt.nx-1, 0, tgt.ny-1])

    if pyfms.mpp.pe() == pyfms.mpp.root_pe():
        make_testfiles()
    pyfms.mpp.sync()

    xgrid = fmsgridtools.XGridObj(
        src_mosaicfile=src.mosaicfile,
        tgt_mosaicfile=tgt.mosaicfile,
        domain=domain,
    )
<<<<<<< HEAD
    xgrid.set_target_tile("tile1")
    xgrid.get_interp(on_gpu=on_gpu)
    xgrid.write(outfile=remapfile)
        
    del xgrid
=======
    xgrid.create_xgrid()
    xgrid.to_dataset()
    xgrid.dataset["tile1"]["tile1"].to_netcdf("remap.nc")

    del xgrid

    xgrid = fmsgridtools.XGridObj(restart_remap_file="remap.nc")
>>>>>>> origin/main

    xgrid = fmsgridtools.XGridObj(
        src_mosaicfile=src.mosaicfile,
        tgt_mosaicfile=tgt.mosaicfile,
        remapfile=remapfile,
        tgt_tile = "tile1")    
    xgrid.read(remapfile=remapfile)

    #answers
    area = fmsgridtools.GridObj(
        gridfile=tgt.gridfile + ".tile1.nc").read(center=True, radians=True).get_fms_area()

<<<<<<< HEAD
    for tile in xgrid.interps:
=======
    src_i = [xgrid.src_cell[i][0] for i in range(nxcells)]
    src_j = [xgrid.src_cell[i][1] for i in range(nxcells)]

    assert src_i == answer_i
    assert src_j == answer_j
>>>>>>> origin/main

        interp = xgrid.interps[tile]
        i_src = interp.i_src
        j_src = interp.j_src
        i_dst = interp.i_dst
        j_dst = interp.j_dst

<<<<<<< HEAD
        assert interp.nxgrid == tgt.nx//2 * tgt.ny//2, f"src_tile = {tile}, {interp.nxgrid}"
=======
    answer_j = []
    for j in range(ny):
        for i in range(nx):
            for ixcell in range(refine):
                answer_j += [j*refine + ixcell + 1]*refine

    tgt_i = [xgrid.tgt_cell[i][0] for i in range(nxcells)]
    tgt_j = [xgrid.tgt_cell[i][1] for i in range(nxcells)]
>>>>>>> origin/main

        for i in range(interp.nxgrid):

            i_d, j_d = i_dst[i], j_dst[i]
            assert i_src[i] == i_d // 2 and j_src[i] == j_d // 2, f"xcell {i}, i_src={i_src[i]}, j_src={j_src[i]} i_dst={i_d}, j_dst={j_d}"

            np.testing.assert_almost_equal(
                interp.xgrid_area[i],
                area[j_d, i_d],
                decimal=2,
                err_msg=f"tile {tile} gridpoint {i}")

    pyfms.fms.end()


def test_xgridobj_gpu():
    xgridobj_test(on_gpu=True)

def test_xgridobj_cpu():
    xgridobj_test(on_gpu=False)

if __name__ == "__main__":
    test_xgridobj_gpu()
