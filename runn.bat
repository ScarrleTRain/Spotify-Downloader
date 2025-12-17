@echo off
setlocal enabledelayedexpansion

:home
cls
set return=""


call :choose "Sync/Add/Del/Exit: ",return

if /I "%return%"=="Sync" goto :sync
if /I "%return%"=="S"    goto :sync
if /I "%return%"=="Add"  goto :add
if /I "%return%"=="A"    goto :add
if /I "%return%"=="Del"  goto :del
if /I "%return%"=="D"    goto :del
if /I "%return%"=="Exit" goto :end
if /I "%return%"=="E"    goto :end

:: Restart the selection
echo Invalid Input
pause
goto :home

:: Code to handle syncing files in folder
:sync
    cls
    call :display_folders
    call :choose "Select the numbers of the folders you would like to sync, seperated by spaces: ",return
    set folder_choice=%return%

    for %%a in (%folder_choice%) do (
        set folder_name=""
        call :num_to_folder %%a,folder_name
        echo !folder_name!
    )
goto :end

:: Code to handle adding new folders
:add
    cls

goto :end

:: Code to handle deleting folders
:del
    cls
    call :display_folders
    call :choose "Select the numbers of the folders you would like to delete, seperated by spaces: ",return
    set folder_choice=%return%

    for %%a in (%folder_choice%) do (
        cls
        set folder_name=""
        call :num_to_folder %%a,folder_name
        call :choose "Confirm deletion of folder !folder_name! [Y/N]: ",return
        echo !return!
        if /I "!return!"=="Y" (
            echo Deleting !folder_name!
            cd Folders
            rmdir /s /q "!folder_name!" 2>nul
            cd ..
            pause
        ) else ( 
            echo Cancelled deletion of !folder_name!
            pause
        ) 
    )
goto :home

:end
    if exist folder.tempdat ( del folders.tempdat )
exit /b 0

::FUNCTIONS BELOW
::----------------------------------------------------------------

:: Display folders in Folders directory
:display_folders
    dir Folders /a:d /b > folders.tempdat
    set count=1
    for /f "tokens=1 delims=^?" %%a in (folders.tempdat) do (
        echo !count!^) %%a
        set /A count=count+1
    )
exit /b 0

:: Get output for input nicely
:choose
    set /p %~2=%~1
exit /b 0

:num_to_folder
    set count=1
    for /f "tokens=1 delims=^?" %%a in (folders.tempdat) do (
        if "%~1"=="!count!" (
            set %~2=%%a
        )
        set /A count=!count!+1
    )
exit /b 0
