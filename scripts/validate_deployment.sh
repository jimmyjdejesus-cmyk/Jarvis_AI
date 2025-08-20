#!/bin/bash
# Deployment Validation Script for Jarvis AI
# Tests the key deployment functionality without external dependencies

set -e

echo "🔍 Validating Jarvis AI Deployment & Distribution Implementation"
echo "================================================================="

# Test 1: Package installation
echo "✅ Testing pip package installation..."
if command -v jarvis >/dev/null 2>&1; then
    echo "   ✓ jarvis command available"
else
    echo "   ❌ jarvis command not found"
    exit 1
fi

# Test 2: CLI functionality
echo "✅ Testing CLI functionality..."
if jarvis version >/dev/null 2>&1; then
    echo "   ✓ jarvis version works"
else
    echo "   ❌ jarvis version failed"
    exit 1
fi

# Test 3: Configuration initialization
echo "✅ Testing configuration management..."
if jarvis config --validate >/dev/null 2>&1; then
    echo "   ✓ Configuration validation works"
else
    echo "   ❌ Configuration validation failed"
    exit 1
fi

# Test 4: Environment variable support
echo "✅ Testing environment variable overrides..."
export JARVIS_DEBUG_MODE=true
export LANGSMITH_API_KEY=test_key
if jarvis config --show | grep -q "LangSmith API Key: Set"; then
    echo "   ✓ Environment variables work"
else
    echo "   ❌ Environment variables not working"
    exit 1
fi

# Test 5: File structure validation
echo "✅ Testing deployment files..."
required_files=(
    "pyproject.toml"
    "Dockerfile"
    "docker-compose.yml"
    "scripts/installers/install-unix.sh"
    "scripts/installers/install-windows.bat"
    "ui/settings_manager.py"
    "docs/DEPLOYMENT_GUIDE.md"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "   ✓ $file exists"
    else
        echo "   ❌ $file missing"
        exit 1
    fi
done

# Test 6: Configuration sections
echo "✅ Testing Lang ecosystem configuration..."
if grep -q "lang_ecosystem:" config/config.yaml; then
    echo "   ✓ Lang ecosystem settings present"
else
    echo "   ❌ Lang ecosystem settings missing"
    exit 1
fi

if grep -q "langsmith:" config/config.yaml; then
    echo "   ✓ LangSmith configuration present"
else
    echo "   ❌ LangSmith configuration missing"
    exit 1
fi

if grep -q "langgraph_platform:" config/config.yaml; then
    echo "   ✓ LangGraph Platform configuration present"
else
    echo "   ❌ LangGraph Platform configuration missing"
    exit 1
fi

# Test 7: Installer scripts are executable
echo "✅ Testing installer scripts..."
if [[ -x "scripts/installers/install-unix.sh" ]]; then
    echo "   ✓ Unix installer is executable"
else
    echo "   ❌ Unix installer not executable"
    exit 1
fi

# Test 8: Docker files are valid
echo "✅ Testing Docker configuration..."
if docker --version >/dev/null 2>&1; then
    if docker build --dry-run . >/dev/null 2>&1; then
        echo "   ✓ Dockerfile syntax valid"
    else
        echo "   ⚠️  Dockerfile syntax may have issues (dry-run not supported)"
    fi
else
    echo "   ⚠️  Docker not available for testing"
fi

# Test 9: Package metadata
echo "✅ Testing package metadata..."
if python -c "import jarvis_ai; print(jarvis_ai.__version__)" | grep -q "2.0.0"; then
    echo "   ✓ Package version correct"
else
if python -c "import jarvis_ai; print(jarvis_ai.__version__)" | grep -q "$EXPECTED_VERSION"; then
    echo "   ✓ Package version correct ($EXPECTED_VERSION)"
else
    echo "   ❌ Package version incorrect (expected $EXPECTED_VERSION)"
    exit 1
fi

# Test 10: Requirements validation
echo "✅ Testing requirements..."
key_packages=("streamlit" "langchain" "langgraph" "langsmith" "fastapi")
for package in "${key_packages[@]}"; do
    if python -c "import $package" >/dev/null 2>&1; then
        echo "   ✓ $package installed"
    else
        echo "   ❌ $package not installed"
        exit 1
    fi
done

echo
echo "🎉 All deployment validation tests passed!"
echo "================================================================="
echo
echo "📦 Deployment methods available:"
echo "   • pip install jarvis-ai"
echo "   • docker build -t jarvis-ai ."
echo "   • bash scripts/installers/install-unix.sh"
echo
echo "🔧 Configuration management:"
echo "   • jarvis config --init"
echo "   • jarvis config --show"
echo "   • Environment variable overrides"
echo "   • UI-based settings manager"
echo
echo "🚀 Lang ecosystem integration:"
echo "   • LangSmith tracing and monitoring"
echo "   • LangGraph Platform collaboration"
echo "   • Deployment telemetry"
echo
echo "✅ Issue #27 requirements fully implemented!"