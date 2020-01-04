import click
import pandas as pd


@click.command()
@click.argument("city_location_file", type=click.File("r"))
@click.argument("ip_location_file", type=click.File("r"))
@click.option(
    "--output-file", "-o", type=click.File("w"), default="output.csv"
)
def main(city_location_file, ip_location_file, output_file):

    # country = country_iso_code
    # state = subdivision_1_iso_code
    # city = city_name
    # join key = geoname_id
    cities = pd.read_csv(city_location_file).set_index("geoname_id")

    # latitude = latitude
    # longitude = longitude
    # join key = geoname_id
    ip_locations = pd.read_csv(ip_location_file)

    city_locations = (
        ip_locations.join(cities, on="geoname_id", how="inner")
        .groupby(
            [
                "country_iso_code",
                "country_name",
                "subdivision_1_iso_code",
                "subdivision_1_name",
                "city_name",
            ]
        )
        .agg({"latitude": "mean", "longitude": "mean", "geoname_id": "count"})
        .reset_index()
        .rename(columns={"geoname_id": "num_blocks"})
    )

    city_locations.to_csv(output_file, index=False)


if __name__ == "__main__":
    main()
