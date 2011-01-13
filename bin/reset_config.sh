#!/bin/sh

rm -fr $HOME/.config/DigitalGaia/Smewt-dev*
rm /tmp/smewt.cache

# also remove all *.pyc files
find -iname "*.pyc" -exec rm {} \;
