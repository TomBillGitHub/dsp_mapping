run:
	poetry run python main.py

post:
	poetry run python main.py --post

black:
	poetry run black *.py

pylint:
	poetry run pylint *.py
