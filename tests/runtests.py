#! /usr/bin/env python
""" Run all tests """

import os
import shutil
import unittest

from test_helper import TMPDATA

# Core geometry tests
from crs_tests import *
from geometry_init_tests import *
from geometry_tests import *
from quadtree_tests import *
from rtree_tests import *
from metadata_tests import *
from raster_tests import *

# Vector IO
from shapefile_tests import *
from geojson_tests import *
from misc_io_tests import *

# Raster IO
from geotiff_tests import *

if __name__ == "__main__":

    if not os.path.isdir(TMPDATA):
        os.mkdir(TMPDATA)

    try:
        unittest.main()
    finally:
        if os.path.isdir(TMPDATA):
            shutil.rmtree(TMPDATA)
