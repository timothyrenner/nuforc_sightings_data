ROOT = $(shell pwd)

create_environment:
	conda create --name nuforc python=3.6

destroy_environment:
	conda remove --name nuforc --all

freeze:
	pip freeze > requirements.txt

requirements:
	pip install -r requirements.txt

data/raw/nuforc_reports.json:
	cd nuforc_reports;\
	scrapy crawl nuforc_report_spider \
		--output $(ROOT)/data/raw/nuforc_reports.json \
		--output-format jsonlines

data/processed/nuforc_reports.csv: data/raw/nuforc_reports.json
	python scripts/process_report_data.py \
		data/raw/nuforc_reports.json \
		--output-file data/processed/nuforc_reports.csv \
		--exceptions-file data/exceptions/nuforc_exceptions.json

data/external/cities.csv:
	wget http://geolite.maxmind.com/download/geoip/database/GeoLite2-City-CSV.zip
	unzip GeoLite2-City-CSV.zip
	mv GeoLite2-City-CSV_* data/external/geolite_city
	mv GeoLite2-City-CSV.zip data/external/
	python scripts/make_cities.py \
		data/external/geolite_city/GeoLite2-City-Locations-en.csv \
		data/external/geolite_city/GeoLite2-City-Blocks-IPv4.csv \
		--output-file data/external/cities.csv

all: data/processed/nuforc_reports.csv

load_elasticsearch: data/processed/nuforc_reports.csv
	python scripts/load_elasticsearch.py data/processed/nuforc_reports.csv