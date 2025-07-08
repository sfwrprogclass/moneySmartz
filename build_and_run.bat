@echo off
echo Building MoneySmartz executable...
pip install cx_Freeze pygame
python setup.py build
echo.
echo Build complete!
echo.
echo Starting MoneySmartz...
for /d %%i in (build\exe.win*) do (
    start "" "%%i\MoneySmartz.exe"
    goto :done
)
:done
echo.
echo If the game didn't start, please navigate to the build directory and run MoneySmartz.exe manually.
pause