create_environment:
	conda create --name nuforc python=3.6

destroy_environment:
	conda remove --name nuforc --all

freeze:
	pip freeze > requirements.txt

requirements:
	pip install -r requirements.txt