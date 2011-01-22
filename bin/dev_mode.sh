#!/bin/sh

if [ -x $1 ]; then
  echo "Error: you need to specify a development version number for the dev_mode script to work. Aborting..."
  exit
fi

VERSION=$1


# write version number to file
sed "s/__version__ =.*/__version__ = '$VERSION'/" smewt/__init__.py | sed "s/APP_NAME = .*/APP_NAME = 'Smewt-dev'/" | sponge smewt/__init__.py



git commit -a -m "Tagged $VERSION release"
git tag $VERSION


# generate and upload package to PyPI
# TODO: generate win packages
python setup.py sdist upload

echo "Successfully made release $VERSION"
