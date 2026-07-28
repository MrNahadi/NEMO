@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem NEMO Windows launcher. Keep engineering logic in Python; this file only
rem coordinates setup, tests, analytical runs, Fusion CAD requests, and UI.

cd /d "%~dp0"
set "PYTHON_EXE=.venv\Scripts\python.exe"

if not defined NEMO_SAMPLE_COUNT set "NEMO_SAMPLE_COUNT=60"
if not defined NEMO_MAX_ITER set "NEMO_MAX_ITER=80"

if "%~1"=="" goto menu

if /I "%~1"=="help" goto help
if /I "%~1"=="setup" goto command_setup
if /I "%~1"=="check" goto command_check
if /I "%~1"=="pipeline" goto command_pipeline
if /I "%~1"=="fusion" goto command_fusion
if /I "%~1"=="dashboard" goto command_dashboard

echo [ERROR] Unknown command: %~1
echo.
goto help_error

:menu
cls
echo ================================================================
echo                    NEMO PROJECT LAUNCHER
echo ================================================================
echo.
echo  1. Set up or repair the Python environment
echo  2. Run offline checks and tests
echo  3. Run full analytical pipeline: padeye + stabilizer [recommended]
echo  4. Run full analytical pipeline: all three parts
echo  5. Run padeye + stabilizer pipeline and generate Fusion CAD
echo  6. Open the results dashboard
echo  7. Exit
echo.
choice /C 1234567 /N /M "Choose an option [1-7]: "

if errorlevel 7 exit /b 0
if errorlevel 6 goto menu_dashboard
if errorlevel 5 goto menu_fusion
if errorlevel 4 goto menu_all
if errorlevel 3 goto menu_advanced
if errorlevel 2 goto menu_check
if errorlevel 1 goto menu_setup

:menu_setup
call :setup_environment
call :menu_finish
exit /b %errorlevel%

:menu_check
call :run_checks
call :menu_finish
exit /b %errorlevel%

:menu_advanced
call :run_pipeline advanced 0
call :menu_finish
exit /b %errorlevel%

:menu_all
call :run_pipeline all 0
call :menu_finish
exit /b %errorlevel%

:menu_fusion
echo.
echo Before continuing, open Autodesk Fusion and start NEMOBridge.
echo The script will wait for Fusion while generating each finalist.
echo.
choice /C YN /N /M "Is Fusion open and NEMOBridge running? [Y/N]: "
if errorlevel 2 goto menu
call :run_pipeline advanced 1
call :menu_finish
exit /b %errorlevel%

:menu_dashboard
call :start_dashboard
call :menu_finish
exit /b %errorlevel%

:menu_finish
set "MENU_RESULT=%errorlevel%"
echo.
if "%MENU_RESULT%"=="0" (
    echo Operation completed.
) else (
    echo Operation failed. Review the first [ERROR] message above.
)
echo.
pause
exit /b %MENU_RESULT%

:command_setup
call :setup_environment
exit /b %errorlevel%

:command_check
call :run_checks
exit /b %errorlevel%

:command_pipeline
set "TARGET=%~2"
if not defined TARGET set "TARGET=advanced"
call :run_pipeline "%TARGET%" 0
exit /b %errorlevel%

:command_fusion
set "TARGET=%~2"
if not defined TARGET set "TARGET=advanced"
echo [INFO] Fusion and NEMOBridge must already be running.
call :run_pipeline "%TARGET%" 1
exit /b %errorlevel%

:command_dashboard
call :start_dashboard
exit /b %errorlevel%

:setup_environment
echo.
echo ================================================================
echo [SETUP] Preparing the Python environment
echo ================================================================

