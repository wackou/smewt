#!/bin/sh

if [ -x $1 ]; then
  echo "Error: you need to specify a version number for the make_release script to work. Aborting..."
  exit
fi

VERSION=$1


# write version number to file
sed "s/__version__ =.*/__version__ = '$VERSION'/" smewt/__init__.py | sponge smewt/__init__.py

# TODO: generate win packages

git commit -a -m "Tagged $VERSION release"
git tag $VERSION


# generate and upload package to PyPI
python setup.py sdist upload

echo "Successfully made release $VERSION"
