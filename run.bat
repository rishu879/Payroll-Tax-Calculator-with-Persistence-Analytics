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

rem 4. Launch PayPilot Server
echo.
echo [*] Launching PayPilot Server...
echo [*] Server will auto-select an available port (default: 8080, fallback: 8081+).
echo [*] Press Ctrl+C to terminate the server.
echo ======================================================================
echo.
java -cp ".;sqlite-jdbc.jar" PayPilotServer %*
pause
