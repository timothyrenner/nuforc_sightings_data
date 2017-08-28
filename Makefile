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