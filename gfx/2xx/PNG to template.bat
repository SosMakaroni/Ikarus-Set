@echo off
rem Ellenőrizzük, hogy húztak-e rá fájlt
if "%~1" == "" (
    echo Huzz egy vagy tobb PNG kepet erre a fajlra!
    pause
    exit /b
)

echo Feldolgozas folyamatban...

rem Vegig megyunk az osszes rahuzott fajlon
for %%i in (%*) do (
    echo Feldolgozas: %%~nxi
    python png_to_temp.py "%%~i"
)

echo.
echo Minden fajl kesz!
pause