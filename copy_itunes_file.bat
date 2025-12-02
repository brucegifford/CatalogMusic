@echo off

:: ----------------------------------------
:: Source folder (same for all machines)
:: ----------------------------------------
set "SRC_DIR=%USERPROFILE%\Music\iTunes"

:: Files to copy (quotes preserved)
set FILES="iTunes Music Library.xml" "Library.xml"

:: ----------------------------------------
:: Determine destination based on machine/user
:: ----------------------------------------
set "DEST="

:: Case-insensitive checks (THUNDER / bruce → Thunder folder)
if /I "%COMPUTERNAME%"=="THUNDER" if /I "%USERNAME%"=="bruce" (
    set "DEST=C:\dev\CatalogMusic\iTunesData\Thunder"
)

:: Case-insensitive checks (HC-WKS-52437967 / a4n1czz → 3MH1LT folder)
if /I "%COMPUTERNAME%"=="HC-WKS-52437967" if /I "%USERNAME%"=="a4n1czz" (
    set "DEST=C:\dev\CatalogMusic\iTunesData\3MH1LT"
)

:: No matching condition → exit silently
if "%DEST%"=="" exit /b

:: Ensure destination exists
if not exist "%DEST%" mkdir "%DEST%"

:: ----------------------------------------
:: Loop through files
:: %%F includes the quotes, exactly as required
:: ----------------------------------------
for %%F in (%FILES%) do (
    robocopy "%SRC_DIR%" "%DEST%" %%F /XO
)

pause

exit /b
