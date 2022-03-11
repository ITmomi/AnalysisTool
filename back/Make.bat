@ECHO off
SETLOCAL

SET WD=%CD%
SET "BUILDROOT=%WD%\win-build"
SET "DISTROOT=%WD%\dist"

SET CMDOPTIONS=""
IF "%1" == "clean" SET CMDOPTIONS="VALID"
IF "%1" == ""      SET CMDOPTIONS="VALID"

IF NOT %CMDOPTIONS%=="VALID" (
    GOTO USAGE
)

IF "%1" == "clean" (
    CALL :CLEAN
    EXIT /B %ERRORLEVEL%
)

set "ARCHITECTURE=x64"
if "%Platform%" == "X86" (
    set "ARCHITECTURE=x86"
)

REM Main build sequence
CALL :SET_ENVIRONMENT
CALL :VALIDATE_ENVIRONMENT || EXIT /B 1
CALL :CLEAN || EXIT /B 1
CALL :CREATE_VIRTUAL_ENV || EXIT /B 1
CALL :CREATE_REACT_ENV || EXIT /B 1
CALL :CREATE_PYTHON_ENV || EXIT /B 1
CALL :CLEANUP_ENV || EXIT /B 1
CALL :CREATE_INSTALLER || EXIT /B 1


EXIT /B %ERRORLEVEL%
REM Main build sequence Ends


:CLEAN
    ECHO Removing build directory...
    IF EXIST "%BUILDROOT%" RD "%BUILDROOT%" /S /Q > nul || EXIT /B 1

    ECHO Removing temp build directory...
    IF EXIST "%WD%\installer\Output" rd "%WD%\installer\Output" /S /Q > nul || EXIT /B 1

    ECHO Removing installer configuration script...
    IF EXIST DEL /q "%WD%\installer\installer.iss" > nul || EXIT /B 1

    EXIT /B 0
	

:SET_ENVIRONMENT
    ECHO Configuring the environment...
    IF "%ANALYSISTOOL_PYTHON_DIR%" == ""   SET "ANALYSISTOOL_PYTHON_DIR=C:\Python39"
	IF "%ANALYSISTOOL_INNOTOOL_DIR%" == "" SET "ANALYSISTOOL_INNOTOOL_DIR=C:\Program Files (x86)\Inno Setup 6"
	
	REM Set additional variables we need
    FOR /F "tokens=3" %%a IN ('findstr /C:"APP_MAJOR =" %WD%\config\app_config.py')  DO SET APP_MAJOR=%%a
    FOR /F "tokens=3" %%a IN ('findstr /C:"APP_MINOR =" %WD%\config\app_config.py') DO SET APP_MINOR=%%a
    FOR /F "tokens=3" %%a IN ('findstr /C:"APP_REVISION =" %WD%\config\app_config.py')   DO SET APP_REVISION=%%a
	SET APP_VERSION=%APP_MAJOR%.%APP_MINOR%.%APP_REVISION%
	SET APP_NAME=""
    FOR /F "tokens=2* DELims='" %%a IN ('findstr /C:"APP_NAME =" %WD%\config\app_config.py') DO SET APP_NAME=%%a
	SET INSTALLERNAME=%APP_NAME%_%APP_VERSION%_installer_%ARCHITECTURE%.exe
       
    REM get Python version for the runtime build ex. 2.7.1 will be 27
    FOR /f "tokens=1 DELims=." %%G IN ('%ANALYSISTOOL_PYTHON_DIR%/python.exe -c "import sys; print(sys.version.split(' ')[0])"') DO SET PYTHON_MAJOR=%%G
    FOR /f "tokens=2 DELims=." %%G IN ('%ANALYSISTOOL_PYTHON_DIR%/python.exe -c "import sys; print(sys.version.split(' ')[0])"') DO SET PYTHON_MINOR=%%G
    SET "PYTHON_VERSION=%PYTHON_MAJOR%%PYTHON_MINOR%"

    EXIT /B 0


