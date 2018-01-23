@echo off
title MICROBLOG Flask Server
pushd
d:
cd d:\python34\microblog
call .\venv\scripts\activate.bat

rem set MAIL_SERVER=smtp.googlemail.com
rem set MAIL_PORT=587
rem set MAIL_USE_TLS=1
rem set MAIL_USERNAME=syktyvkarec@gmail.com
rem set MAIL_PASSWORD=*****

set FLASK_APP=microblog.py
set FLASK_DEBUG=1
:1
flask run
rem cmd
goto 1
call .\venv\scripts\deactivate.bat
popd