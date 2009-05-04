# setup.py
# coding: latin-1
#from distutils.core import setup

# Copyright (C) 2006-2007 Ricard Marxer <email@ricardmarxer.com>
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3.0 of the License, or (at your option) any
# later version.
# 
# This library is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# 
# You should have received a copy of the GNU General Public License along
# with this library; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

description   = """ Smewt is the revolution.

2008, Nicolas Wack, Ricard Marxer, Roberto Toscano

"""

import ez_setup
from setuptools import setup, find_packages
ez_setup.use_setuptools()

#from distutils.core import setup
import os
import sys
import glob

# The library extensions
unused_extensions = ['.dll', '.so', '.jnilib']
options = {}

packages = find_packages()

data_files = [('/usr/share/applications' , ['digitalgaia-smewt.desktop']),
              ('/usr/share/icons/hicolor/scalable/apps' , ['smewt/icons/smewt.svg'])]

opts = {}

# Data files necessary for each platform
if sys.platform == 'linux2':
    unused_extensions.remove('.so')
    buildstyle = 'console'

elif sys.platform == 'win32':
    import py2exe
    buildstyle = 'console'
    packager = 'py2exe'
    unused_extensions.remove('.dll')
    data_files += [(r'', [r'MSVCP71.dll'])]

    ## Necessary to find MSVCP71.dll
    origIsSystemDLL = py2exe.build_exe.isSystemDLL
    
    def isSystemDLL(pathname):
            if os.path.basename(pathname).lower() in ("msvcp71.dll", "dwmapi.dll"):
                    return 0
            return origIsSystemDLL(pathname)
        
    py2exe.build_exe.isSystemDLL = isSystemDLL
        
elif sys.platform == 'darwin':
    import py2app
    buildstyle = 'app'
    packager = 'py2app'
    options = dict(py2app = dict(argv_emulation = True))
    unused_extensions.remove('.jnilib')

provides = packages

requires = [#'IMDbPY(>=3.7)',
            #'Cheetah(>=1.0)',
            #'pycurl',
            #'IMDbPY(>=4.0)',
            #'PyQt(>=4.4.0)'
            ]

install_requires = [#'IMDbPY',
                    #'Cheetah',
                    #0'pycurl',
                    #'IMDbPY',
                    #'PyQt'
                    ]

dependency_links = []


scripts = ['smewg.py']

# HACK: allow to update the menus
from setuptools.command.install import install as _install
import subprocess

class install(_install):
    def run(self):
        _install.run(self)
        print 'Processing triggers for menu ...'
        subprocess.call(['xdg-desktop-menu', 'install', '/usr/share/applications/digitalgaia-smewt.desktop'])
        subprocess.call(['update-menus'])
        
        
setup(name = 'Smewt',
      cmdclass = {'install': install},
      version = '1.0',
      description = description,
      author = 'Nicolas Wack, Ricard Marxer Piñón, Roberto Toscano',
      author_email = '',
      url = 'http://www.smewt.com/',
      #options = options,
      requires = requires,
      install_requires = install_requires,
      dependency_links = dependency_links,
      provides = provides,
      packages = packages,
      scripts = scripts,
      package_data = {'smewt.icons': ['*.png', '*.svg'],
                      'smewt.media.common': ['*.png'],
                      'smewt.media.common.images.flags': ['*.png'],
                      'smewt.media.thirdparty': ['*.js'],
                      'smewt.media.thirdparty.dataTables.media.css': ['*.css'],
                      'smewt.media.thirdparty.dataTables.media.js': ['*.js'],
                      'smewt.media.thirdparty.dataTables.media.images': ['*.jpg'],
                      'smewt.media.movie': ['*.tmpl', '*.css', '*.js'],
                      'smewt.media.series': ['*.tmpl', '*.css', '*.js'],
                      'smewt.media.speeddial': ['*.html', '*.png']},
      data_files = data_files,
      classifiers =
            [ 'Development Status :: 1 - Beta',
              'Intended Audience :: Entertainment',
              'License :: OSI Approved :: GPL License',
              'Topic :: Multimedia :: Sound/Audio'],
      zip_safe = False # the package can run out of an .egg file
      )