if not exist "%PYTHON_EXE%" (
    echo [SETUP] Creating .venv ...
    set "VENV_CREATED=0"
    where py >nul 2>&1
    if not errorlevel 1 (
        py -3 -m venv .venv
        if not errorlevel 1 set "VENV_CREATED=1"
    )
    if "!VENV_CREATED!"=="0" (
        echo [SETUP] The Python launcher was unavailable or failed; trying python ...
        where python >nul 2>&1
        if errorlevel 1 (
            echo [ERROR] Python 3.10 or newer was not found.
            echo Install Python from https://www.python.org/downloads/windows/
            exit /b 1
        )
        python -m venv .venv
        if not errorlevel 1 set "VENV_CREATED=1"
    )
    if "!VENV_CREATED!"=="0" (
        echo [ERROR] Failed to create the virtual environment.
        exit /b 1
    )
)

echo [SETUP] Updating pip ...
"%PYTHON_EXE%" -m pip install --upgrade pip
if errorlevel 1 (
    echo [ERROR] pip could not be updated. Check the internet connection.
    exit /b 1
)

echo [SETUP] Installing NEMO and development dependencies ...
"%PYTHON_EXE%" -m pip install -e ".[dev]"
if errorlevel 1 (
    echo [ERROR] NEMO dependencies could not be installed.
    exit /b 1
)

echo [SETUP] Environment ready.
exit /b 0

:ensure_environment
if not exist "%PYTHON_EXE%" (
    call :setup_environment
    exit /b %errorlevel%
)

"%PYTHON_EXE%" -c "import nemo" >nul 2>&1
if errorlevel 1 (
    echo [INFO] NEMO is not installed in .venv; repairing the environment.
    call :setup_environment
    exit /b %errorlevel%
)
exit /b 0

:run_checks
call :ensure_environment
if errorlevel 1 exit /b 1

echo.
echo ================================================================
echo [CHECK] Running the offline test suite
echo ================================================================
"%PYTHON_EXE%" -m pytest -q
if errorlevel 1 (
    echo [ERROR] Offline tests failed. The pipeline was not started.
    exit /b 1
)

echo [CHECK] Registered parts:
"%PYTHON_EXE%" -m nemo.cli parts
if errorlevel 1 exit /b 1
exit /b 0

:make_run_id
if defined NEMO_RUN_ID (
    set "ACTIVE_RUN_ID=%NEMO_RUN_ID%"
    exit /b 0
)
for /f "delims=" %%I in ('%PYTHON_EXE% -c "from datetime import datetime; print(datetime.now().strftime('%%Y%%m%%d_%%H%%M%%S'))"') do set "ACTIVE_RUN_ID=%%I"
if not defined ACTIVE_RUN_ID (
    echo [ERROR] Could not create a run identifier.
    exit /b 1
)
exit /b 0

:run_pipeline
set "PIPELINE_TARGET=%~1"
set "WITH_FUSION=%~2"

call :ensure_environment
if errorlevel 1 exit /b 1

if /I not "%NEMO_SKIP_TESTS%"=="1" (
    call :run_checks
    if errorlevel 1 exit /b 1
)

call :make_run_id
if errorlevel 1 exit /b 1

echo.
echo ================================================================
echo [PIPELINE] Run ID: %ACTIVE_RUN_ID%
echo [PIPELINE] Target: %PIPELINE_TARGET%
echo [PIPELINE] Samples per part: %NEMO_SAMPLE_COUNT%
echo [PIPELINE] Maximum iterations per optimizer start: %NEMO_MAX_ITER%
echo ================================================================

if /I "%PIPELINE_TARGET%"=="advanced" (
    call :run_part padeye %WITH_FUSION%
    if errorlevel 1 exit /b 1
    call :run_part stabilizer %WITH_FUSION%
    if errorlevel 1 exit /b 1
    goto pipeline_complete
)

if /I "%PIPELINE_TARGET%"=="all" (
    call :run_part bracket %WITH_FUSION%
    if errorlevel 1 exit /b 1
    call :run_part padeye %WITH_FUSION%
    if errorlevel 1 exit /b 1
    call :run_part stabilizer %WITH_FUSION%
    if errorlevel 1 exit /b 1
    goto pipeline_complete
)

if /I "%PIPELINE_TARGET%"=="bracket" goto run_single_part
if /I "%PIPELINE_TARGET%"=="padeye" goto run_single_part
if /I "%PIPELINE_TARGET%"=="stabilizer" goto run_single_part

