# 🐳 Docker Setup Guide

This guide will help you build and run the AI Skill Recommendation System using Docker.

## 📋 Prerequisites

1. **Docker Desktop** installed and running
   - Download from: https://www.docker.com/products/docker-desktop/
   - Make sure Docker is running before proceeding

2. **Groq API Key**
   - Sign up at: https://console.groq.com/
   - Get your API key from: https://console.groq.com/keys

## 🚀 Quick Start (Windows)

### Option 1: Using the Batch File (Recommended)
```bash
# Run the batch file
build_and_run.bat
```

### Option 2: Manual Steps
```bash
# 1. Create .env file with your API key
echo GROQ_API_KEY=your_actual_api_key_here > .env

# 2. Build containers
docker-compose build

# 3. Start the application
docker-compose up -d
```

## 🚀 Quick Start (Linux/Mac)

### Option 1: Using the Shell Script
```bash
# Make script executable
chmod +x build_and_run.sh

# Run the script
./build_and_run.sh
```

### Option 2: Manual Steps
```bash
# 1. Create .env file with your API key
echo "GROQ_API_KEY=your_actual_api_key_here" > .env

# 2. Build containers
docker-compose build

# 3. Start the application
docker-compose up -d
```

## 🔧 Manual Setup Steps

### Step 1: Environment Setup
Create a `.env` file in the project root:
```bash
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional
DEFAULT_MODEL=llama3-8b-8192
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
LOG_LEVEL=INFO
```

### Step 2: Build Containers
```bash
# Build both frontend and backend containers
docker-compose build

# Or build individually
docker-compose build backend
docker-compose build frontend
```

### Step 3: Start the Application
```bash
# Start in detached mode (background)
docker-compose up -d

# Or start in foreground to see logs
docker-compose up
```

## 🌐 Access the Application

Once running, you can access:

- **Frontend**: http://localhost
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## 📊 Useful Commands

### View Logs
```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
```

### Stop the Application
```bash
# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes
docker-compose down -v
```

### Restart Services
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Check Container Status
```bash
# List running containers
docker-compose ps

# Check container health
docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
```

## 🔍 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the ports
   netstat -ano | findstr :80
   netstat -ano | findstr :8000
   
   # Kill the process or change ports in docker-compose.yml
   ```

2. **Build Fails**
   ```bash
   # Clean and rebuild
   docker-compose down
   docker system prune -f
   docker-compose build --no-cache
   ```

3. **API Key Issues**
   ```bash
   # Check if API key is loaded
   docker-compose exec backend env | grep GROQ
   
   # Restart with new environment
   docker-compose down
   docker-compose up -d
   ```

4. **Frontend Not Loading**
   ```bash
   # Check nginx logs
   docker-compose logs frontend
   
   # Check if backend is responding
   curl http://localhost:8000/api/v1/health
   ```

### Debug Mode
```bash
# Start with debug logging
DEBUG=true docker-compose up

# Or modify .env file
echo "DEBUG=true" >> .env
docker-compose up -d
```

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Nginx Proxy   │    │   Backend       │
│   (React)       │◄──►│   (Port 80)     │◄──►│   (FastAPI)     │
│   Port 3000     │    │                 │    │   Port 8000     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Container Structure

### Backend Container
- **Base Image**: Python 3.11-slim
- **Port**: 8000
- **Health Check**: `/api/v1/health`
- **Dependencies**: FastAPI, LangChain, Groq, etc.

### Frontend Container
- **Base Image**: Node.js 18 + Nginx
- **Port**: 80
- **Health Check**: `/`
- **Features**: React app served by Nginx

## 🔒 Security Notes

- The application runs on `localhost` by default
- For production, update nginx.conf with proper security headers
- Consider using Docker secrets for API keys in production
- The current setup is for development purposes

## 🚀 Production Deployment

For production deployment, consider:

1. **Environment Variables**: Use Docker secrets or environment management
2. **SSL/TLS**: Add HTTPS with proper certificates
3. **Monitoring**: Add logging and monitoring solutions
4. **Scaling**: Use Docker Swarm or Kubernetes
5. **Security**: Implement proper authentication and authorization

## 📞 Support

If you encounter issues:

1. Check the logs: `docker-compose logs`
2. Verify Docker is running: `docker info`
3. Check port availability: `netstat -ano | findstr :80`
4. Ensure API key is valid and has sufficient credits 