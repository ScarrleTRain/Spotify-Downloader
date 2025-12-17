@echo off
setlocal enabledelayedexpansion
cls

:: Run Python script to choose user
python chooseUser.py
if %errorlevel%==0 (
    :: Read user ID from temp file and delete it
    set /p userId=<.tempdat
    del .tempdat

    :: Get playlist links for the selected user
    python getLinks.py !userId!
    if errorlevel 1 exit /b !errorlevel!
) else if %errorlevel%==2 (
    echo Continuing with previously selected playlists.
) else if %errorlevel%==1 (
    exit /b
)

:: Prompt user for download confirmation
set /p "downloadConfirmation=Would you like to download now (Y/N): "
if /I not "%downloadConfirmation%"=="Y" (
    echo Skipping download.
    exit /b
)

:: Check required Python modules
call :check_module spotdl
call :check_module spotipy
call :check_module emoji

:: Ensure 'Folders' directory exists and change into it
if not exist "Folders" mkdir "Folders"
cd "Folders"

:: Set path to CSV file containing playlist names and links
set "csv_file=..\playlist_links.csv"

:: Loop through CSV file and download each playlist
for /f "tokens=1,2 delims=," %%a in (%csv_file%) do (
    set "playlist_name=%%a"
    set "playlist_link=%%b"

    echo Beginning "!playlist_name!" download...

    rmdir /s /q "!playlist_name!" 2>nul
    mkdir "!playlist_name!" 2>nul
    cd "!playlist_name!"
    python -m spotdl !playlist_link! --ffmpeg-args "-b:a 320k" --threads 4 --cache-path "../.spotdl-cache" --preload --log-level INFO
    echo Finished downloading "!playlist_name!"
    cd ..
)

cd ..
pause
exit /b

:: Function to check if a Python module is installed, and install it if missing
:check_module
python -c "import %1" >nul 2>&1
if errorlevel 1 (
    echo %1 not found, installing...
    python -m pip install --user %1
)
exit /b