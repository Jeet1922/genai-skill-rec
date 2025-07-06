#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Building and Running AI Skill Recommendation System${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating template...${NC}"
    cat > .env << EOF
# Groq API Key (Required)
GROQ_API_KEY=your_groq_api_key_here

# Optional settings
DEFAULT_MODEL=llama3-8b-8192
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
LOG_LEVEL=INFO
EOF
    echo -e "${YELLOW}📝 Please edit .env file and add your Groq API key${NC}"
    echo -e "${YELLOW}   Get your API key from: https://console.groq.com/keys${NC}"
    exit 1
fi

# Check if GROQ_API_KEY is set
if ! grep -q "GROQ_API_KEY=your_groq_api_key_here" .env; then
    echo -e "${GREEN}✅ GROQ_API_KEY found in .env file${NC}"
else
    echo -e "${RED}❌ Please set your GROQ_API_KEY in .env file${NC}"
    exit 1
fi

echo -e "${GREEN}🔨 Building Docker containers...${NC}"

# Build the containers
docker-compose build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Containers built successfully!${NC}"
else
    echo -e "${RED}❌ Failed to build containers${NC}"
    exit 1
fi

echo -e "${GREEN}🚀 Starting the application...${NC}"

# Start the containers
docker-compose up -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Application started successfully!${NC}"
    echo -e "${GREEN}🌐 Frontend: http://localhost${NC}"
    echo -e "${GREEN}🔧 API Docs: http://localhost:8000/docs${NC}"
    echo -e "${GREEN}❤️  Health Check: http://localhost:8000/api/v1/health${NC}"
    echo -e "${YELLOW}📊 To view logs: docker-compose logs -f${NC}"
    echo -e "${YELLOW}🛑 To stop: docker-compose down${NC}"
else
    echo -e "${RED}❌ Failed to start containers${NC}"
    exit 1
fi 