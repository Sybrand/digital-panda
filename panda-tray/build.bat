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

:esky
rem you need to install py2exe and esky
python setup.py bdist_esky
goto inno

:inno
rem you need to install innosetup

goto end

:wix
rem ################
rem create installer
rem ################
rem you need to install Wix
rem "C:\Program Files (x86)\WiX Toolset v3.7\bin\candle.exe" -nologo "digitalpanda.wxs" -out "digitalpanda.wixobj"  -ext WixUtilExtension  -ext WixUIExtension
rem "C:\Program Files (x86)\WiX Toolset v3.7\bin\light.exe" -nologo "digitalpanda.wixobj" -out "digitalpanda.msi"  -ext WixUtilExtension  -ext WixUIExtension

:end