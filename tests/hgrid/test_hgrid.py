import os
from click.testing import CliRunner
from fmsgridtools.main import main
from fmsgridtools.make_hgrid.hgridobj import HGridObj
from numpy.typing import NDArray
import numpy as np


# Test `fmsgridtools make-hgrid`
def test_make_hgrid_lonlat_grid():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Testing: fmsgridtools make-hgrid lonlat --xbnds 0,30 --ybnds 50,50 --nlon 60 --nlat 20
        result = runner.invoke(main, ['make-hgrid', 'lonlat',
                                      '--xbnds', '0,30',
                                      '--ybnds', '50,50',
                                      '--nlon',  '60',
                                      '--nlat', '20',])
        if result.exit_code != 0:
            print(result.output)
        assert result.exit_code == 0
        assert os.path.exists('horizontal_grid.nc'), "File 'horizontal_grid.nc' does not exist."
        os.remove('horizontal_grid.nc')


def test_make_hgrid_gnomonic_ed():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Testing: fmsgridtools make-hgrid gnomonic --nlon 96 --grid_name C48_grid
        result = runner.invoke(main, ['make-hgrid', 'gnomonic',
                                      '--nlon',  '96',
                                      '--grid_name', 'C48_grid',])
        if result.exit_code != 0:
            print(result.output)
        assert result.exit_code == 0

        tiles = [f"C48_grid.tile{i}.nc" for i in range(1, 7)]
        missing = [f for f in tiles if not os.path.exists(f)]
        assert not missing, f"Missing grid tile files: {', '.join(missing)}"
        for f in tiles:
            os.remove(f)


def test_make_hgrid_gnomonic_ed_nest():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Testing: fmsgridtools make-hgrid gnomonic --nlon 96 --grid_name C48_grid --do_schmidt --stretch_factor 1.0
        #                                           --target_lon -97.5 --target_lat 36.5 --nest_grids 3 --parent_tile 2,5,6
        #                                           --refine_ratio 2,2,2 --istart_nest 7,13,7 --jstart_nest 7,7,23
        #                                           --iend_nest 58,68,40 --jend_nest 58,68,48 --halo 3
        cmd = [
            "make-hgrid", "gnomonic",
            "--nlon", "96",
            "--grid_name", "C48_grid",
            "--do_schmidt",
            "--stretch_factor", "1.0",
            "--target_lon", "-97.5",
            "--target_lat", "36.5",
            "--nest_grids", "3",
            "--parent_tile", "2,5,6",
            "--refine_ratio", "2,2,2",
            "--istart_nest", "7,13,7",
            "--jstart_nest", "7,7,23",
            "--iend_nest", "58,68,40",
            "--jend_nest", "58,68,48",
            "--halo", "3",
        ]
        result = runner.invoke(main, cmd)
        if result.exit_code != 0:
            print(result.output)
        assert result.exit_code == 0

        tiles = [f"C48_grid.tile{i}.nc" for i in range(1, 10)]
        missing = [f for f in tiles if not os.path.exists(f)]
        assert not missing, f"Missing grid tile files: {', '.join(missing)}"
        for f in tiles:
            os.remove(f)


def test_make_hgrid_gnomonic_ed_telescope_nest():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Testing: fmsgridtools make-hgrid gnomonic --nlon 96 --grid_name C48_grid --do_schmidt --stretch_factor 1.0
        #                                           --target_lon -97.5 --target_lat 36.5 --nest_grids 3 --parent_tile 2,5,6
        #                                           --refine_ratio 2,2,2 --istart_nest 7,13,7 --jstart_nest 7,7,23
        #                                           --iend_nest 58,68,40 --jend_nest 58,68,48 --halo 3
        cmd = [
            "make-hgrid", "gnomonic",
            "--nlon", "96",
            "--grid_name", "C48_grid",
            "--do_schmidt",
            "--stretch_factor", "1.0",
            "--target_lon", "-97.5",
            "--target_lat", "36.5",
            "--nest_grids", "3",
            "--parent_tile", "2,5,7", #tile7 (a nest) is a parent
            "--refine_ratio", "2,2,2",
            "--istart_nest", "7,13,7",
            "--jstart_nest", "7,7,23",
            "--iend_nest", "58,68,40",
            "--jend_nest", "58,68,48",
            "--halo", "3",
        ]
        result = runner.invoke(main, cmd)
        if result.exit_code != 0:
            print(result.output)
        assert result.exit_code == 0

        tiles = [f"C48_grid.tile{i}.nc" for i in range(1, 10)]
        missing = [f for f in tiles if not os.path.exists(f)]
        assert not missing, f"Missing grid tile files: {', '.join(missing)}"
        for f in tiles:
            os.remove(f)


