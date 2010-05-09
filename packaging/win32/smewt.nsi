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

Section 'Prerequisites' SecPrerequisites

  SetOutPath $INSTDIR\Prerequisites
  MessageBox MB_YESNO "Install Microsoft Visual Studio 2008 C-Runtime?" /SD IDYES IDNO endRedist
    File "vcredist_x86.exe"
    ExecWait "$INSTDIR\Prerequisites\vcredist_x86.exe"
    Goto endRedist

  endRedist:
SectionEnd


Section "Smewt GUI client" SecSmewt

  SetOutPath $INSTDIR
  File smewg.bat
  File smewg.vbs
  File smewt.ico
  File ${SMEWT_ROOT}\src\smewg.py
  File ${PYTHON_ROOT}\pythonw.exe

  ;Import main smewt module
  SetOutPath $INSTDIR\site-packages\smewt
  File /r /x *.pyc ${SMEWT_ROOT}\src\smewt\*.*
  
  ;Import dependencies

  ;Python stuff, this is ugly but hey, we're on windows after all...
  SetOutPath $INSTDIR\DLLs
  File C:\Windows\System32\python26.dll
  SetOutPath $INSTDIR\Lib
  File ${PYTHON_ROOT}\Lib\__future__.py
  File ${PYTHON_ROOT}\Lib\_abcoll.py
  File ${PYTHON_ROOT}\Lib\abc.py
  File ${PYTHON_ROOT}\Lib\base64.py
  File ${PYTHON_ROOT}\Lib\bisect.py
  File ${PYTHON_ROOT}\Lib\cgi.py
  File ${PYTHON_ROOT}\Lib\codecs.py
  File ${PYTHON_ROOT}\Lib\ConfigParser.py
  File ${PYTHON_ROOT}\Lib\copy.py
  File ${PYTHON_ROOT}\Lib\copy_reg.py
  File ${PYTHON_ROOT}\Lib\collections.py
  File ${PYTHON_ROOT}\Lib\dis.py
  File ${PYTHON_ROOT}\Lib\fnmatch.py
  File ${PYTHON_ROOT}\Lib\functools.py
  File ${PYTHON_ROOT}\Lib\genericpath.py
  File ${PYTHON_ROOT}\Lib\gettext.py
  File ${PYTHON_ROOT}\Lib\gzip.py
  File ${PYTHON_ROOT}\Lib\hashlib.py
  File ${PYTHON_ROOT}\Lib\heapq.py
  File ${PYTHON_ROOT}\Lib\httplib.py
  File ${PYTHON_ROOT}\Lib\inspect.py
  File ${PYTHON_ROOT}\Lib\keyword.py
  File ${PYTHON_ROOT}\Lib\linecache.py
  File ${PYTHON_ROOT}\Lib\locale.py
  File ${PYTHON_ROOT}\Lib\markupbase.py
  File ${PYTHON_ROOT}\Lib\md5.py
  File ${PYTHON_ROOT}\Lib\mimetools.py
  File ${PYTHON_ROOT}\Lib\ntpath.py
  File ${PYTHON_ROOT}\Lib\nturl2path.py
  File ${PYTHON_ROOT}\Lib\os.py
  File ${PYTHON_ROOT}\Lib\opcode.py
  File ${PYTHON_ROOT}\Lib\posixpath.py
  File ${PYTHON_ROOT}\Lib\pprint.py
  File ${PYTHON_ROOT}\Lib\Queue.py
  File ${PYTHON_ROOT}\Lib\random.py
  File ${PYTHON_ROOT}\Lib\re.py
  File ${PYTHON_ROOT}\Lib\rfc822.py
  File ${PYTHON_ROOT}\Lib\sgmllib.py
  File ${PYTHON_ROOT}\Lib\site.py
  File ${PYTHON_ROOT}\Lib\socket.py
  File ${PYTHON_ROOT}\DLLs\_socket.pyd
  File ${PYTHON_ROOT}\Lib\sre_compile.py
  File ${PYTHON_ROOT}\Lib\sre_constants.py
  File ${PYTHON_ROOT}\Lib\sre_parse.py
  File ${PYTHON_ROOT}\Lib\stat.py
  File ${PYTHON_ROOT}\Lib\string.py
  File ${PYTHON_ROOT}\Lib\StringIO.py
  File ${PYTHON_ROOT}\Lib\struct.py
  File ${PYTHON_ROOT}\Lib\subprocess.py
  File ${PYTHON_ROOT}\Lib\tempfile.py
  File ${PYTHON_ROOT}\Lib\token.py
  File ${PYTHON_ROOT}\Lib\tokenize.py
  File ${PYTHON_ROOT}\Lib\traceback.py
  File ${PYTHON_ROOT}\Lib\threading.py
  File ${PYTHON_ROOT}\Lib\types.py
  File ${PYTHON_ROOT}\Lib\urlparse.py
  File ${PYTHON_ROOT}\Lib\urllib.py
  File ${PYTHON_ROOT}\Lib\urllib2.py
  File ${PYTHON_ROOT}\Lib\UserDict.py
  File ${PYTHON_ROOT}\Lib\warnings.py
  File ${PYTHON_ROOT}\Lib\weakref.py
  SetOutPath $INSTDIR\Lib\encodings
  File ${PYTHON_ROOT}\Lib\encodings\*.py
  SetOutPath $INSTDIR\Lib\logging
  File ${PYTHON_ROOT}\Lib\logging\*.py

  ;3rdparty modules
  SetOutPath $INSTDIR\site-packages
  File ${PYTHON_PACKAGES}\pycurl.pyd
  File ${PYTHON_PACKAGES}\feedparser.py
  SetOutPath $INSTDIR\site-packages\Cheetah
  File /r ${PYTHON_PACKAGES}\Cheetah\*.py
  SetOutPath $INSTDIR\site-packages\lxml
  File /r ${PYTHON_PACKAGES}\lxml\*.py
  File /r ${PYTHON_PACKAGES}\lxml\*.pyd
  SetOutPath $INSTDIR\site-packages\imdb
  File /r ${PYTHON_PACKAGES}\imdb\*.py
  File /r ${PYTHON_PACKAGES}\imdb\*.pyd



  ;PyQt4 python modules
  SetOutPath $INSTDIR\site-packages
  File ${PYTHON_PACKAGES}\sip.pyd
  SetOutPath $INSTDIR\site-packages\PyQt4
  File ${PYTHON_PACKAGES}\PyQt4\__init__.py
  File ${PYTHON_PACKAGES}\PyQt4\QtCore.pyd
  File ${PYTHON_PACKAGES}\PyQt4\QtGui.pyd
  File ${PYTHON_PACKAGES}\PyQt4\QtSvg.pyd
  File ${PYTHON_PACKAGES}\PyQt4\QtWebKit.pyd
  File ${PYTHON_PACKAGES}\PyQt4\QtNetwork.pyd

  ;PyQt4 required DLLs
  SetOutPath $INSTDIR\DLLs
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


