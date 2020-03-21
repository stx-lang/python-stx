# Contributing

## Python Version

Use Python 3.8.0 through [pyenv](https://github.com/pyenv/pyenv#installation):

```shell script
pyenv shell 3.8.0
python -m venv env
source env/bin/activate
```

## Dependencies

List and install the main dependencies using the file `requirements-main.txt`.
 
```shell script
pip install -r requirements-main.txt
```
 
Freeze the specific versions in the file `requirements.txt`.

```shell script
pip freeze > requirements.txt
```

##  Generating Packages

This command generates the distribution packages:

```shell script
python setup.py sdist bdist_wheel
```

You may need to install:

```shell script
pip install setuptools wheel
```

# Uploading Package

```
# Test
python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Production
twine upload dist/*
```
