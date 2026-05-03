@echo off
REM run_assets_fixed.bat

IF "%~1"=="" (
    echo Használat: %~nx0 ExcelFajl.xlsx [--nml] [--lng] [--sort]
    pause
    goto :eof
)

REM Így a %* tartalmazza a fájlnevet és minden egyéb kapcsolót egyszer
python excel_to_assets.py %*
pause