:VALIDATE_ENVIRONMENT
    ECHO ****************************************************************
    ECHO * Build summary
    ECHO ****************************************************************
    ECHO Build path:                %BUILDROOT%
    ECHO Output directory:          %DISTROOT%
    ECHO Installer name:            %INSTALLERNAME%
    ECHO.
    ECHO Python directory:          %ANALYSISTOOL_PYTHON_DIR%
    ECHO Python DLL:                %ANALYSISTOOL_PYTHON_DIR%\Python%PYTHON_VERSION%.dll
    ECHO Python version:            %PYTHON_MAJOR%.%PYTHON_MINOR%
    ECHO.
    ECHO InnoTool directory:        %ANALYSISTOOL_INNOTOOL_DIR%
    ECHO.
    ECHO App version:               %APP_VERSION%
    ECHO App name:                  %APP_NAME%
    ECHO ****************************************************************

    ECHO Checking the environment...
    IF NOT EXIST "%ANALYSISTOOL_INNOTOOL_DIR%" (
        ECHO !ANALYSISTOOL_INNOTOOL_DIR! does not exist
        ECHO Please install InnoTool and set the ANALYSISTOOL_INNOTOOL_DIR environment variable.
        EXIT /B 1
    )

    IF NOT EXIST "%ANALYSISTOOL_PYTHON_DIR%" (
        ECHO !ANALYSISTOOL_PYTHON_DIR! does not exist.
        ECHO Please install Python and set the ANALYSISTOOL_PYTHON_DIR environment variable.
        EXIT /B 1
    )

    IF NOT EXIST "%ANALYSISTOOL_PYTHON_DIR%\Python%PYTHON_VERSION%.dll" (
        ECHO !ANALYSISTOOL_PYTHON_DIR!\Python!PYTHON_VERSION!.dll does not exist.
        ECHO Please check your Python installation is complete.
        EXIT /B 1
    )

    IF NOT EXIST "%ANALYSISTOOL_PYTHON_DIR%\Scripts\virtualenv.exe" (
        ECHO !ANALYSISTOOL_PYTHON_DIR!\Scripts\virtualenv.exe does not exist.
        ECHO Please install the virtualenv package in Python.
        EXIT /B 1
    )

    EXIT /B 0


:CREATE_VIRTUAL_ENV
    ECHO Creating virtual environment...
    IF NOT EXIST "%BUILDROOT%"  MKDIR "%BUILDROOT%"
    
    CD "%BUILDROOT%"

    REM Note that we must use virtualenv.exe here, as the venv module doesn't allow python.exe to relocate.
    "%ANALYSISTOOL_PYTHON_DIR%\Scripts\virtualenv.exe" venv

    XCOPY /S /I /E /H /Y "%ANALYSISTOOL_PYTHON_DIR%\DLLs" "%BUILDROOT%\venv\DLLs" > nul || EXIT /B 1
    XCOPY /S /I /E /H /Y "%ANALYSISTOOL_PYTHON_DIR%\Lib" "%BUILDROOT%\venv\Lib" > nul || EXIT /B 1

    ECHO Activating virtual environment -  %BUILDROOT%\venv...
    CALL "%BUILDROOT%\venv\Scripts\activate" || EXIT /B 1

    ECHO Installing dependencies...
    CALL pip install --trusted-host files.pythonhosted.org -r "%WD%\requirements.txt" || EXIT /B 1
    

    CD %WD%
    EXIT /B 0


:CREATE_REACT_ENV
    MKDIR "%BUILDROOT%\runtime"

    CD "%WD%\..\front"

    ECHO Installing javascript dependencies...
    CALL yarn config set "strict-ssl" false -g || EXIT /B 1
    CALL yarn install || EXIT /B 1

    ECHO Bundling javascript...
    CALL yarn build || EXIT /B 1

    CD %WD%
    EXIT /B 0
    

