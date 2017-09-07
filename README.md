# NUFORC Sighting Reports

The Nationa UFO Research Center ([NUFORC](http://www.nuforc.org/)) maintains an online database of over 100,000 UFO sightings including city, shape, and a text description.
This project contains the code necessary to collect the data in the database, perform some standardization and cleaning, and geocode the sightings at the city/state level.

## Quickstart

**NOTE** Requires the Anaconda python distribution.

To get started, cd into the project root and run

```shell
make create_environment
source activate nuforc

make requirements

# Takes a very long time - about 3-4 hours.
make all
```

This downloads two datasets: the raw reports as line delimited JSON and a CSV file that contains refined fields (i.e. standardized / corrected states, cities, shapes, etc) as well as additional fields for the latitude and longitude of the sighting at the city level for most of the sightings.

## Raw Reports

The raw reports are pulled into `data/raw/nuforc_reports.json` as line delimited JSON.
The reports take a long time to download because there are a lot of them and because the scraper is throttled so as not to hit the NUFORC server very hard.
Each record has the following schema:

```javascript
{
    // Full text of the report.
    "text": string,

    // Summary stats as a string.
    "stats": string, 
    
    // The date-time as it appears in the report (M/DD/YY HH:MM).
    "date_time": string, 

    // URL to the original report.
    "report_link": string, 

    // City name.
    "city": string,

    // State as 2 character code.
    "state": string,

    // The shape of the object.
    "shape": string,

    // The duration of the sighting in no particular format.
    "duration": string,

    // A summary of the sighting. Seems to be just the first few sentences of 
    // the full report.
    "summary": string,

    // The date the sighting was posted to the NUFORC site as M/DD/YY.
    "posted": string
}
```

In this file all fields are as they appear on the site.
The scraper does no parsing except on the HTML elements to extract the content text.

## Enhanced Reports

The enhanced reports in CSV format are stored in `data/processed/nuforc_reports.csv`.
The data standardizations are as follows:

* Parse and standardize date-time values to ISO 8601 where possible (null when not possible).
* Standardize shape captilization plus a few minor merges (circular -> circle, etc).
* Standardize the state codes to capital case and fix obvious defects and misprints.
* Standardize the cities (i.e. Ft -> Fort, St -> Saint, etc) and remove irrelevant characters like parentheses.

All of the data cleaning code can be found in `scripts/process_report_data.py`.
The code is straightforward and pretty well commented.

In addition to the standardization, the reports are also geocoded where possible.
Most of the reports (~90k out of ~110k) were able to find a match by the geocoder, which uses the [MaxMind](https://dev.maxmind.com/geoip/geoip2/geolite2/) GeoLite2 database as a lookup mechanism for lat/lon.
Since there's no country information, pretty much all of the geocoded reports are in US and Canada.
Most of the "leftovers" are either outside US/Canada or pretty much impossible to geocode accurately (i.e. "rural, CA" or "Unknown location (military video)").

Here's the schema for the file:

| column name      | description                                                    |
| ---------------- | -------------------------------------------------------------- |
| `summary`        | The summary of the report (usually first couple of sentences). |
| `city`           | The city where the sighting occurred.                          |
| `state`          | The 2 character state code where the sighting occurred.        |
| `date_time`      | The date / time of the sighting in ISO 8601.                   |
| `shape`          | The shape of the object.                                       |
| `duration`       | The duration of the sighting in no particular format.          |
| `stats`          | Key stats about the report.                                    |
| `report_link`    | Link to the original report on the NUFORC site.                |
| `text`           | The full text of the report.                                   |
| `posted`         | The date the sighting was posted in ISO 8601.                  |
| `city_latitude`  | The latitude of the city of the sighting.                      |
| `city_longitude` | The longitude of the city of the sighting.                     |

## Makefile Targets

The included makefile has the following targets.

| target                              | description                                                      |
| ----------------------------------- | ---------------------------------------------------------------- |
| `create_environment`                | Creates a conda environment `nuforc`.                            |
| `destroy_environment`               | Destroys the `nuforc` environment.                               |
| `freeze`                            | Freezes the dependencies into `requirements.txt`.                |
| `requirements`                      | Installs the dependencies in `requirements.txt`.                 |
| `data/raw/nuforc_reports.json`      | Performs the scrape for the raw reports.                         |
| `data/external/cities.csv`          | Downloads and builds the city geocoder file.                     |
| `data/processed/nuforc_reports.csv` | Processed and geocodes the reports.                              |
| `all`                               | Shortcut for `data/processed/nuforc_reports.csv`.                |
| `load_elasticsearch`                | Loads the processed reports into a local Elasticsearch instance. |

The only thing that isn't super obvious is the Elasticsearch target.
I use Elasticsearch / Kibana to summarize, visualize, and sanity check the data while I work on the processing, so I put it there for convenience.
Use it or ignore it, it's not vital to getting the data.

## Other Notes

This product includes GeoLite2 data created by MaxMind, available from
<a href="http://www.maxmind.com">http://www.maxmind.com</a>.
