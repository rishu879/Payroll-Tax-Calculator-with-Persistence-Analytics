#!/usr/bin/env bash
# ==============================================================================
# PayPilot: Statutory Payroll & Tax Portal (Linux / macOS Launcher)
# ==============================================================================
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "======================================================================"
echo "  PayPilot: Statutory Payroll & Tax Portal (College Academic Project) "
echo "======================================================================"
echo ""

# Verify Java Runtime
if ! command -v java &> /dev/null; then
    echo "[ERROR] 'java' command not found. Please install JDK 17+ (OpenJDK/Adoptium)."
    exit 1
fi

# Verify Compiler
if ! command -v javac &> /dev/null; then
    echo "[ERROR] 'javac' command not found. Please ensure JDK (not just JRE) is on PATH."
    exit 1
fi

# Compile if class file missing
if [ ! -f "PayPilotServer.class" ]; then
    echo "[*] Compiling PayPilotServer.java..."
    javac -encoding UTF-8 -cp ".:sqlite-jdbc.jar" PayPilotServer.java
    echo "[*] Compilation completed successfully."
fi

# Test mode
if [ "$1" == "--test" ]; then
    echo "[*] Executing PayPilot statutory engine test suite..."
    java -cp ".:sqlite-jdbc.jar" PayPilotServer --test
    exit 0
fi

# Start Server
echo ""
echo "[*] Launching PayPilot Server at: http://127.0.0.1:8080"
echo "[*] Press Ctrl+C to terminate the server."
echo "======================================================================"
echo ""
java -cp ".:sqlite-jdbc.jar" PayPilotServer
