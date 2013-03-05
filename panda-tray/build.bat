@echo off

rem pull the version from version.py
FOR /F "tokens=3" %%i in (version.py) DO set version = %%i

set pandapfx=C:\Temp\panda.pfx
set zip="C:\Program Files (x86)\7-Zip\7z.exe"
IF "%1"=="installer" GOTO inno
IF "%1"=="sign" GOTO sign
IF "%1"=="distfile" GOTO distfile
goto py2exe

:py2exe
rem ##################################
rem compile python to exe using py2exe
rem ##################################
rem you need to install py2exe
rmdir /s /q dist
python setup.py py2exe
goto end

:sign
echo off
echo F.Y.I: You need to have 7zip installed
echo F.Y.I: You need to specify the version in version.py
set zipfile="dist\Digital Panda Tray Application-%version%.win32.zip"
echo "signing executables"
rem "C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\Bin\signtool.exe" sign /f %pandapfx% /p %2 "dist\*.exe"
echo "re-creating zip file"
del %zipfile%
set f1=".\dist\*.exe"
set f2=".\dist\*.zip"
set f3=".\dist\gfx"
%zip% a -r -tzip -mx9 %zipfile% %f1% %f2% %f3%
goto end

:distfile
python build_panda.py version
goto end


:inno
echo "F.Y.I: you need to install innosetup and have the pfx file in the correct place!"
del "Output\setup.exe"
"c:\Program Files (x86)\Inno Setup 5\ISCC.exe" "/sStandard=$qC:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\Bin\signtool.exe$q sign /f %pandapfx% /p %2 /d $qDigital Panda - Cloud Storage Synchronisation Client$q $f" installer.iss
del "Output\Setup.Digital Panda Tray Application-%version%.win32.exe"
rename "Output\setup.exe" "Setup.Digital Panda Tray Application-%version%.win32.exe"
goto end

:end