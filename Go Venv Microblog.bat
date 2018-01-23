@echo off
title CMD in Microblog environment
pushd
d:
cd d:\python34\microblog
call .\venv\scripts\activate.bat
set FLASK_APP=microblog.py

cmd

call .\venv\scripts\deactivate.bat
popd