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
from setuptools import setup
ez_setup.use_setuptools()

#from distutils.core import setup
import os
import sys
import glob

# The library extensions
unused_extensions = ['.dll', '.so', '.jnilib']
options = {}

packages = ['smewt',
            'smewt.base',
            'smewt.media',
            'smewt.media.series',
            'smewt.gui',
            'smewt.solvers',
            'smewt.taggers',
            'smewt.guessers',
            'smewt.icons'
            ]

data_files = []

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

requires = ['IMDbPY(>=0.38)',
            'Cheetah(>=1.0)',
            'PyQt(>=4.4.3)'
            ]

install_requires = ['IMDbPY',
                    'Cheetah',
                    'PyQt'
                    ]

dependency_links = []


scripts = ['smewg.py']

setup(name = 'Smewt',
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
      package_data = {'smewt.icons': ['applications-multimedia.png'],
                      'smewt.media.series': ['view_episodes_by_season.tmpl',
                                             'view_all_series.tmpl',
                                             'jquery-1.2.2.pack.js',
                                             'animatedcollapse.js']},
      data_files = data_files,
      classifiers =
            [ 'Development Status :: 1 - Beta',
              'Environment :: Console',
              'Intended Audience :: Developers',
              'Intended Audience :: Entertainment',
              'License :: OSI Approved :: GPL License',
              'Topic :: Multimedia :: Sound/Audio'],
      zip_safe=True, # the package can run out of an .egg file
      console=scripts,
      options = opts
      )
