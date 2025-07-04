#!/bin/bash

# Vector Database Test Runner
# This script runs different test suites for the vector database repository

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Vector Database Test Runner${NC}"
echo "=================================="

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}pytest is not installed. Installing test dependencies...${NC}"
    pip install -r tests/requirements.txt
fi

# Function to run tests with error handling
run_test_suite() {
    local test_name="$1"
    local test_path="$2"
    local test_args="$3"
    
    echo -e "\n${YELLOW}Running $test_name...${NC}"
    echo "----------------------------------------"
    
    if [ -n "$test_args" ]; then
        if pytest $test_path $test_args; then
            echo -e "${GREEN}✓ $test_name passed${NC}"
            return 0
        else
            echo -e "${RED}✗ $test_name failed${NC}"
            return 1
        fi
    else
        if pytest $test_path; then
            echo -e "${GREEN}✓ $test_name passed${NC}"
            return 0
        else
            echo -e "${RED}✗ $test_name failed${NC}"
            return 1
        fi
    fi
}

# Parse command line arguments
case "${1:-all}" in
    "unit")
        echo "Running unit tests only..."
        run_test_suite "Unit Tests" "tests/test_docker_compose.py tests/test_examples.py tests/test_faiss_api.py" ""
        ;;
    "docker")
        echo "Running Docker configuration tests..."
        run_test_suite "Docker Tests" "tests/test_docker_compose.py" ""
        ;;
    "api")
        echo "Running API tests..."
        run_test_suite "API Tests" "tests/test_faiss_api.py" ""
        ;;
    "examples")
        echo "Running example script tests..."
        run_test_suite "Example Tests" "tests/test_examples.py" ""
        ;;
    "integration")
        echo "Running integration tests (requires running services)..."
        run_test_suite "Integration Tests" "tests/test_integration.py" "-m integration"
        ;;
    "all")
        echo "Running all tests..."
        
        # Run unit tests first
        run_test_suite "Unit Tests" "tests/" "-m 'not integration'"
        unit_result=$?
        
        # Run integration tests if unit tests pass
        if [ $unit_result -eq 0 ]; then
            echo -e "\n${YELLOW}Unit tests passed. Running integration tests...${NC}"
            run_test_suite "Integration Tests" "tests/" "-m integration" || true
        fi
        ;;
    "coverage")
        echo "Running tests with coverage..."
        pytest tests/ --cov=. --cov-report=html --cov-report=term
        echo -e "\n${GREEN}Coverage report generated in htmlcov/index.html${NC}"
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [test_type]"
        echo ""
        echo "Available test types:"
        echo "  all         Run all tests (default)"
        echo "  unit        Run unit tests only"
        echo "  docker      Run Docker configuration tests"
        echo "  api         Run API tests"
        echo "  examples    Run example script tests"
        echo "  integration Run integration tests (requires services)"
        echo "  coverage    Run tests with coverage report"
        echo "  help        Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0                    # Run all tests"
        echo "  $0 unit              # Run only unit tests"
        echo "  $0 integration       # Run only integration tests"
        echo "  $0 coverage          # Run with coverage"
        exit 0
        ;;
    *)
        echo -e "${RED}Unknown test type: $1${NC}"
        echo "Use '$0 help' to see available options"
        exit 1
        ;;
esac

echo -e "\n${GREEN}Test run completed!${NC}"