#!/bin/sh

VERSION=$(cat version.txt)

echo "Clear previous builds..." && \
rm -rf env/ && rm -rf build/ && \
rm -rf dist/ && rm -rf *.egg-info/ && \

echo "Create a new virtual env..." && \
python -m venv env && \

echo "Activating virtual env..." && \
source env/bin/activate && \

echo "Installing requirements..." && \
pip install -r requirements-dev.txt && \

echo "Auditing code..." && \
flake8 && \

echo "Running unit tests..." && \
pytest && \

echo "Generating dist archives..." && \
python setup.py sdist bdist_wheel && \

echo "" && \
echo "Publish package $VERSION..." && \
twine upload dist/* && \

echo "" && \
echo "Pushing tag..." && \
git tag $VERSION -a -m "Release for version $VERSION" && \
git push --follow-tags && \

echo "Done!"
