from setuptools import setup, find_packages
import os, sys

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    'pygoo>=0.1.3',
    'pycurl',
    'cheetah',
    'lxml',
    'feedparser'
]


datafiles_exts = [ '*.png', '*.svg', '*.tmpl', '*.css', '*.html', '*.js' ]

# py2app data
APP = ['bin/smewg.py']
DATA_FILES = []
OPTIONS = { 'argv_emulation': True,
            'iconfile': 'smewt/icons/smewt.icns',
            'packages': [ 'smewt', 'Cheetah', 'lxml' ],
            'frameworks': [ '/Developer/Applications/Qt/plugins/iconengines/libqsvgicon.dylib' ],
            'includes': [ 'sip', 'PyQt4', 'PyQt4.QtCore', 'PyQt4.QtGui', 'PyQt4.QtNetwork', 'PyQt4.QtWebKit',  'PyQt4.QtXml', 'PyQt4.QtSvg' ],
            'excludes': [ 'PyQt4.QtDesigner', 'PyQt4.QtOpenGL', 'PyQt4.QtScript',
                          'PyQt4.QtSql', 'PyQt4.QtTest' ] # 'PyQt4.phonon'
            }


args = dict(name = 'smewt',
            version = '0.2',
            description = 'Smewt - a smart media manager.',
            long_description = README + '\n\n' + NEWS,
            classifiers = [], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
            keywords = 'smewt pygoo media manager video collection',
            author = 'Nicolas Wack',
            author_email = 'wackou@gmail.com',
            url = 'http://www.smewt.com/',
            license = 'GPLv3',
            packages = find_packages(exclude = [ 'ez_setup', 'examples', 'tests' ]),
            #package_data = dict((package, datafiles_exts) for package in find_packages()),
            include_package_data = True,
            scripts = [ 'bin/smewg' ],
            install_requires = install_requires
            )

if sys.platform == 'darwin':
    args.update(dict(# for py2app
                     name = 'Smewt',
                     app=APP,
                     data_files=DATA_FILES,
                     options={'py2app': OPTIONS, 'plist':dict(CFBundleIdentifier = 'com.smewt.Smewt')},
                     setup_requires=['py2app']
                     ))

setup(**args)
