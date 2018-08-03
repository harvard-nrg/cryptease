init:
	pip install pipenv --upgrade
	pip install --dev --skip-lock
test:
	pipenv run py.test tests/test.py
publish:
	pip install 'twine>=1.5.0'
	python setup.py sdist bdist_wheel --universal
	twine upload dist/*
	rm -fr build dist .egg cryptease.egg-info
