import click
import json
import re

from csv import DictReader, DictWriter
from datetime import datetime, timedelta
from toolz import curry, get_in

REPORT_DATE_TIME = "%m/%d/%y %H:%M"
SHORT_REPORT_DATE_TIME = "%m/%d/%y"


def create_date_time(report_date_time):
    """ Takes a report datetime as a string and converts it into a datetime
        object.
    """
    try:
        date_time = datetime.strptime(report_date_time, REPORT_DATE_TIME)
    except ValueError:
        # Some of the dates are in the "short" format.
        date_time = datetime.strptime(report_date_time, SHORT_REPORT_DATE_TIME)

    # Correct century for future dates.
    if date_time > datetime.now():
        date_time = date_time - timedelta(year=100)
    return date_time


def remove_parens(report_city):
    """ Removes parenthetical "enhancements" to the city names.
    """

    return re.sub("\(.*\)", "", report_city).strip()


def remove_forward_slashes(report_city):
    """ Removes forward slashes in city names, uses first value.
    """

    return report_city.split("/")[0].strip()


def fix_saints(report_city):
    """ Changes St. -> Saint
    """

    city_components = report_city.split(" ")

    if city_components[0].strip().lower() == "st.":
        city_components[0] = "Saint"

    return " ".join(city_components)


def fix_forts(report_city):
    """ Changes Ft. -> Fort.
    """

    city_components = report_city.split(" ")

    if city_components[0].strip().lower() == "ft.":
        city_components[0] = "Fort"

    return " ".join(city_components)


def fix_mounts(report_city):
    """ Changes Mt. -> Mount
    """

    city_components = report_city.split(" ")

    if city_components[0].strip().lower() == "mt.":
        city_components[0] = "Mount"

    return " ".join(city_components)


def clean_shape(shape):
    """ Standardizes the shape.
    """

    # Standardize shapes to lower case, merge the obvious ones.
    new_shape = shape.lower() if shape else None
    if new_shape == "triangular":
        new_shape = "triangle"
    if new_shape == "changed":
        new_shape == "changing"

    return new_shape


def clean_state(state):
    """ Upper cases the state and fixes a few weird issues.
    """

    new_state = state.upper() if state else None
    # NF -> NL for Newfoundland and Labrador.
    if new_state == "NF":
        new_state = "NL"
    # PQ -> QC for Quebec.
    if new_state == "PQ":
        new_state = "QC"
    # SA -> SK for Sasketchewan.
    if new_state == "SA":
        new_state = "SK"
    # YK -> YT for Yukon Territory.
    if new_state == "YK":
        new_state = "YT"

    return new_state


def clean_city(city, state):
    """ Cleans the city names.
    """
    new_city = remove_parens(city)
    new_city = remove_forward_slashes(new_city)
    new_city = fix_saints(new_city)
    new_city = fix_forts(new_city)
    new_city = fix_mounts(new_city)

    ####### SPOT CORRECTIONS #######
    # These are corrections for the obvious weird stuff in either the city
    # database or the sighting data.

    # Correct New York City -> New York
    if new_city.lower() == "new york city":
        new_city = "New York"

    # Correct Saint / St. Louis MO -> St Louis MO
    if (
        (new_city.lower() == "saint louis")
        or (new_city.lower() == "st. louis")
    ) and (state == "MO"):
        new_city = "St Louis"

    # Correct Washington, D.C. -> Washington.
    if new_city.lower() == "washington, d.c.":
        new_city = "Washington"

    # Correct Saint Petersburg, FL -> St. Petersburg
    if (new_city.lower() == "saint petersburg") and (state == "FL"):
        new_city = "St. Petersburg"

    # Correct Port St. Lucie -> Port Saint Lucie
    if (new_city.lower() == "port st. lucie") and (state == "FL"):
        new_city = "Port Saint Lucie"

    if (new_city.lower() == "saint peters") and (state == "MO"):
        new_city = "City of Saint Peters"

    return new_city


def _geocoder_template(geocoder_hash, state, city):
    """ This is the template function for the geocoder. It's meant to have the
        first argument (the hash) bound.
    """
    return (
        get_in([(state, city.lower()), 0], geocoder_hash, None),
        get_in([(state, city.lower()), 1], geocoder_hash, None),
    )


def create_geocoder(city_file):
    """ Creates a geocoder function for cities that takes a city name and region
        and returns the latitude and longitude.
    """
    reader = DictReader(city_file)

    # Create a blank hash to load.
    # (state_iso,city_name) => (lat, lon, records)
    # state/city collisions are resolved by whichever one has the most records.
    # Not 100% that's the right call but it's a start.
    geocoder_hash = {}

    for row in reader:
        row_key = (
            row["subdivision_1_iso_code"].upper(),
            row["city_name"].lower(),
        )

        if (row_key not in geocoder_hash) or (
            int(row["num_blocks"]) > geocoder_hash[row_key][2]
        ):
            geocoder_hash[row_key] = (
                float(row["latitude"]),
                float(row["longitude"]),
                int(row["num_blocks"]),
            )

    # Bind the geocoder hash to the geocoder template.
    return curry(_geocoder_template)(geocoder_hash)


@click.command()
@click.argument("raw_report_file", type=click.File("r"))
@click.argument("city_file", type=click.File("r"))
@click.option(
    "--output-file", "-o", type=click.File("w"), default="output.csv"
)
def main(raw_report_file, city_file, output_file):
    """ Reads the raw scraped JSON reports and processes them into a CSV file
        whilst performing data enrichment and cleaning. 
    """

    # Create the geocoder function.
    geocode = create_geocoder(city_file)

    writer = DictWriter(
        output_file,
        fieldnames=[
            "summary",
            "city",
            "state",
            "date_time",
            "shape",
            "duration",
            "stats",
            "report_link",
            "text",
            "posted",
            "city_latitude",
            "city_longitude",
        ],
    )

    writer.writeheader()

    for report_str in raw_report_file:

        report = json.loads(report_str)

        try:
            # Standardize the dates into isoformat.
            posted_date_time = create_date_time(report["posted"]).isoformat()
            report_date_time = create_date_time(
                report["date_time"],
            ).isoformat()
        except Exception as e:
            posted_date_time = None
            report_date_time = None

        report["posted"] = posted_date_time
        report["date_time"] = report_date_time

        # Clean the shape.
        report["shape"] = (
            clean_shape(report["shape"])
            if report["shape"]
            else report["shape"]
        )

        # Clean the state abbreviations.
        report["state"] = (
            clean_state(report["state"])
            if report["state"]
            else report["state"]
        )

        # Clean the city.
        report["city"] = (
            clean_city(report["city"], report["state"])
            if report["city"] and report["state"]
            else report["city"]
        )

        # Geocode the report.
        if report["state"] and report["city"]:
            city_lat, city_lon = geocode(report["state"], report["city"])
            report["city_latitude"] = city_lat
            report["city_longitude"] = city_lon
        else:
            report["city_latitude"] = None
            report["city_longitude"] = None

        writer.writerow(report)


if __name__ == "__main__":
    main()  # Click injects the arguments.

