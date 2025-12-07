
@echo off

rem Specify the directory containing your .ui files here
set "directory=C:\PythonProjects\EvonyTools\ActiveGenerals"

for /f "tokens=*" %%a in ('dir /b /a-d "%directory%\*.ui"') do (
  echo ***** Processing file: "%%a"  *****
  @echo off
  pyuic5 "%directory%\%%a" -o "%directory%\%%~na_ui.py"
)

echo Finished processing .ui files.

pause