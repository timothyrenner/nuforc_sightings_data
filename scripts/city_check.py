# Checks for cities that aren't in the city data file.

import pandas as pd
from csv import DictReader, DictWriter
from toolz import compose, pluck
import sys

sightings = DictReader(open('data/processed/nuforc_reports.csv', 'r'))
bad_cities = \
    DictWriter(open('bad_cities.csv', 'w'), fieldnames=['city','state'])

for sighting in sightings:
    if not sighting['city_latitude'] or not sighting['city_longitude']:
        bad_cities.writerow(
            {
                "city": sighting["city"],
                "state": sighting["state"]
            }
        )