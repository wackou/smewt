;Smewt main installer
;Written by Nicolas Wack <wackou@gmail.com>
;
;Inspired by:
;NSIS Modern User Interface
;Basic Example Script
;Written by Joost Verburg

;--------------------------------
;Include Modern UI

  !include "MUI2.nsh"

;--------------------------------
;General

  ;Name and file
  Name "Smewt"
  !define VERSION '0.2' 
  !define SMEWT_ROOT '..\..'
  !define PYTHON_ROOT 'C:\Python26'
  !define PYTHON_PACKAGES '${PYTHON_ROOT}\Lib\site-packages'

  OutFile "smewt_${VERSION}_setup.exe"

  ;Default installation folder
  InstallDir "$PROGRAMFILES\Smewt"
  
  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\Smewt" ""

  ;Request application privileges for Windows Vista
  RequestExecutionLevel user

  ;Useful to disable compression under development
  SetCompress off


;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_LICENSE "${NSISDIR}\Docs\Modern UI\License.txt"
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  
;--------------------------------
;Languages
 
  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section "Smewt GUI client" SecSmewt

  SetOutPath $INSTDIR
  File smewg.bat
  File ${SMEWT_ROOT}\src\smewg.py
  File ${PYTHON_ROOT}\pythonw.exe

  ;Import main smewt module
  SetOutPath $INSTDIR\site-packages\smewt
  File /r /x *.pyc ${SMEWT_ROOT}\src\smewt\*.*
  
  ;Import dependencies
  
  ;PyQt4 python modules
  SetOutPath $INSTDIR\site-packages\PyQt4
  File ${PYTHON_PACKAGES}\PyQt4\__init__.py
  File ${PYTHON_PACKAGES}\PyQt4\QtCore.pyd
  File ${PYTHON_PACKAGES}\PyQt4\QtGui.pyd
  File ${PYTHON_PACKAGES}\PyQt4\QtSvg.pyd
  File ${PYTHON_PACKAGES}\PyQt4\QtWebKit.pyd
  File ${PYTHON_PACKAGES}\PyQt4\QtNetwork.pyd

  ;PyQt4 required DLLs
  SetOutPath $INSTDIR\DLLs
  File C:\Windows\System32\python26.dll
  File ${PYTHON_PACKAGES}\PyQt4\bin\libgcc_s_dw2-1.dll
  File ${PYTHON_PACKAGES}\PyQt4\bin\mingwm10.dll
  File ${PYTHON_PACKAGES}\PyQt4\bin\QtCore4.dll
  File ${PYTHON_PACKAGES}\PyQt4\bin\QtGui4.dll
  File ${PYTHON_PACKAGES}\PyQt4\bin\QtSvg4.dll
  File ${PYTHON_PACKAGES}\PyQt4\bin\QtWebKit4.dll
  File ${PYTHON_PACKAGES}\PyQt4\bin\QtNetwork4.dll
  File ${PYTHON_PACKAGES}\PyQt4\bin\QtXmlPatterns4.dll
  File ${PYTHON_PACKAGES}\PyQt4\bin\phonon4.dll
  SetOutPath $INSTDIR\imageformats
  File ${PYTHON_PACKAGES}\PyQt4\plugins\imageformats\*.*
  
  ;Store installation folder
  WriteRegStr HKCU "Software\Smewt" "" $INSTDIR
  
  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd

;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_SecSmewt ${LANG_ENGLISH} "The main Smewt program."

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecSmewt} $(DESC_SecSmewt)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  Delete "$INSTDIR\Uninstall.exe"

  RMDir /r /REBOOTOK $INSTDIR

  DeleteRegKey /ifempty HKCU "Software\Smewt"

SectionEnd
