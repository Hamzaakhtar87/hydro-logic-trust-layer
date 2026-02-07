#!/bin/bash

# ============================================
# Hydro-Logic Trust Layer - Service Starter
# ============================================
# This script starts all services for the Hydro-Logic Trust Layer
# 
# Usage: ./start.sh [options]
#   --backend-only    Start only the backend
#   --frontend-only   Start only the frontend
#   --dev             Development mode with hot reload (default)
#   --prod            Production mode
#   --stop            Stop all running services
#   --help            Show this help message

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_DIR"
FRONTEND_DIR="$PROJECT_DIR/frontend"
VENV_DIR="$PROJECT_DIR/venv"
BACKEND_PORT=8000
FRONTEND_PORT=3000
PID_FILE="$PROJECT_DIR/.running_services.pid"

# Default options
MODE="dev"
START_BACKEND=true
START_FRONTEND=true

# ============================================
# Helper Functions
# ============================================

print_banner() {
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║   🌊 Hydro-Logic Trust Layer                              ║"
    echo "║   HTTPS for AI Agents                                     ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    print_status "Checking requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.10+"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+"
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm"
        exit 1
    fi
    
    # Check virtual environment
    if [ ! -d "$VENV_DIR" ]; then
        print_warning "Virtual environment not found. Creating..."
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    fi
    
    # Check .env file
    if [ ! -f "$PROJECT_DIR/.env" ]; then
        if [ -f "$PROJECT_DIR/.env.example" ]; then
            print_warning ".env file not found. Creating from .env.example..."
            cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
            print_warning "Please update .env with your GEMINI_API_KEY"
        else
            print_error ".env file not found. Please create one with GEMINI_API_KEY"
            exit 1
        fi
    fi
    
    print_success "All requirements satisfied"
}

install_dependencies() {
    print_status "Installing dependencies..."
    
    # Backend dependencies
    print_status "Installing Python dependencies..."
    source "$VENV_DIR/bin/activate"
    pip install -q -r "$PROJECT_DIR/requirements.txt"
    print_success "Python dependencies installed"
    
    # Frontend dependencies
    if [ -d "$FRONTEND_DIR" ] && [ -f "$FRONTEND_DIR/package.json" ]; then
        print_status "Installing Node.js dependencies..."
        cd "$FRONTEND_DIR"
        npm install --silent
        cd "$PROJECT_DIR"
        print_success "Node.js dependencies installed"
    fi
}

start_backend() {
    print_status "Starting backend server on port $BACKEND_PORT..."
    
    source "$VENV_DIR/bin/activate"
    cd "$BACKEND_DIR"
    
    # Check if port is in use
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $BACKEND_PORT is already in use. Stopping existing process..."
        kill $(lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t) 2>/dev/null || true
        sleep 2
    fi
    
    if [ "$MODE" = "prod" ]; then
        # Production mode
        nohup uvicorn backend.main:app --host 0.0.0.0 --port $BACKEND_PORT > "$PROJECT_DIR/logs/backend.log" 2>&1 &
    else
        # Development mode with reload
        nohup uvicorn backend.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > "$PROJECT_DIR/logs/backend.log" 2>&1 &
    fi
    
    BACKEND_PID=$!
    echo "backend:$BACKEND_PID" >> "$PID_FILE"
    
    # Wait for backend to start
    sleep 3
    
    if curl -s "http://localhost:$BACKEND_PORT/health" > /dev/null 2>&1; then
        print_success "Backend started successfully (PID: $BACKEND_PID)"
        echo -e "  ${PURPLE}→ API:${NC}     http://localhost:$BACKEND_PORT"
        echo -e "  ${PURPLE}→ Docs:${NC}    http://localhost:$BACKEND_PORT/api/docs"
        echo -e "  ${PURPLE}→ Health:${NC}  http://localhost:$BACKEND_PORT/health"
    else
        print_error "Backend failed to start. Check logs/backend.log"
        return 1
    fi
}

start_frontend() {
    if [ ! -d "$FRONTEND_DIR" ] || [ ! -f "$FRONTEND_DIR/package.json" ]; then
        print_warning "Frontend directory not found. Skipping..."
        return 0
    fi
    
    print_status "Starting frontend server on port $FRONTEND_PORT..."
    
    cd "$FRONTEND_DIR"
    
    # Check if port is in use
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $FRONTEND_PORT is already in use. Stopping existing process..."
        kill $(lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t) 2>/dev/null || true
        sleep 2
    fi
    
    # Set API URL for frontend
    export VITE_API_URL="http://localhost:$BACKEND_PORT"
    
    if [ "$MODE" = "prod" ]; then
        # Production mode - build and serve
        npm run build --silent
        nohup npx serve -s dist -l $FRONTEND_PORT > "$PROJECT_DIR/logs/frontend.log" 2>&1 &
    else
        # Development mode
        nohup npm run dev -- --port $FRONTEND_PORT --host > "$PROJECT_DIR/logs/frontend.log" 2>&1 &
    fi
    
    FRONTEND_PID=$!
    echo "frontend:$FRONTEND_PID" >> "$PID_FILE"
    
    cd "$PROJECT_DIR"
    
    # Wait for frontend to start
    sleep 5
    
    if curl -s "http://localhost:$FRONTEND_PORT" > /dev/null 2>&1; then
        print_success "Frontend started successfully (PID: $FRONTEND_PID)"
        echo -e "  ${PURPLE}→ App:${NC}     http://localhost:$FRONTEND_PORT"
    else
        print_warning "Frontend may still be starting. Check logs/frontend.log"
    fi
}

stop_services() {
    print_status "Stopping all services..."
    
    # Stop from PID file
    if [ -f "$PID_FILE" ]; then
        while IFS=':' read -r service pid; do
            if ps -p "$pid" > /dev/null 2>&1; then
                kill "$pid" 2>/dev/null || true
                print_status "Stopped $service (PID: $pid)"
            fi
        done < "$PID_FILE"
        rm -f "$PID_FILE"
    fi
    
    # Also kill by port
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        kill $(lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t) 2>/dev/null || true
    fi
    
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        kill $(lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t) 2>/dev/null || true
    fi
    
    # Kill any remaining uvicorn processes for this project
    pkill -f "uvicorn backend.main" 2>/dev/null || true
    
    print_success "All services stopped"
}

show_help() {
    echo "Usage: ./start.sh [options]"
    echo ""
    echo "Options:"
    echo "  --backend-only    Start only the backend API server"
    echo "  --frontend-only   Start only the frontend development server"
    echo "  --dev             Development mode with hot reload (default)"
    echo "  --prod            Production mode"
    echo "  --stop            Stop all running services"
    echo "  --install         Install/update dependencies only"
    echo "  --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./start.sh                    # Start all services in dev mode"
    echo "  ./start.sh --backend-only     # Start only backend"
    echo "  ./start.sh --prod             # Start in production mode"
    echo "  ./start.sh --stop             # Stop all services"
}

# ============================================
# Parse Arguments
# ============================================

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-only)
            START_FRONTEND=false
            shift
            ;;
        --frontend-only)
            START_BACKEND=false
            shift
            ;;
        --dev)
            MODE="dev"
            shift
            ;;
        --prod)
            MODE="prod"
            shift
            ;;
        --stop)
            stop_services
            exit 0
            ;;
        --install)
            check_requirements
            install_dependencies
            exit 0
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# ============================================
# Main Execution
# ============================================

print_banner

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"

# Clear old PID file
rm -f "$PID_FILE"

# Check requirements
check_requirements

# Install dependencies if needed
if [ ! -f "$PROJECT_DIR/.deps_installed" ] || [ "$1" = "--install" ]; then
    install_dependencies
    touch "$PROJECT_DIR/.deps_installed"
fi

# Start services
echo ""
print_status "Starting services in ${MODE} mode..."
echo ""

if [ "$START_BACKEND" = true ]; then
    start_backend
    echo ""
fi

if [ "$START_FRONTEND" = true ]; then
    start_frontend
    echo ""
fi

# Summary
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  🚀 Hydro-Logic Trust Layer is running!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${CYAN}Backend API:${NC}    http://localhost:$BACKEND_PORT"
echo -e "  ${CYAN}API Docs:${NC}       http://localhost:$BACKEND_PORT/api/docs"
if [ "$START_FRONTEND" = true ]; then
echo -e "  ${CYAN}Frontend App:${NC}   http://localhost:$FRONTEND_PORT"
fi
echo ""
echo -e "  ${YELLOW}To stop all services:${NC} ./start.sh --stop"
echo -e "  ${YELLOW}View logs:${NC} tail -f logs/backend.log logs/frontend.log"
echo ""