echo [ERROR] Invalid target '%PIPELINE_TARGET%'.
echo Use bracket, padeye, stabilizer, advanced, or all.
exit /b 1

:run_single_part
call :run_part "%PIPELINE_TARGET%" %WITH_FUSION%
if errorlevel 1 exit /b 1

:pipeline_complete
echo.
echo ================================================================
echo [DONE] NEMO pipeline completed
echo [DONE] Run ID: %ACTIVE_RUN_ID%
echo [DONE] Results: data\runs\%ACTIVE_RUN_ID%_*
echo [DONE] Validation packages: reports\%ACTIVE_RUN_ID%_*
echo ================================================================
echo.
echo FEA is not automated. Open each generated VALIDATION_CHECKLIST.md and
echo complete the documented Fusion Static Stress validation manually.
exit /b 0

:run_part
setlocal EnableDelayedExpansion
set "PART=%~1"
set "PART_FUSION=%~2"
set "RUN_PREFIX=data\runs\%ACTIVE_RUN_ID%_!PART!"
set "SAMPLE_DIR=!RUN_PREFIX!_sample"
set "BASELINE_DIR=!RUN_PREFIX!_optimize_baseline"
set "STARTS_DIR=!RUN_PREFIX!_starts"
set "START1_DIR=!RUN_PREFIX!_optimize_start_01"
set "START2_DIR=!RUN_PREFIX!_optimize_start_02"
set "REPORT_DIR=reports\%ACTIVE_RUN_ID%_!PART!_validation"

if exist "!SAMPLE_DIR!" (
    echo [ERROR] Output folder already exists: !SAMPLE_DIR!
    echo Choose a different NEMO_RUN_ID or leave it unset for an automatic timestamp.
    endlocal & exit /b 1
)
if exist "!REPORT_DIR!" (
    echo [ERROR] Validation folder already exists: !REPORT_DIR!
    echo Choose a different NEMO_RUN_ID or leave it unset for an automatic timestamp.
    endlocal & exit /b 1
)

echo.
echo ----------------------------------------------------------------
echo [PART] !PART!
echo ----------------------------------------------------------------

echo [1/7] Evaluating the configured baseline ...
"%PYTHON_EXE%" -m nemo.cli evaluate --part !PART!
if errorlevel 1 goto part_failed

echo [2/7] Running !NEMO_SAMPLE_COUNT!-point Latin-hypercube sampling ...
"%PYTHON_EXE%" -m nemo.cli sample --part !PART! --count !NEMO_SAMPLE_COUNT! --method latin --seed 42 --run-dir "!SAMPLE_DIR!"
if errorlevel 1 goto part_failed

echo [3/7] Optimizing from the configured baseline ...
"%PYTHON_EXE%" -m nemo.cli optimize --part !PART! --max-iter !NEMO_MAX_ITER! --run-dir "!BASELINE_DIR!"
if errorlevel 1 goto part_failed

echo [4/7] Selecting two alternative optimizer starts ...
"%PYTHON_EXE%" -m nemo.cli validation-package --part !PART! "!SAMPLE_DIR!\results.csv" "!BASELINE_DIR!\results.csv" --count 2 --output-dir "!STARTS_DIR!"
if errorlevel 1 goto part_failed

if not exist "!STARTS_DIR!\fusion_requests\candidate_01_request.json" (
    echo [ERROR] No feasible alternative start was found for !PART!.
    goto part_failed
)

echo [5/7] Optimizing from candidate 01 ...
"%PYTHON_EXE%" -m nemo.cli optimize --part !PART! --start-json "!STARTS_DIR!\fusion_requests\candidate_01_request.json" --max-iter !NEMO_MAX_ITER! --run-dir "!START1_DIR!"
if errorlevel 1 goto part_failed

