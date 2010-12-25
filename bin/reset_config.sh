#!/bin/sh

rm -fr $HOME/.config/DigitalGaia/*
rm -fr $HOME/Library/Preferences/Smewt*collection*
rm -fr $HOME/Library/Preferences/com.smewt.*
rm -fr /tmp/smewt.cache

# also remove all *.pyc files
find . -iname "*.pyc" -exec rm {} \;
