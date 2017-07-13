"""
Data input functions for Karta

Used available drivers to read input data and return Karta geometry objects.
"""
import os
from numbers import Number
from osgeo import ogr
import picogeojson
from . import geometry
from . import _shp as shp
from . import _gpx as gpx
from ..crs import GeographicalCRS, ProjectedCRS, LonLatWGS84
from .. import errors

### GeoInterface functions ###

def from_shape(obj, properties=None):
    """ Read a __geo_interface__ dictionary and return an appropriate karta
    object """
    return _from_shape(obj.__geo_interface__, None)

def _from_shape(d, properties):
    if d is None:
        return None
    elif d["type"] == "Feature":
        p = d["properties"]
        return _from_shape(d["geometry"], p)
    else:
        c = d["coordinates"]
        if c is None:
            return None
        elif d["type"] == "Point":
            return geometry.Point(c, properties=properties)
        elif d["type"] == "LineString":
            return geometry.Line(c, properties=properties)
        elif d["type"] == "Polygon":
            subs = [geometry.Polygon(c[i]) for i in range(1, len(c))]
            return geometry.Polygon(c[0], properties=properties, subs=subs)
        elif d["type"] == "MultiPoint":
            return geometry.Multipoint(c, properties=properties)
        elif d["type"] == "MultiLineString":
            return geometry.Multiline(c, properties=properties)
        elif d["type"] == "MultiPolygon":
            return geometry.Multipolygon(c, properties=properties)
        else:
            raise NotImplementedError("Geometry type {0} not "
                                      "implemented".format(d["type"]))

### GeoJSON functions ###

def read_geojson(f, crs=LonLatWGS84):
    """ Parse GeoJSON and return a list of geometries.

    f : file-like object or str
        file object to read from or a GeoJSON string
    crs : karta.crs.CRS
        CRS object to bind to new geometries
    """
    def convert(geom, **kw):
        if isinstance(geom, picogeojson.Feature):
            res = [convert_feature(geom, **kw)]
        elif isinstance(geom, picogeojson.FeatureCollection):
            res = [convert_feature(f, **kw) for f in geom.features]
        elif isinstance(geom, picogeojson.GeometryCollection):
            res = [convert(item, **kw) for item in geom.geometries]
        else:
            res = convert_geometry(geom, **kw)
        return res

    def convert_geometry(geom, **kw):
        # TODO: Requires clean-up; was written before properties vs data was
        # clearly worked out. Hacks to bring it up to speed are ugly.
        if isinstance(geom, picogeojson.Point):
            kw.setdefault("properties", {})
            kw.setdefault("data", {})
            kw["properties"].update(kw["data"])
            del kw["data"]
            return geometry.Point(geom.coordinates, **kw)
        elif isinstance(geom, picogeojson.LineString):
            kw.setdefault("properties", {})
            kw.setdefault("data", {})
            kw["properties"].update(kw["data"])
            del kw["data"]
            return geometry.Line(geom.coordinates, **kw)
        elif isinstance(geom, picogeojson.Polygon):
            kw.setdefault("properties", {})
            kw.setdefault("data", {})
            kw["properties"].update(kw["data"])
            del kw["data"]
            return geometry.Polygon(geom.coordinates[0],
                                    subs=geom.coordinates[1:],
                                    **kw)
        elif isinstance(geom, picogeojson.MultiPoint):
            return geometry.Multipoint(geom.coordinates, **kw)
        elif isinstance(geom, picogeojson.MultiLineString):
            return geometry.Multiline(geom.coordinates, **kw)
        elif isinstance(geom, picogeojson.MultiPolygon):
            return geometry.Multipolygon(geom.coordinates, **kw)
        else:
            raise TypeError("{0} is a not a GeoJSON entity".format(type(geom)))

    def convert_feature(feat, **kw):
        properties = {}
        data = {}
        if isinstance(feat.geometry, (picogeojson.MultiPoint,
                                      picogeojson.MultiLineString,
                                      picogeojson.MultiPolygon)):
            n = len(feat.geometry.coordinates)
            for k, v in feat.properties.items():
                try:
                    if len(v) == n:
                        data[k] = v
                    else:
                        properties[k] = v
                except TypeError:
                    properties[k] = v
        else:
            properties.update(feat.properties)
        # if len(data) == 0:
        #     data = {}
        # else:
        #     for key, val in data.items():
        #         if any(isinstance(a, Number) or hasattr(a, "dtype") for a in val):
        #             for i in range(len(val)):
        #                 if val[i] is None:
        #                     val[i] = float('nan')
        kw["data"] = data
        kw["properties"] = properties
        return convert(feat.geometry, **kw)

    R = picogeojson.Deserializer()
    geom = R(f)
    return convert(geom, crs=crs)