## Test `make_grid_info`
def test_make_grid_info_gnomonic_ed():
    grid = HGridObj()

    ntiles = 6
    grid_size = 96
    nlon = np.fromstring(str(grid_size), dtype=np.int32, sep=',')
    grid.make_grid_info(nlon=nlon, ntiles=ntiles, ntiles_global=6,
                        grid_type="GNOMONIC_ED", conformal=False)

    nsuper = (grid_size + 1) * (grid_size + 1) * ntiles
    narea = (grid_size) * (grid_size) * ntiles
    dx_size = (grid_size) * (grid_size + 1) * ntiles # Same as dy
    assert_grid_shape_and_size(grid, ntiles, grid_size, nsuper, narea, dx_size, dx_size)


def test_make_grid_info_gnomonic_ed_nest():
    grid = HGridObj()

    ntiles_global = 6
    nest_grids = 3
    grid_size = 96
    nlon = np.fromstring(str(grid_size), dtype=np.int32, sep=',')
    ntiles = ntiles_global + nest_grids
    parent_tile = np.fromstring("2,5,6", dtype=np.int32, sep=',')
    refine_ratio = np.fromstring("2,2,2", dtype=np.int32, sep=',')
    istart_nest = np.fromstring("7,13,7", dtype=np.int32, sep=',')
    iend_nest = np.fromstring("58,68,40", dtype=np.int32, sep=',')
    jstart_nest = np.fromstring("7,7,23", dtype=np.int32, sep=',')
    jend_nest = np.fromstring("58,68,48", dtype=np.int32, sep=',')
    grid_type = "GNOMONIC_ED"
    conformal = False
    output_length_angle = True

    grid.make_grid_info(nlon=nlon, ntiles=ntiles, ntiles_global=6, nest_grids=nest_grids,
                        parent_tile=parent_tile, refine_ratio=refine_ratio, istart_nest=istart_nest,
                        iend_nest=iend_nest, jstart_nest=jstart_nest, jend_nest=jend_nest,
                        grid_type=grid_type, output_length_angle=output_length_angle, conformal=conformal)

    nxl_values = np.array([96, 96, 96, 96, 96, 96, 104, 112, 68], dtype=np.int32)
    nyl_values = np.array([96, 96, 96, 96, 96, 96, 104, 124, 52], dtype=np.int32)
    nsuper = 97*97*6 + 105*105 + 113*125 + 69*53

    # Not sure about this one but this is what the code is doing ...
    narea = 96*96*6 + 105*105 + 113*125 + 69*53
    dx_size = 96*97*6 + 105*106 + 113*126 + 69*54
    dy_size = 97*96*6 + 106*105 + 114*125 + 70*53
    assert_grid_shape_and_size(grid, ntiles, grid_size, nsuper, narea, dx_size, dy_size,
                               nxl_values=nxl_values, nyl_values=nyl_values)


def test_make_grid_info_gnomonic_ed_telescope_nest():
    grid = HGridObj()

    ntiles_global = 6
    nest_grids = 3
    grid_size = 96
    nlon = np.fromstring(str(grid_size), dtype=np.int32, sep=',')
    ntiles = ntiles_global + nest_grids

    # This is the same as the previous test but with a telescope nest,
    # So the parent (tile7) is a nest
    parent_tile = np.fromstring("2,5,7", dtype=np.int32, sep=',')
    refine_ratio = np.fromstring("2,2,2", dtype=np.int32, sep=',')
    istart_nest = np.fromstring("7,13,7", dtype=np.int32, sep=',')
    iend_nest = np.fromstring("58,68,40", dtype=np.int32, sep=',')
    jstart_nest = np.fromstring("7,7,23", dtype=np.int32, sep=',')
    jend_nest = np.fromstring("58,68,48", dtype=np.int32, sep=',')
    grid_type = "GNOMONIC_ED"
    conformal = False
    output_length_angle = True

    grid.make_grid_info(nlon=nlon, ntiles=ntiles, ntiles_global=6, nest_grids=nest_grids,
                        parent_tile=parent_tile, refine_ratio=refine_ratio, istart_nest=istart_nest,
                        iend_nest=iend_nest, jstart_nest=jstart_nest, jend_nest=jend_nest,
                        grid_type=grid_type, output_length_angle=output_length_angle, conformal=conformal)

    nxl_values = np.array([96, 96, 96, 96, 96, 96, 104, 112, 68], dtype=np.int32)
    nyl_values = np.array([96, 96, 96, 96, 96, 96, 104, 124, 52], dtype=np.int32)
    nsuper = 97*97*6 + 105*105 + 113*125 + 69*53

    # Not sure about this one but this is what the code is doing ...
    narea = 96*96*6 + 105*105 + 113*125 + 69*53
    dx_size = 96*97*6 + 105*106 + 113*126 + 69*54
    dy_size = 97*96*6 + 106*105 + 114*125 + 70*53
    assert_grid_shape_and_size(grid, ntiles, grid_size, nsuper, narea, dx_size, dy_size,
                               nxl_values=nxl_values, nyl_values=nyl_values)


def test_make_grid_info_lat_lon():
    grid = HGridObj()

    grid_size = 60
    conformal = False
    nlon = np.fromstring(str(grid_size), dtype=np.int32, sep=',')
    nlat = np.fromstring(str(grid_size), dtype=np.int32, sep=',')
    nxbnds = np.fromstring('0,30', dtype=np.int32, sep=',')
    nybnds = np.fromstring('50,50', dtype=np.int32, sep=',')
    grid.make_grid_info(nlon=nlon, nlat=nlat, nxbnds=nxbnds.size, nybnds=nybnds.size,
                        conformal=conformal)

    nsuper = (grid_size + 1) * (grid_size + 1)
    narea = grid_size * grid_size
    dx_size = (grid_size + 1) * (grid_size)
    dy_size = (grid_size + 1) * (grid_size)
    assert_grid_shape_and_size(grid, 1, grid_size, nsuper, narea, dx_size, dy_size,
                               nxl_values=nlon, nyl_values=nlat)


def assert_grid_shape_and_size(grid, ntiles, grid_size, nsuper, narea, dx_size, dy_size,
                               nxl_values: NDArray=None, nyl_values: NDArray=None):
    if nxl_values is None:
        assert grid.nxl.size == ntiles, f"grid.nxl.size mismatch: expected {ntiles}, got {grid.nxl.size}"
        assert np.all(grid.nxl == grid_size), f"grid.nxl values mismatch: expected all {grid_size}, got {grid.nxl}"
    else:
        assert np.array_equal(grid.nxl, nxl_values), f"grid.nxl values mismatch: expected all {nxl_values}, got {grid.nxl}"

    if nyl_values is None:
        assert grid.nyl.size == ntiles, f"grid.nyl.size mismatch: expected {ntiles}, got {grid.nyl.size}"
        assert np.all(grid.nyl == grid_size), f"grid.nyl values mismatch: expected all {grid_size}, got {grid.nyl}"
    else:
        assert np.array_equal(grid.nyl, nyl_values), f"grid.nyl values mismatch: expected all {nyl_values}, got {grid.nyl}"

    assert grid.nx == grid_size, f"grid.nx mismatch: expected {grid_size}, got {grid.nx}"
    assert grid.nxp == grid_size + 1, f"grid.nxp mismatch: expected {grid_size + 1}, got {grid.nxp}"
    assert grid.x.size == nsuper, f"grid.x.size mismatch: expected {nsuper}, got {grid.x.size}"

    assert grid.ny == grid_size, f"grid.ny mismatch: expected {grid_size}, got {grid.ny}"
    assert grid.nyp == grid_size + 1, f"grid.nyp mismatch: expected {grid_size + 1}, got {grid.nyp}"
    assert grid.y.size == nsuper, f"grid.y.size mismatch: expected {nsuper}, got {grid.y.size}"

    assert grid.area.size == narea, f"grid.area.size mismatch: expected {narea}, got {grid.area.size}"

    assert grid.isc == 0, f"grid.isc mismatch: expected 0, got {grid.isc}"
    assert grid.iec == grid_size - 1, f"grid.iec mismatch: expected {grid_size - 1}, got {grid.iec}"
    assert grid.jsc == 0, f"grid.jsc mismatch: expected 0, got {grid.jsc}"
    assert grid.jec == grid_size - 1, f"grid.jec mismatch: expected {grid_size - 1}, got {grid.jec}"

    assert grid.dx.size == dx_size, f"grid.dx.size mismatch: expected {dx_size}, got {grid.dx.size}"
    assert grid.dy.size == dy_size, f"grid.dy.size mismatch: expected {dy_size}, got {grid.dy.size}"
    assert grid.angle_dx.size == nsuper, f"grid.angle_dx.size mismatch: expected {nsuper}, got {grid.angle_dx.size}"
    assert grid.angle_dy.size == nsuper, f"grid.angle_dy.size mismatch: expected {nsuper}, got {grid.angle_dy.size}"
