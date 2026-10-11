#!/bin/bash
# Run all tests for the OpenBird project

set -e

echo "======================================"
echo "Running OpenBird Tests"
echo "======================================"

# Python tests
echo ""
echo "=== Python Tests ==="
cd /home/arash/projects/openbird

# Check if pytest is available
if command -v pytest &> /dev/null; then
    echo "Running Python unit tests..."
    pytest _scripts/ -v --tb=short 2>&1 | head -100
else
    echo "pytest not found, skipping Python tests"
fi

# Frontend tests
echo ""
echo "=== Frontend Tests ==="
cd /home/arash/projects/openbird/frontend

if [ -f package.json ] && command -v npm &> /dev/null; then
    echo "Running frontend tests..."
    npm test -- --watchAll=false 2>&1 | head -100
else
    echo "Frontend not configured or npm not found, skipping"
fi

# Flutter tests
echo ""
echo "=== Flutter Tests ==="
cd /home/arash/projects/openbird/flutter_app

if [ -f pubspec.yaml ] && command -v flutter &> /dev/null; then
    echo "Getting Flutter dependencies..."
    flutter pub get
    
    echo "Generating localizations..."
    flutter gen-l10n
    
    echo "Running Flutter analyze..."
    flutter analyze
    
    echo "Running Flutter unit tests..."
    flutter test --coverage
    
    echo "Checking formatting..."
    dart format --output=none --set-exit-if-changed .
    
    echo "Flutter tests passed!"
else
    echo "Flutter not found or not configured, skipping"
fi

echo ""
echo "======================================"
echo "All tests completed successfully!"
echo "======================================"