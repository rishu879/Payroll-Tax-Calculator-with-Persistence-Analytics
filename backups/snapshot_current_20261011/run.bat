@echo off
title PayPilot: Statutory Payroll ^& Tax Portal
echo ======================================================================
echo   PayPilot: Statutory Payroll ^& Tax Portal (College Academic Project)
echo ======================================================================
echo.

rem 1. Check for Java runtime
where java >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] 'java' command was not found on your system PATH.
    echo Please install OpenJDK 17+ or Eclipse Adoptium Temurin and add to PATH.
    pause
    exit /b 1
)

rem 2. Run automated self-test flag if requested
if "%1"=="--test" (
    echo [*] Executing PayPilot statutory engine test suite...
    java -cp ".;sqlite-jdbc.jar" PayPilotServer --test
    pause
    exit /b 0
)

rem 3. Compile PayPilotServer.java
echo [*] Compiling PayPilotServer.java...
javac -encoding UTF-8 -cp ".;sqlite-jdbc.jar" PayPilotServer.java
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Compilation failed. Please inspect syntax or imports.
    pause
    exit /b 1
)
echo [*] Build successful!

rem 4. Check if server is already running on port 8080
netstat -ano | findstr :8080 | findstr LISTENING >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [*] Port 8080 is currently active and running.
    echo [*] Opening http://localhost:8080 in your default browser...
    start http://localhost:8080
    echo.
    echo Type R to restart server fresh, or press Enter to keep current server:
    set /p RESTART_CHOICE=""
    if /i "%RESTART_CHOICE%"=="R" (
        echo [*] Stopping previous instance on port 8080...
        for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
        timeout /t 1 /nobreak >nul
        goto launch
    )
    exit /b 0
)

:launch

rem 5. Launch PayPilot Server
echo.
echo [*] Launching PayPilot Server at: http://127.0.0.1:8080
echo [*] Opening browser in 3 seconds...
start http://localhost:8080
echo [*] Press Ctrl+C to terminate the server.
echo ======================================================================
echo.
java -cp ".;sqlite-jdbc.jar" PayPilotServer
pause
