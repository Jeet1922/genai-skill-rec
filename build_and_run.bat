@echo off
setlocal enabledelayedexpansion

echo 🚀 Building and Running AI Skill Recommendation System

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found. Creating template...
    (
        echo # Groq API Key ^(Required^)
        echo GROQ_API_KEY=your_groq_api_key_here
        echo.
        echo # Optional settings
        echo DEFAULT_MODEL=llama3-8b-8192
        echo API_HOST=0.0.0.0
        echo API_PORT=8000
        echo DEBUG=true
        echo LOG_LEVEL=INFO
    ) > .env
    echo 📝 Please edit .env file and add your Groq API key
    echo    Get your API key from: https://console.groq.com/keys
    pause
    exit /b 1
)

REM Check if GROQ_API_KEY is set
findstr /c:"GROQ_API_KEY=your_groq_api_key_here" .env >nul
if not errorlevel 1 (
    echo ❌ Please set your GROQ_API_KEY in .env file
    pause
    exit /b 1
)

echo ✅ GROQ_API_KEY found in .env file
echo 🔨 Building Docker containers...

REM Build the containers
docker-compose build
if errorlevel 1 (
    echo ❌ Failed to build containers
    pause
    exit /b 1
)

echo ✅ Containers built successfully!
echo 🚀 Starting the application...

REM Start the containers
docker-compose up -d
if errorlevel 1 (
    echo ❌ Failed to start containers
    pause
    exit /b 1
)

echo ✅ Application started successfully!
echo 🌐 Frontend: http://localhost
echo 🔧 API Docs: http://localhost:8000/docs
echo ❤️  Health Check: http://localhost:8000/api/v1/health
echo 📊 To view logs: docker-compose logs -f
echo 🛑 To stop: docker-compose down
pause 