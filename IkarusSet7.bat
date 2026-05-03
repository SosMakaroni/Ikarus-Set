chcp 65001

setlocal enabledelayedexpansion

set "filename=%~n0"
set "path=%~dp0"

del "%path%\%filename%.nml"
copy /b "%path%\Vehicles_code\*.nml" "%path%\%filename%.nml"

C:\Users\balin\AppData\Local\Microsoft\WindowsApps\python.exe version.py

C:\Users\balin\AppData\Local\Microsoft\WindowsApps\python.exe C:\Users\balin\nml\nmlc -c --grf %filename%.grf %filename%.nml
rd /s /q ".nmlcache\"
copy "%filename%.grf" "C:\Users\Balin\Documents\OpenTTD\content_download\newgrf"
pause>nul
