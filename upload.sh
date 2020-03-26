#!/bin/sh

echo "Clear previous builds..."  && \
./clear.sh && \

echo "Create a new brand virtual env..."  && \
python -m venv env && \

echo "Activating virtual env..."  && \
source env/bin/activate && \

echo "Installing requirements..."  && \
pip install -r requirements-dev.txt && \

echo "Auditing code..."  && \
flake8 && \

echo "Generating dist package..."  && \
python setup.py sdist bdist_wheel && \

echo "Uploading version $(cat version.txt)..."  && \
twine upload dist/*
