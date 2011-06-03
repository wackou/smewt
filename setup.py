# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os, sys

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    'pygoo>=0.1.4',
    'guessit>=0.2',
    'BeautifulSoup', # for periscope
    'cheetah',
    'lxml',
    'feedparser'
]


datafiles_exts = [ '*.png', '*.svg', '*.tmpl', '*.css', '*.html', '*.js' ]


args = dict(name = 'smewt',
            version = '0.3',
            description = 'Smewt - a smart media manager.',
            long_description = README + '\n\n' + NEWS,
            classifiers = [], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
            keywords = 'smewt pygoo media manager video collection',
            author = 'Nicolas Wack, Ricard Marxer',
            author_email = 'wackou@gmail.com',
            url = 'http://www.smewt.com/',
            license = 'GPLv3',
            packages = find_packages(exclude = [ 'ez_setup', 'examples', 'tests', 'utils' ]),
            #package_data = dict((package, datafiles_exts) for package in find_packages()),
            include_package_data = True,
            scripts = [ 'bin/smewg' ],
            install_requires = install_requires
            )


if sys.platform == 'linux2':
    from setuptools.command.install import install
    import subprocess

    class SmewtInstall(install):
        def run(self):
            install.run(self)
            print 'Processing triggers for menu...'
            subprocess.call(['xdg-desktop-menu', 'install', 'packaging/linux/falafelton-smewt.desktop'])
            subprocess.call(['xdg-icon-resource', 'install', '--size', '128', 'smewt/icons/falafelton-smewt_128x128.png', 'falafelton-smewt'])
            if os.path.exists('/usr/bin/update-menus'):
                # Debian
                subprocess.call(['update-menus'])
            elif os.path.exists('/usr/bin/update-desktop-database'):
                # Ubuntu
                subprocess.call(['update-desktop-database'])

    # only try install icon and menu entry if we are root
    # (ie: do not do it when we install stuff in a virtualenv)
    if os.geteuid() == 0:
        args.update(dict(cmdclass = { 'install': SmewtInstall }))


if sys.platform == 'darwin':
    # py2app data
    OPTIONS = { 'argv_emulation': True,
                'iconfile': 'smewt/icons/smewt.icns',
                'packages': [ 'smewt', 'Cheetah', 'lxml', 'guessit' ],
                'frameworks': [ '/Developer/Applications/Qt/plugins/iconengines/libqsvgicon.dylib' ],
                'includes': [ 'sip', 'PyQt4', 'PyQt4.QtCore', 'PyQt4.QtGui', 'PyQt4.QtNetwork', 'PyQt4.QtWebKit',  'PyQt4.QtXml', 'PyQt4.QtSvg', 'ntpath' ],
                'excludes': [ 'PyQt4.QtDesigner', 'PyQt4.QtOpenGL', 'PyQt4.QtScript',
                              'PyQt4.QtSql', 'PyQt4.QtTest' ] # 'PyQt4.phonon'
                }

    args.update(dict(# for py2app
                     name = 'Smewt',
                     app = [ 'bin/smewg.py' ],
                     options = { 'py2app': OPTIONS,
                                 'plist': dict(CFBundleIdentifier = 'com.smewt.Smewt')
                                 },
                     setup_requires = [ 'py2app' ]
                     ))


if sys.platform == 'win32':
    import py2exe
    import glob
    from os.path import join

    allfiles = []
    for package in find_packages():
        datafiles = []
        root_path = package.replace('.', '\\')
        for pattern in datafiles_exts:
            datafiles += glob.glob(join(root_path, pattern))
        if datafiles:
            allfiles.append((root_path, datafiles))

    # also add qt plugins
    allfiles.append(('iconengines', glob.glob('C:\\Python27\\Lib\\site-packages\\PyQt4\\plugins\\iconengines\\*')))
    allfiles.append(('imageformats', glob.glob('C:\\Python27\\Lib\\site-packages\\PyQt4\\plugins\\imageformats\\*')))

    # add the open.exe utility program
    allfiles.append(('.', [ 'packaging\\win32\\open.exe' ]))

    from py2exe.build_exe import py2exe as build_exe
    import guessit

    class SmewtMediaCollector(build_exe):
        """Extension that copies smewt missing data."""
        def copy_extensions(self, extensions):
            """Copy the missing extensions."""
            build_exe.copy_extensions(self, extensions)

            # Create the media subdir where the
            # Python files are collected.
            media = 'guessit' # os.path.join('guessit')
            full = os.path.join(self.collect_dir, media)
            if not os.path.exists(full):
                self.mkpath(full)

            # Copy the media files to the collection dir.
            # Also add the copied file to the list of compiled
            # files so it will be included in zipfile.
            for f in glob.glob(guessit.__path__[0] + '/*.txt'):
                name = os.path.basename(f)
                self.copy_file(f, os.path.join(full, name))
                self.compiled_files.append(os.path.join(media, name))

    args.update(dict(windows = ['bin/smewg'],
                     cmdclass = { 'py2exe': SmewtMediaCollector },
                     data_files = allfiles,
                     options = { 'py2exe': { 'dll_excludes': 'MSVCP90.dll',
                                             'includes': [ 'sip',
                                                           'PyQt4.QtNetwork',
                                                           'Cheetah.DummyTransaction',
                                                           'lxml', 'lxml._elementpath'
                                                           ],
                                             'packages': [ 'smewt.3rdparty.periscope',
                                                           'BeautifulSoup' ]
                                             }}))


setup(**args)
