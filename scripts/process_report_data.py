import click
import json
import re

from csv import DictWriter
from datetime import datetime,timedelta

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

def clean_city(city):
    """ Cleans the city names.
    """
    new_city = remove_parens(city)
    new_city = remove_forward_slashes(new_city)
    new_city = fix_saints(new_city)

    return new_city

@click.command()
@click.argument('raw_report_file', type=click.File('r'))
@click.option('--output-file', '-o', 
              type=click.File('w'), 
              default='output.csv')
@click.option('--exceptions-file', '-e', 
              type=click.File('w'), 
              default='exceptions.json')
def main(raw_report_file, output_file, exceptions_file):
    """ Reads the raw scraped JSON reports and processes them into a CSV file
        whilst performing data enrichment and cleaning. If a report can't be
        cleaned in an automated way it is passed to an exceptions file, with
        the exception added as a field.
    """

    writer = DictWriter(output_file, fieldnames=[
        "summary", "city", "state", "date_time", "shape", "duration",
        "stats", "report_link", "text", "posted"
    ])

    writer.writeheader()

    for report_str in raw_report_file:
        
        report = json.loads(report_str)
        
        try:
            # Standardize the dates into isoformat.
            posted_date_time = \
                create_date_time(
                    report["posted"]
                ).isoformat()
            report_date_time = \
                create_date_time(
                    report["date_time"], 
                ).isoformat()
        except Exception as e:
            posted_date_time = None
            report_date_time = None

        report["posted"] = posted_date_time
        report["date_time"] = report_date_time
        
        # Clean the shape.
        report["shape"] = clean_shape(report["shape"]) \
            if report["shape"] \
            else report["shape"]

        # Clean the state abbreviations.
        report["state"] = clean_state(report["state"]) \
            if report["state"] \
            else report["state"]

        # Clean the city.
        report["city"] = clean_city(report["city"]) \
            if report["city"] \
            else report["city"]

        writer.writerow(report)

if __name__ == "__main__":
    main() # Click injects the arguments.