@echo off
echo Starting Ellipsoid Labs Frontend...
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
)

REM Start the development server
echo Starting React development server on http://localhost:3000
echo Press Ctrl+C to stop the server
echo.
npm start

pause
