#!/usr/bin/env python
# encoding: utf-8


# the following two variables are used by the target "waf dist"
VERSION = '0.1-dev'
APPNAME = 'smewt'

# these variables are mandatory ('/' are converted automatically)
srcdir = '.'
blddir = 'build'

def init():
    pass


def set_options(opt):
    # options provided by the modules
    opt.tool_options('qt4')


def configure(conf):
    # check that we have everything required
    conf.check_tool('g++ qt4')
    #print conf, type(conf), dir(conf)
    #print conf.env

    # system-wide flags
    conf.env['CXXFLAGS'] += [ '-Wall -O2 -fPIC' ] # -Werror

    # add support for QtDBus
    conf.env['CPPPATH'] += [ '/usr/include/qt4/QtDBus' ]
    conf.env['LIB'] += [ 'QtDBus' ]

    # add support for libcurl
    conf.env['LIB'] += [ 'curl' ]

    # add support for Soprano
    conf.env['LIB'] += [ 'soprano', 'sopranoclient' ]


def build(bld):
    bld.add_subdirs('src')
    #build_daemon(bld)
