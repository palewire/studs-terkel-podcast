serve:
	export FLASK_ENV=development && export FLASK_APP=app.py && pipenv run flask run

freeze:
	pipenv run python freeze.py
	echo 'studs.show' > docs/CNAME

tweet:
	pipenv run python notebooks/tweet.py

.PHONY: freeze serve tweet
