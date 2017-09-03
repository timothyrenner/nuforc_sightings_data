# Checks for cities that aren't in the city data file.

import pandas as pd
from csv import DictReader
from toolz import compose, pluck
import sys

listmap = compose(list, map)

# THANK YOU STACK OVERFLOW: 
# https://stackoverflow.com/questions/18171739/unicodedecodeerror-when-reading-csv-file-in-pandas-with-python

cities = \
    pd.read_csv('data/external/cities.csv', encoding="ISO-8859-1", skiprows=1)

# Lower case the city names.
cities.loc[:, 'city'] = cities['city'].str.lower()

# Set the index.
cities.set_index('city', inplace=True)

sightings = DictReader(open('data/processed/nuforc_reports.csv', 'r'))

sighting_cities = \
    listmap(
        lambda x: x.lower() if x else x, # Lower case the city.
        pluck(
            'city', # Get the city field.
            sightings
        )
    )

sighting_cities_frame = pd.DataFrame(data={
    "city": sighting_cities
})

sighting_cities_joined = \
    sighting_cities_frame.join(cities, how='left', on='city')

bad_joins = sighting_cities_joined.latitude.isnull()

sighting_cities_joined.loc[bad_joins, 'city'].to_csv('bad_cities.csv', index=False)