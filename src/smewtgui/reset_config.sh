#!/bin/sh

rm $HOME/.config/DigitalGaia/Smewg.*
rm /tmp/smewt.cache

# also remove all *.pyc files
find -iname "*.pyc" -exec rm {} \;