def _geojson_properties2karta(properties, n):
    """ Takes a dictionary (derived from a GeoJSON properties object) and
    divides it into singleton properties and *n*-degree data. """
    props = {}
    data = {}
    for (key, value) in properties.items():
        if isinstance(value, list) or isinstance(value, tuple):
            if len(value) == n:
                data[key] = value
            else:
                raise ValueError("properties must be singleton or per-vertex")
        else:
            props[key] = value
    return props, data

### Shapefile functions ###

def get_filenames(stem, check=False):
    """ Given a filename basename, return the associated shapefile paths. If
    `check` is True, ensure that the files exist."""
    if stem.endswith(".shp"):
        stem = stem[:-4]
    shp = stem + '.shp'
    shx = stem + '.shx'
    dbf = stem + '.dbf'
    if check:
        for fnm in (shp, shx, dbf):
            if not os.path.isfile(fnm):
                raise Exception('missing {0}'.format(fnm))
    return {'shp':shp, 'shx':shx, 'dbf':dbf}

def ogr_read_shapefile(stem):
    fnms = get_filenames(stem)
    driver = ogr.GetDriverByName("ESRI Shapefile")
    ds = driver.Open(fnms["shp"], 0)
    layer = ds.GetLayer()

    try:
        _geoms = [_from_shape(gi, p)
                 for (gi,p) in zip(shp.ogr_read_geometries(layer),
                                   shp.ogr_read_attributes(layer))]
        crs = ogr_parse_srs(layer)
    finally:
        del ds, driver, layer

    geoms = []
    for g in _geoms:
        if isinstance(g, list):
            for part in g:
                part.crs = crs
            geoms.append(g)
        elif g is not None:
            g.crs = crs
            geoms.append(g)
    return geoms

def ogr_parse_srs(lyr):
    """ Given an OGR type with a `GetSpatialRef` method, return a matching CRS
    object. """
    srs = lyr.GetSpatialRef()
    if srs is None:
        crs = LonLatWGS84
    else:
        name = srs.GetAttrValue('PROJCS')
        if srs.IsGeographic():
            spheroid = "+a={a} +f={f}".format(a=srs.GetSemiMajor(),
                                              f=1.0/srs.GetInvFlattening())
            crs = GeographicalCRS(spheroid, name)
        else:
            crs = ProjectedCRS(srs.ExportToProj4(), name=name)
    return crs

# convenience binding
read_shapefile = ogr_read_shapefile


### GPX functions ###

def read_gpx_waypts(fnm):
    gpx_doc = gpx.GPX(fnm)
    return [_waypt2pt(pt) for pt in gpx_doc.waypts]

def read_gpx_tracks(fnm):
    gpx_doc = gpx.GPX(fnm)
    return [_track2lines(trk) for trk in gpx_doc.tracks]

def _waypt2pt(waypt):
    return geometry.Point(waypt.lonlat,
                          properties=waypt.properties,
                          crs=LonLatWGS84)

def _seg2line(seg):
    return geometry.Line([pt.lonlat for pt in seg.trkpts],
                         properties=seg.properties,
                         crs=LonLatWGS84)

def _track2lines(track):
    return [_seg2line(seg) for seg in track.trksegs]

