#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os


def build_macosx_app():
    os.system('rm -fr dist build')
    os.system('cp bin/smewg bin/smewg.py')
    os.system('python setup.py py2app')


    APPDIR = 'dist/Smewt.app'

    os.system('cp -R /Developer/Applications/Qt/plugins/ %s/Contents/plugins' % APPDIR)

    open('%s/Contents/Resources/qt.conf' % APPDIR, 'w').write('''[Paths]
qt_plugpath=plugins
''')

    for MODULE in [ 'QtCore', 'QtGui', 'QtXml', 'QtSvg', 'QtNetwork', 'QtDBus' ]:
        os.system("find %s/Contents/plugins -type f -exec install_name_tool -change %s.framework/Versions/4/%s @executable_path/../Frameworks/%s.framework/Versions/4/%s {} ';'" % (APPDIR, MODULE, MODULE, MODULE, MODULE))


    os.system("find %s/ -name \"*_debug\" -exec rm {} ';'" % APPDIR)


def build_dmg():
    import sys
    sys.path.append('.')
    import smewt
    DMG_NAME = 'dist/Smewt_%s.dmg' % smewt.__version__

    print 'building DMG...'
    os.system('rm -fr dist/smewt_dmg dist/tmp_smewt.dmg %s' % DMG_NAME)
    os.system('mkdir dist/smewt_dmg')

    print 'Copying files...'
    os.system('cp packaging/macosx/dmg_skeleton/Applications dist/smewt_dmg/')
    os.system('cp packaging/macosx/dmg_skeleton/_DS_Store dist/smewt_dmg/.DS_Store')
    os.system('cp -r packaging/macosx/dmg_skeleton/_background dist/smewt_dmg/.background')
    os.system('cp -a dist/Smewt.app dist/smewt_dmg/')

    print 'Making hybrid DMG...'
    os.system('hdiutil makehybrid -hfs -hfs-volume-name Smewt -hfs-openfolder dist/smewt_dmg dist/smewt_dmg -o dist/tmp_smewt.dmg')

    print 'Optimizing DMG...'
    os.system('hdiutil convert -format UDZO dist/tmp_smewt.dmg -o %s' % DMG_NAME)

    print 'All done! The final DMG is in %s' % DMG_NAME

def cleanup():
    os.system('rm bin/smewg.py')


if __name__ == '__main__':
    build_macosx_app()
    build_dmg()
    cleanup()
