rmdir /S /Q dist
rmdir /S /Q build
C:\Python27\python.exe setup.py py2exe
cd packaging\win32
"C:\Program Files\NSIS\makensis.exe" smewt.nsi
cd ..\..