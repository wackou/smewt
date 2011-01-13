#!/bin/sh

rm -fr $HOME/.config/DigitalGaia/Smewt-dev*
rm -fr /tmp/smewt.cache

# for Mac OS X
rm -fr $HOME/Library/Preferences/Smewt*collection*
rm -fr $HOME/Library/Preferences/com.smewt.*


# also remove all *.pyc files
find . -iname "*.pyc" -exec rm {} \;
