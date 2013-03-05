@echo off
IF "%1"=="installer" GOTO inno
IF "%1"=="sign" GOTO sign
goto py2exe

:py2exe
rem ##################################
rem compile python to exe using py2exe
rem ##################################
rem you need to install py2exe
rmdir /s /q dist
python setup.py py2exe
rename dist\auto_update.exe panda-tray.exe
goto end

:sign
goto end

:inno
goto end

:end