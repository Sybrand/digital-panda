@echo off
set pandapfx=C:\Temp\panda.pfx
set version=0.16
set zip="C:\Program Files (x86)\7-Zip\7z.exe"
IF "%1"=="installer" GOTO inno
IF "%1"=="sign" GOTO sign
goto esky

:py2exe
rem ##################################
rem compile python to exe using py2exe
rem ##################################
rem you need to install py2exe
rem rmdir /s /q dist
python setup.py py2exe
mkdir dist\gfx
copy gfx\digital-panda-icon.ico dist\gfx\
copy gfx\digital-panda-online-1616.png dist\gfx\
copy gfx\icon1616.png dist\gfx\
copy gfx\connection-ok.png dist\gfx\
copy gfx\digital-panda-header.png dist\gfx\
copy gfx\digital-panda-online-1616.png dist\gfx\
copy gfx\digital-panda-menu-graphic.png dist\gfx\
rename dist\panda-tray-w.exe panda-tray.exe
goto end

:sign
echo off
echo F.Y.I: You need to have 7zip installed
echo F.Y.I: You need to specify the version
set zipfile="dist\Digital Panda Tray Application-%version%.win32.zip"
echo delete previous directory
rmdir /s /q "dist\Digital Panda Tray Application-%version%.win32"
echo unzipping %zipfile%
%zip% x -odist -y %zipfile%
echo "signing executables"
"C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\Bin\signtool.exe" sign /f %pandapfx% /p %2 "dist\panda-tray-w.exe"
"C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\Bin\signtool.exe" sign /f %pandapfx% /p %2 "dist\Digital Panda Tray Application-%version%.win32\panda-tray-w.exe"
"C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\Bin\signtool.exe" sign /f %pandapfx% /p %2 "dist\*.dll"
"C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\Bin\signtool.exe" sign /f %pandapfx% /p %2 "dist\Digital Panda Tray Application-%version%.win32\*.dll"
echo "re-creating zip file"
del %zipfile%
set f1=".\dist\Digital Panda Tray Application-%version%.win32\panda-tray-w.exe"
set f2=".\dist\Digital Panda Tray Application-%version%.win32\python27.dll"
set f3=".\dist\Digital Panda Tray Application-%version%.win32"
%zip% a -r -tzip -mx9 %zipfile% %f1% %f2% %f3%
goto end


:esky
rem you need to install py2exe and esky
python setup.py bdist_esky
goto end

:inno
echo "F.Y.I: you need to install innosetup and have the pfx file in the correct place!"
del "Output\setup.exe"
"c:\Program Files (x86)\Inno Setup 5\ISCC.exe" "/sStandard=$qC:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\Bin\signtool.exe$q sign /f %pandapfx% /p %2 /d $qDigital Panda - Cloud Storage Synchronisation Client$q $f" installer.iss
del "Output\Setup.Digital Panda Tray Application-%version%.win32.exe"
rename "Output\setup.exe" "Setup.Digital Panda Tray Application-%version%.win32.exe"
goto end

:wix
rem ################
rem create installer
rem ################
rem you need to install Wix
rem "C:\Program Files (x86)\WiX Toolset v3.7\bin\candle.exe" -nologo "digitalpanda.wxs" -out "digitalpanda.wixobj"  -ext WixUtilExtension  -ext WixUIExtension
rem "C:\Program Files (x86)\WiX Toolset v3.7\bin\light.exe" -nologo "digitalpanda.wixobj" -out "digitalpanda.msi"  -ext WixUtilExtension  -ext WixUIExtension

:end