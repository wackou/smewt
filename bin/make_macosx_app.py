#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

#os.system('rm -fr dist build')
#os.system('python setup.py py2app')


APPDIR = 'dist/Smewt.app'

os.system('cp -R /Developer/Applications/Qt/plugins/ %s/Contents/plugins' % APPDIR)

open('%s/Contents/Resources/qt.conf' % APPDIR, 'w').write('''[Paths]
qt_plugpath=plugins
''')

for MODULE in [ 'QtCore', 'QtGui', 'QtXml', 'QtSvg', 'QtNetwork', 'QtDBus' ]:
    os.system("find %s/Contents/plugins -type f -exec install_name_tool -change %s.framework/Versions/4/%s @executable_path/../Frameworks/%s.framework/Versions/4/%s {} ';'" % (APPDIR, MODULE, MODULE, MODULE, MODULE))


os.system("find %s/ -name \"*_debug\" -exec rm {} ';'")
'''
find dist/smewt.app/Contents/plugins -type f -exec install_name_tool -change QtGui.framework/Versions/4/QtGui @executable_path/../Frameworks/QtGui.framework/Versions/4/QtGui {} ';'

find dist/smewt.app/Contents/plugins -type f -exec install_name_tool -change QtCore.framework/Versions/4/QtCore @executable_path/../Frameworks/QtCore.framework/Versions/4/QtCore {} ';'

find dist/smewt.app/Contents/plugins -type f -exec install_name_tool -change QtCore.framework/Versions/4/QtCore @executable_path/../Frameworks/QtCore.framework/Versions/4/QtCore {} ';'

'''
                                                                                                                                                                       
