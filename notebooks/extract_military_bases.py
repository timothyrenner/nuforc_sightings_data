import typer
from pathlib import Path
import pandas as pd
from dataclasses import dataclass, asdict, field
from typing import List
from pyproj import Transformer
from lxml import etree
from shapely import Point, to_geojson, transform, Polygon
import numpy as np


def geographic_buffer(
    longitude: float, latitude: float, buffer_size_km: float
) -> Polygon:
    # In general picking a map projection amounts to picking the least worst
    # solution. One fairly standard approach is to perform a universal
    # transverse mercator (UTM) projection. The standard definition divides
    # these into zones, but it's easy to recenter the central meridian at the
    # centroid of the geometry and perform the projection there to minimize
    # distance distortion. The lon_0 keyword argument sets the central
    # meridian. Note longitude is x.
    lonlat_to_tmerc = Transformer.from_crs(
        "EPSG:4326",
        f"+proj=tmerc +ellps=WGS84 +lon_0={longitude}",
        always_xy=True,
    )

    geometry_tmerc_coords = lonlat_to_tmerc.transform(longitude, latitude)
    geometry_tmerc = Point(*geometry_tmerc_coords)

    geometry_tmerc_buffered = geometry_tmerc.buffer(buffer_size_km * 1000)
    geometry_tmerc_buffered_coords = np.array(
        geometry_tmerc_buffered.boundary.coords
    )

    tmerc_to_lonlat = Transformer.from_crs(
        lonlat_to_tmerc.target_crs, lonlat_to_tmerc.source_crs, always_xy=True
    )

    geometry_lonlat_buffered_coords = tmerc_to_lonlat.transform(
        geometry_tmerc_buffered_coords[:, 0],
        geometry_tmerc_buffered_coords[:, 1],
    )

    buffer_lonlat_polygon_def = np.vstack(geometry_lonlat_buffered_coords).T

    return Polygon(buffer_lonlat_polygon_def)


@dataclass
class MilitaryBase:
    name: str
    branch: str
    link: str
    latitude: float
    longitude: float
    buffer_100km_geojson: str = field(init=False)

    def __post_init__(self):
        buffer_100km_polygon = geographic_buffer(
            self.longitude, self.latitude, 100
        )
        self.buffer_100km_geojson = to_geojson(buffer_100km_polygon)


def main(input_file: Path, output_file: Path):
    namespaces = {"kml": "http://www.opengis.net/kml/2.2"}
    military_base_tree = etree.parse(input_file)

    names = military_base_tree.xpath(
        "//kml:Placemark/kml:name/text()", namespaces=namespaces
    )

    coordinates = military_base_tree.xpath(
        "//kml:Placemark/kml:Point/kml:coordinates/text()",
        namespaces=namespaces,
    )

    # Each of these needs to be parsed and extracted as HTML.
    # This will happen inside the loop.
    description_tables = military_base_tree.xpath(
        "//kml:Placemark/kml:description/text()", namespaces=namespaces
    )

    # HTML parser for the tables.
    html_parser = etree.HTMLParser()

    bases: List[MilitaryBase] = []

    for name, coordinate_str, description in zip(
        names, coordinates, description_tables
    ):
        base_lon, base_lat = coordinate_str.split(",")

        description_tree = etree.fromstring(description, html_parser)
        branch = description_tree.xpath("//table/tr/td")[
            1
        ].xpath(  # Second row has the branch name.
            "./b/text()"
        )[
            0
        ]
        link = description_tree.xpath("//table/tr/td")[0].xpath("./a/@href")[0]

        bases.append(
            MilitaryBase(
                name=name,
                branch=branch,
                link=link,
                latitude=float(base_lat),
                longitude=float(base_lon),
            )
        )

    pd.DataFrame(list(map(asdict, bases))).to_csv(output_file)


if __name__ == "__main__":
    typer.run(main)
