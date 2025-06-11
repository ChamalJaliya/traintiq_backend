@echo off
echo ===========================================
echo    TraintiQ AI Chat System - Backend
echo ===========================================
echo.

:: Check if config.env exists
if not exist "config.env" (
    echo ERROR: config.env file not found!
    echo Please make sure config.env exists with your API key.
    pause
    exit /b 1
)

:: Load environment variables from config.env
for /f "tokens=1,2 delims==" %%a in (config.env) do (
    if "%%a"=="OPENAI_API_KEY" (
        if "%%b"=="YOUR_OPENAI_API_KEY_HERE" (
            echo.
            echo ERROR: Please update your OPENAI_API_KEY in config.env
            echo Current value: %%b
            echo.
            echo To fix this:
            echo 1. Open config.env file
            echo 2. Replace YOUR_OPENAI_API_KEY_HERE with your actual OpenAI API key
            echo 3. Save the file and run this script again
            echo.
            pause
            exit /b 1
        )
        set %%a=%%b
    ) else (
        set %%a=%%b
    )
)

echo Checking virtual environment...
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing/updating dependencies...
pip install -r requirements.txt

echo.
echo Environment configured:
echo - OpenAI API Key: Set ✓
echo - Virtual Environment: Active ✓
echo - Dependencies: Updated ✓
echo.

echo Starting TraintiQ Chat Backend Server...
echo Server will be available at: http://localhost:5000
echo Health check: http://localhost:5000/api/chat/health
echo.
echo Press Ctrl+C to stop the server
echo.

python run.py

# Deploy everything
deploy-docker.bat

# Start services  
docker-manage.bat start

# View logs
docker-manage.bat logs

# Check status
docker-manage.bat status

# Stop all
docker-manage.bat stop

# This will build and start all services
docker-compose --env-file docker.env up --build -d

# Check if everything is running
docker-compose ps 