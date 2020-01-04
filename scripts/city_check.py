# Checks for cities that aren't in the city data file.

import pandas as pd
from csv import DictReader, DictWriter
from toolz import compose, pluck, countby
import sys

sightings = DictReader(open('data/processed/nuforc_reports.csv', 'r'))
bad_cities_file = \
    DictWriter(open('bad_cities.csv', 'w'), fieldnames=['city','state','count'])
bad_cities_file.writeheader()

bad_cities = []
for sighting in sightings:
    if not sighting['city_latitude'] or not sighting['city_longitude']:
        bad_cities.append(
            {
                "city": sighting["city"],
                "state": sighting["state"]
            }
        )

bad_cities_counts = countby(['state','city'], bad_cities)

total = 0
for (state, city), count in \
    sorted(bad_cities_counts.items(), key=lambda x: x[1], reverse=True):

    total += count
    
    bad_cities_file.writerow({'state': state, 'city': city, 'count': count})

print("Total number of incomplete geocodes: {}".format(total))
    