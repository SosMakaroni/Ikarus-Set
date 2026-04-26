@echo off
rem Ellenőrizzük, hogy húztak-e rá fájlt
if "%~1"=="" (
    echo Huzz egy PNG kepet erre a fajlra!
    pause
    exit /b
)

rem A Python szkript futtatása a kép elérési útjával
python png_to_temp.py "%~1"

pause