set "HAS_START2=0"
if exist "!STARTS_DIR!\fusion_requests\candidate_02_request.json" (
    set "HAS_START2=1"
    echo [6/7] Optimizing from candidate 02 ...
    "%PYTHON_EXE%" -m nemo.cli optimize --part !PART! --start-json "!STARTS_DIR!\fusion_requests\candidate_02_request.json" --max-iter !NEMO_MAX_ITER! --run-dir "!START2_DIR!"
    if errorlevel 1 goto part_failed
) else (
    echo [6/7] Candidate 02 was unavailable; continuing with two optimizer starts.
)

echo [7/7] Building the final validation package ...
if "!HAS_START2!"=="1" (
    "%PYTHON_EXE%" -m nemo.cli validation-package --part !PART! "!SAMPLE_DIR!\results.csv" "!BASELINE_DIR!\results.csv" "!START1_DIR!\results.csv" "!START2_DIR!\results.csv" --count 5 --output-dir "!REPORT_DIR!"
) else (
    "%PYTHON_EXE%" -m nemo.cli validation-package --part !PART! "!SAMPLE_DIR!\results.csv" "!BASELINE_DIR!\results.csv" "!START1_DIR!\results.csv" --count 5 --output-dir "!REPORT_DIR!"
)
if errorlevel 1 goto part_failed

if "!PART_FUSION!"=="1" (
    call :generate_fusion_candidates "!PART!" "!REPORT_DIR!"
    if errorlevel 1 goto part_failed
)

echo [PART DONE] !PART!
echo [PART DONE] Checklist: !REPORT_DIR!\VALIDATION_CHECKLIST.md
endlocal & exit /b 0

:part_failed
echo [ERROR] Pipeline failed while processing !PART!.
endlocal & exit /b 1

:generate_fusion_candidates
setlocal EnableDelayedExpansion
set "FUSION_PART=%~1"
set "FUSION_REPORT=%~2"
set "RESPONSE_DIR=!FUSION_REPORT!\fusion_responses"
if not exist "!RESPONSE_DIR!" mkdir "!RESPONSE_DIR!"

echo [FUSION] Generating baseline and finalist CAD for !FUSION_PART! ...
for %%F in ("!FUSION_REPORT!\fusion_requests\*_request.json") do (
    echo [FUSION] %%~nF
    "%PYTHON_EXE%" -m nemo.cli cad --part !FUSION_PART! --params-json "%%~fF" --artifact step --artifact boundary_tags --output-json "!RESPONSE_DIR!\%%~nF_response.json"
    if errorlevel 1 (
        echo [ERROR] Fusion failed while processing %%~nxF.
        endlocal & exit /b 1
    )
)
endlocal & exit /b 0

:start_dashboard
call :ensure_environment
if errorlevel 1 exit /b 1
echo.
echo ================================================================
echo [DASHBOARD] Starting NEMO Results
echo [DASHBOARD] Open http://localhost:8501 in a browser.
echo [DASHBOARD] Press Ctrl+C in this window to stop it.
echo ================================================================
"%PYTHON_EXE%" -m streamlit run dashboard\app.py
exit /b %errorlevel%

:help
echo NEMO build launcher
echo.
echo Usage:
echo   build.bat                         Open the beginner menu
echo   build.bat setup                   Create .venv and install dependencies
echo   build.bat check                   Run offline tests and list parts
echo   build.bat pipeline [target]       Run the analytical pipeline
echo   build.bat fusion [target]         Run pipeline plus Fusion CAD export
echo   build.bat dashboard               Start the Streamlit dashboard
echo   build.bat help                    Show this help
echo.
echo Targets:
echo   bracket       Original proof-of-concept only
echo   padeye        Padeye only
echo   stabilizer    Stabilizer only
echo   advanced      Padeye and stabilizer [default]
echo   all           Bracket, padeye, and stabilizer
echo.
echo Optional environment overrides:
echo   NEMO_SAMPLE_COUNT   Samples per part; default 60
echo   NEMO_MAX_ITER       Iterations per optimizer start; default 80
echo   NEMO_SKIP_TESTS=1   Skip pre-pipeline tests
echo   NEMO_RUN_ID         Supply a deterministic output folder prefix
exit /b 0

:help_error
call :help
exit /b 1