Section "Start Menu Shortcuts" SecMenu

  CreateDirectory "$SMPROGRAMS\Smewt"
  SetOutPath $INSTDIR
  CreateShortCut "$SMPROGRAMS\Smewt\Smewt.lnk" "$INSTDIR\smewg.vbs" "" "$INSTDIR\smewt.ico" 0
  CreateShortCut "$SMPROGRAMS\Smewt\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0

SectionEnd


;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_SecSmewt ${LANG_ENGLISH} "The main Smewt program."
  LangString DESC_SecPrerequisites ${LANG_ENGLISH} "The Visual Studio 2008 C runtime. If you don't know what that is, you probably need to install it."
  LangString DESC_SecMenu ${LANG_ENGLISH} "Install Start menu shortcuts."

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecSmewt} $(DESC_SecSmewt)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecPrerequisites} $(DESC_SecPrerequisites)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecMenu} $(DESC_SecMenu)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  Delete "$INSTDIR\Uninstall.exe"

  ; Remove shortcuts, if any
  Delete "$SMPROGRAMS\Smewt\*.*"
  RMDir "$SMPROGRAMS\Smewt"

  RMDir /r /REBOOTOK $INSTDIR

  DeleteRegKey /ifempty HKCU "Software\Smewt"

SectionEnd
