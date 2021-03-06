Package reference
=================

This is a nearly-exhaustive listing of *karta* classes and function. Some
experimental, deprecated, or private components are excluded.

Raster package (``karta.raster``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``karta.raster`` package provides *Grid* classes as well as readers for ESRI
ASCII grids and GeoTiff files. The most commonly used *Grid* subclass is
*RegularGrid*, which can efficiently handle gridded datasets with constant
offsets between nodes. *Grids* support geographically-aware clipping, sampling,
and profile extraction.

.. automodule:: karta.raster.grid

.. autoclass:: karta.raster.grid.Grid
    :members:

RegularGrid
-----------

.. autoclass:: karta.raster.grid.RegularGrid
    :members:

SimpleBand
----------

.. autoclass:: karta.raster.band.SimpleBand
    :members:

CompressedBand
--------------

.. autoclass:: karta.raster.band.CompressedBand
    :members:

Miscellaneous raster functions
------------------------------

.. automodule:: karta.raster.misc
    :members:

Raster IO modules
-----------------

.. automodule:: karta.raster.read
    :members:

GeoTiff (GDAL interface)
++++++++++++++++++++++++

.. automodule:: karta.raster._gdal
    :members:

ESRI ASCII grids
++++++++++++++++

.. automodule:: karta.raster._aai
    :members:

Vector package (``karta.vector``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The package ``karta.vector`` provides a *Geometry* class, subclasses for
*Point*, *Line*, and *Polygon* types and their multipart counterparts, as well
as readers and writers for ESRI shapefiles, GeoJSON, and GPX files.

All concrete geometries support the `__geo_interface__`_ attribute, and map to
*Feature* types.

.. _`__geo_interface__`: https://gist.github.com/sgillies/2217756

Geometry
--------

.. automodule:: karta.vector.geometry

Geometry
++++++++

.. autoclass:: karta.vector.geometry.Geometry
    :members:

Point
+++++

.. autoclass:: karta.vector.Point
    :members:
    :inherited-members:

Line
++++

.. autoclass:: karta.vector.Line
    :members:
    :inherited-members:

Polygon
+++++++

.. autoclass:: karta.vector.Polygon
    :members:
    :inherited-members:

Multipoint
++++++++++

.. autoclass:: karta.vector.Multipoint
    :members:
    :inherited-members:

Multiline
+++++++++

.. autoclass:: karta.vector.Multiline
    :members:
    :inherited-members:

Multipolygon
++++++++++++

.. autoclass:: karta.vector.Multipolygon
    :members:
    :inherited-members:

Metadata tables
---------------

.. automodule:: karta.vector.table

.. autoclass:: karta.vector.table.Table
    :members:

.. autoclass:: karta.vector.table.Indexer
    :members:

Trees
-----

Quadtree
++++++++

.. automodule:: karta.vector.quadtree
    :members:

R-Tree
++++++

.. automodule:: karta.vector.rtree
    :members:

Vector IO modules
-----------------

.. automodule:: karta.vector.read
    :members:

GeoJSON
+++++++

.. automodule:: karta.vector._geojson
    :members:

ESRI shapefile (GDAL interface)
+++++++++++++++++++++++++++++++

.. automodule:: karta.vector._shp
    :members:

GPS Exchange
++++++++++++

.. automodule:: karta.vector._gpx
    :members:

Managing coordinate systems
~~~~~~~~~~~~~~~~~~~~~~~~~~~

CRS (``karta.crs``)
-------------------

.. automodule:: karta.crs
    :members:

Geodesy (``karta.geodesy``)
---------------------------

Functions from ``karta.geodesy`` should generally be accessed through a ``CRS``
subclass rather than directly.

.. automodule:: karta.geodesy
    :members:
