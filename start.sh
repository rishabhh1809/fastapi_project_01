#!/bin/bash

# ============================================================
# Event Ticketing Platform - Startup Script
# ============================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="postgres-ticketing"
DB_NAME="event_ticketing"
DB_USER="postgres"
DB_PASSWORD="postgres"
DB_PORT="5432"
FASTAPI_HOST="127.0.0.1"
FASTAPI_PORT="8000"

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}    Event Ticketing Platform - Startup Script${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# -------------------- Docker PostgreSQL --------------------
echo -e "${YELLOW}[1/4] Checking Docker...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker daemon is not running. Please start Docker.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"

# -------------------- Start PostgreSQL --------------------
echo -e "${YELLOW}[2/4] Starting PostgreSQL container...${NC}"

# Check if container exists
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    # Container exists, check if running
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo -e "${GREEN}✅ PostgreSQL container already running${NC}"
    else
        # Container exists but stopped, start it
        echo -e "${YELLOW}   Starting stopped container...${NC}"
        docker start ${CONTAINER_NAME}
        echo -e "${GREEN}✅ PostgreSQL container started${NC}"
    fi
else
    # Container doesn't exist, create it
    echo -e "${YELLOW}   Creating new PostgreSQL container...${NC}"
    docker run -d \
        --name ${CONTAINER_NAME} \
        -e POSTGRES_USER=${DB_USER} \
        -e POSTGRES_PASSWORD=${DB_PASSWORD} \
        -e POSTGRES_DB=${DB_NAME} \
        -p ${DB_PORT}:5432 \
        -v postgres_ticketing_data:/var/lib/postgresql/data \
        postgres:17-alpine
    echo -e "${GREEN}✅ PostgreSQL container created and started${NC}"
fi

# -------------------- Wait for PostgreSQL --------------------
echo -e "${YELLOW}[3/4] Waiting for PostgreSQL to be ready...${NC}"

MAX_RETRIES=30
RETRY_COUNT=0

until docker exec ${CONTAINER_NAME} pg_isready -U ${DB_USER} -d ${DB_NAME} &> /dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo -e "${RED}❌ PostgreSQL failed to start after ${MAX_RETRIES} attempts${NC}"
        exit 1
    fi
    echo -e "   Waiting... (${RETRY_COUNT}/${MAX_RETRIES})"
    sleep 1
done

echo -e "${GREEN}✅ PostgreSQL is ready${NC}"

# -------------------- Activate Virtual Environment --------------------
echo -e "${YELLOW}[4/4] Starting FastAPI application...${NC}"

# Navigate to project directory
cd "$(dirname "$0")"

# Check for virtual environment
if [ -d ".venv" ]; then
    echo -e "   Activating virtual environment (.venv)..."
    source .venv/bin/activate
elif [ -d "venv" ]; then
    echo -e "   Activating virtual environment (venv)..."
    source venv/bin/activate
elif [ -d "env" ]; then
    echo -e "   Activating virtual environment (env)..."
    source env/bin/activate
else
    echo -e "${YELLOW}   No virtual environment found, using system Python${NC}"
fi

# -------------------- Start FastAPI --------------------
echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}🚀 Starting FastAPI server...${NC}"
echo -e "${GREEN}============================================================${NC}"
echo -e "   📍 API:     http://localhost:${FASTAPI_PORT}"
echo -e "   📚 Docs:    http://localhost:${FASTAPI_PORT}/docs"
echo -e "   📊 Metrics: http://localhost:${FASTAPI_PORT}/metrics"
echo -e "${GREEN}============================================================${NC}"
echo ""

cd src
uvicorn app.main:app --host ${FASTAPI_HOST} --port ${FASTAPI_PORT} --reload
