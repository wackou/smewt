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
  !define VERSION  '0.3'
  !define SMEWT_ROOT '..\..'
  ; comment this, we don't want to run smewg the first time as admin on windows 7
  ; TODO: is this really necessary or are we being too cautious?
  ;!define MUI_FINISHPAGE_RUN '$INSTDIR\smewg.exe'

  OutFile "smewt_${VERSION}_setup.exe"

  ;Default installation folder
  InstallDir "$PROGRAMFILES\Smewt"

  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\Smewt" ""

  ;Request application privileges for Windows Vista / 7 to install in Program Files
  RequestExecutionLevel admin

  ;Useful to disable compression under development
  ;SetCompress off


;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING


;--------------------------------
;Pages

  !insertmacro MUI_PAGE_LICENSE "${SMEWT_ROOT}\COPYING"
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  !insertmacro MUI_PAGE_FINISH

  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
;Languages

  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

;Section 'Prerequisites' SecPrerequisites

;  SetOutPath $INSTDIR\Prerequisites
;  MessageBox MB_YESNO "Install Microsoft Visual Studio 2008 C-Runtime?" /SD IDYES IDNO endRedist
;    File "vcredist_x86.exe"
;    ExecWait "$INSTDIR\Prerequisites\vcredist_x86.exe"
;    Goto endRedist

;  endRedist:
;SectionEnd


Section "Smewt GUI client" SecSmewt

  SetOutPath $INSTDIR
  File smewt.ico
  File ${SMEWT_ROOT}\dist\*.exe
  File ${SMEWT_ROOT}\dist\*.pyd
  File ${SMEWT_ROOT}\dist\*.dll
  File ${SMEWT_ROOT}\dist\library.zip

  File /r ${SMEWT_ROOT}\dist\iconengines
  File /r ${SMEWT_ROOT}\dist\imageformats
  File /r ${SMEWT_ROOT}\dist\smewt

  ;Store installation folder
  WriteRegStr HKCU "Software\Smewt" "" $INSTDIR

  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd


Section "Start Menu Shortcuts" SecMenu

  CreateDirectory "$SMPROGRAMS\Smewt"
  SetOutPath $INSTDIR
  CreateShortCut "$SMPROGRAMS\Smewt\Smewt.lnk" "$INSTDIR\smewg.exe" "" "$INSTDIR\smewt.ico" 0
  CreateShortCut "$SMPROGRAMS\Smewt\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0

SectionEnd


;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_SecSmewt ${LANG_ENGLISH} "The main Smewt program."
  ;LangString DESC_SecPrerequisites ${LANG_ENGLISH} "The Visual Studio 2008 C runtime. If you don't know what that is, you probably need to install it."
  LangString DESC_SecMenu ${LANG_ENGLISH} "Install Start menu shortcuts."

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecSmewt} $(DESC_SecSmewt)
    ;!insertmacro MUI_DESCRIPTION_TEXT ${SecPrerequisites} $(DESC_SecPrerequisites)
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
