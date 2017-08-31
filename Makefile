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

all: data/processed/nuforc_reports.csv