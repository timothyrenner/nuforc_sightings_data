ROOT = $(shell pwd)
.PHONY: create_environment
.PHONY: destroy_environment
.PHONY: requirements
.PHONY: pull_reports
.PHONY: pull_cities
.PHONY: pull_data
.PHONY: load_elasticsearch

create_environment:
	conda create --name nuforc python=3.6

destroy_environment:
	conda remove --name nuforc --all

requirements:
	pip install -r requirements.txt

pull_reports:
	touch $(ROOT)/data/raw/nuforc_reports.json
	mv $(ROOT)/data/raw/nuforc_reports.json $(ROOT)/data/raw/nuforc_reports_orig.json
	cd nuforc_reports; \
	scrapy crawl nuforc_report_spider \
		--output $(ROOT)/data/raw/nuforc_reports.json \
		--output-format jsonlines
	cd $(ROOT)

	# Union the old reports with the new reports.
	python scripts/union_nuforc_reports.py \
		data/raw/nuforc_reports_orig.json \
		data/raw/nuforc_reports.json \
		data/raw/nuforc_reports_merged.json
	
	# Move the unioned file to the main file, delete the interim orig file.
	mv data/raw/nuforc_reports_merged.json data/raw/nuforc_reports.json
	rm data/raw/nuforc_reports_orig.json

pull_cities:
	wget http://geolite.maxmind.com/download/geoip/database/GeoLite2-City-CSV.zip
	unzip GeoLite2-City-CSV.zip
	mv GeoLite2-City-CSV_* data/external/geolite_city
	mv GeoLite2-City-CSV.zip data/external/
	python scripts/make_cities.py \
		data/external/geolite_city/GeoLite2-City-Locations-en.csv \
		data/external/geolite_city/GeoLite2-City-Blocks-IPv4.csv \
		--output-file data/external/cities.csv

pull_data: pull_reports pull_cities

data/processed/nuforc_reports.csv: data/raw/nuforc_reports.json data/external/cities.csv
	python scripts/process_report_data.py \
		data/raw/nuforc_reports.json \
		data/external/cities.csv \
		--output-file data/processed/nuforc_reports.csv

load_elasticsearch: data/processed/nuforc_reports.csv
	python scripts/load_elasticsearch.py data/processed/nuforc_reports.csv