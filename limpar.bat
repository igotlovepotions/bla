@echo off
cd /d "%~dp0"

if exist results rmdir /s /q results
mkdir results

for %%N in (1 2 3 4 5 5.1 6 7 8 9) do mkdir "results\%%N"

echo Pasta results recriada com as subpastas 1 a 9 e 5.1.
pause