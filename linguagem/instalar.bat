@echo off
setlocal
set "ROOT=%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  set "PYTHON=py"
) else (
  set "PYTHON=python"
)
%PYTHON% "%ROOT%hzhon_cli.py" %*
endlocal