:CREATE_PYTHON_ENV
    ECHO Staging Python...	
	IF NOT EXIST "%BUILDROOT%\runtime"  MKDIR "%BUILDROOT%\runtime"
	
    COPY %ANALYSISTOOL_PYTHON_DIR%\python%PYTHON_VERSION%.dll "%BUILDROOT%\runtime"  > nul || EXIT /B 1
    COPY %ANALYSISTOOL_PYTHON_DIR%\python.exe "%BUILDROOT%\runtime" > nul || EXIT /B 1
    COPY %ANALYSISTOOL_PYTHON_DIR%\pythonw.exe "%BUILDROOT%\runtime" > nul || EXIT /B 1

    ECHO Cleaning up unnecessary .pyc and .pyo files...
    FOR /R "%BUILDROOT%\venv" %%f in (*.pyc *.pyo) do DEL /q "%%f" 1> nul 2>&1
    ECHO Removing tests...
    FOR /R "%BUILDROOT%\venv\Lib" %%f in (test tests) do RD /Q /S "%%f" 1> nul 2>&1
    ECHO Removing TCL...
    RD /Q /S "%BUILDROOT%\venv\tcl" 1> nul 2>&1
	
	ECHO Copy Python Scripts...
	XCOPY /S /I /E /H /Y "%WD%\common" "%BUILDROOT%\common" > nul || EXIT /B 1
	XCOPY /S /I /E /H /Y "%WD%\config" "%BUILDROOT%\config" > nul || EXIT /B 1
	XCOPY /S /I /E /H /Y "%WD%\controller" "%BUILDROOT%\controller" > nul || EXIT /B 1
	XCOPY /S /I /E /H /Y "%WD%\convert" "%BUILDROOT%\convert" > nul || EXIT /B 1
	XCOPY /S /I /E /H /Y "%WD%\dao" "%BUILDROOT%\dao" > nul || EXIT /B 1
	XCOPY /S /I /E /H /Y "%WD%\flaskapp" "%BUILDROOT%\flaskapp" > nul || EXIT /B 1
	XCOPY /S /I /E /H /Y "%WD%\installer" "%BUILDROOT%\installer" > nul || EXIT /B 1
	XCOPY /S /I /E /H /Y "%WD%\migrations" "%BUILDROOT%\migrations" > nul || EXIT /B 1
	XCOPY /S /I /E /H /Y "%WD%\resource" "%BUILDROOT%\resource" > nul || EXIT /B 1
	XCOPY /S /I /E /H /Y "%WD%\service" "%BUILDROOT%\service" > nul || EXIT /B 1
	XCOPY /S /I /E /H /Y "%WD%\web" "%BUILDROOT%\web" > nul || EXIT /B 1
	
	COPY %WD%\..\AnalysisTool_Launcher\bin\Release\AnalysisTool_Launcher.exe "%BUILDROOT%" > nul || EXIT /B 1
	COPY %WD%\alembic.ini "%BUILDROOT%" > nul || EXIT /B 1
	COPY %WD%\main.py "%BUILDROOT%" > nul || EXIT /B 1
	COPY %WD%\LICENSE.md "%BUILDROOT%" > nul || EXIT /B 1
	COPY %WD%\..\README.md "%BUILDROOT%" > nul || EXIT /B 1

    EXIT /B 0


:CREATE_INSTALLER
    ECHO Preparing for creation of windows installer...
    IF NOT EXIST "%DISTROOT%" MKDIR "%DISTROOT%"

    CD "%WD%\installer"

    ECHO Processing installer configuration script...
    CALL "%ANALYSISTOOL_PYTHON_DIR%\python" "%WD%\installer\replace.py" "-i" "%WD%\installer\installer.iss.in" "-o" "%WD%\installer\installer.iss.in_stage1" "-s" MYAPP_VERSION -r """%APP_VERSION%"""
	CALL "%ANALYSISTOOL_PYTHON_DIR%\python" "%WD%\installer\replace.py" "-i" "%WD%\installer\installer.iss.in_stage1" "-o" "%WD%\installer\installer.iss.in_stage2" "-s" MYAPP_NAME -r """%APP_NAME%"""
    

    SET ARCMODE=
    IF "%ARCHITECTURE%" == "x64" (
        set ARCMODE="x64"
    )
    CALL "%ANALYSISTOOL_PYTHON_DIR%\python" "%WD%\installer\replace.py" "-i" "%WD%\installer\installer.iss.in_stage2" "-o" "%WD%\installer\installer.iss" "-s" MYAPP_ARCHITECTURESMODE -r """%ARCMODE%"""
    

    ECHO Cleaning up...
    DEL /s "%WD%\installer\installer.iss.in_stage*" > nul

    ECHO Creating windows installer using INNO tool...
    CALL "%ANALYSISTOOL_INNOTOOL_DIR%\ISCC.exe" /q "%WD%\installer\installer.iss" || EXIT /B 1

    ECHO Renaming installer...
    MOVE "%WD%\installer\Output\mysetup.exe" "%DISTROOT%\%INSTALLERNAME%" > nul || EXIT /B 1

    ECHO Location - %DISTROOT%\%INSTALLERNAME%
    ECHO Installer generated successfully.

    CD %WD%
    EXIT /B 0


:CLEANUP_ENV
    ECHO Cleaning the build environment...
    RD "%BUILDROOT%\venv\Include" /S /Q 1> nul 2>&1
    DEL /s "%BUILDROOT%\venv\pip-selfcheck.json" 1> nul 2>&1

    EXIT /B 0


:USAGE
    ECHO Invalid command line options.
    ECHO Usage: "Make.bat [clean]"
    ECHO.

    EXIT /B 1

