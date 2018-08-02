init:
	pip install pipenv --upgrade
test:
	pipenv run py.test tests/test.py
publish:
	pip install 'twine>=1.5.0'
	python setup.py sdist bdist_wheel
	twine upload dist/*
	rm -fr build dist .egg encrypt.egg-info
