#!/bin/bash

# Validation script to check if the deployment environment is ready
# Run this before deploying to EC2

echo "================================================"
echo "Deployment Validation Script"
echo "================================================"

ERRORS=0
WARNINGS=0

# Function to print success message
success() {
    echo "✓ $1"
}

# Function to print error message
error() {
    echo "✗ ERROR: $1"
    ((ERRORS++))
}

# Function to print warning message
warning() {
    echo "⚠ WARNING: $1"
    ((WARNINGS++))
}

# Function to print info message
info() {
    echo "ℹ INFO: $1"
}

echo ""
echo "[1/7] Checking project structure..."
if [ ! -d "app" ]; then
    error "app/ directory not found"
else
    success "app/ directory exists"
fi

if [ ! -f "app/main.py" ]; then
    error "app/main.py not found"
else
    success "app/main.py exists"
fi

if [ ! -f "app/processing.py" ]; then
    error "app/processing.py not found"
else
    success "app/processing.py exists"
fi

if [ ! -f "app/utils.py" ]; then
    error "app/utils.py not found"
else
    success "app/utils.py exists"
fi

if [ ! -f "app/models.py" ]; then
    error "app/models.py not found"
else
    success "app/models.py exists"
fi

echo ""
echo "[2/7] Checking configuration files..."
if [ ! -f "requirements.txt" ]; then
    error "requirements.txt not found"
else
    success "requirements.txt exists"
    
    # Check if requirements.txt has content
    if [ ! -s "requirements.txt" ]; then
        error "requirements.txt is empty"
    else
        success "requirements.txt has content"
        info "Dependencies: $(wc -l < requirements.txt) packages"
    fi
fi

if [ ! -f "start.sh" ]; then
    error "start.sh not found"
else
    success "start.sh exists"
    
    # Check if start.sh is executable
    if [ ! -x "start.sh" ]; then
        warning "start.sh is not executable (will be fixed with chmod +x)"
    else
        success "start.sh is executable"
    fi
fi

echo ""
echo "[3/7] Checking Python syntax..."
if command -v python3 &> /dev/null; then
    success "Python 3 is available"
    
    # Check Python files syntax
    for pyfile in app/*.py; do
        if [ -f "$pyfile" ]; then
            if python3 -m py_compile "$pyfile" 2>/dev/null; then
                success "$(basename $pyfile) - syntax OK"
            else
                error "$(basename $pyfile) - syntax error"
            fi
        fi
    done
else
    warning "Python 3 not found (will be installed on EC2)"
fi

echo ""
echo "[4/7] Checking required Python packages in requirements.txt..."
REQUIRED_PACKAGES=("fastapi" "uvicorn" "ultralytics" "huggingface-hub" "pytesseract" "pillow" "opencv-python" "numpy")

for package in "${REQUIRED_PACKAGES[@]}"; do
    if grep -q "$package" requirements.txt; then
        success "$package listed in requirements.txt"
    else
        error "$package missing from requirements.txt"
    fi
done

echo ""
echo "[5/7] Checking for unnecessary files..."
if [ -d "venv" ]; then
    warning "venv/ directory exists - should be excluded from deployment"
    info "Add venv/ to .gitignore or exclude during upload"
fi

if [ -d "__pycache__" ]; then
    warning "__pycache__/ directory exists - should be excluded from deployment"
fi

if [ -d ".git" ]; then
    success ".git/ directory exists (using version control)"
else
    warning "No .git/ directory - consider using version control"
fi

echo ""
echo "[6/7] Checking documentation..."
if [ -f "README.md" ]; then
    success "README.md exists"
else
    warning "README.md not found"
fi

if [ -f "EC2_DEPLOYMENT.md" ]; then
    success "EC2_DEPLOYMENT.md exists"
else
    warning "EC2_DEPLOYMENT.md not found"
fi

echo ""
echo "[7/7] Checking file permissions..."
for script in *.sh; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            success "$script is executable"
        else
            warning "$script is not executable (run: chmod +x $script)"
        fi
    fi
done

echo ""
echo "================================================"
echo "Validation Summary"
echo "================================================"
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo "✓ All critical checks passed!"
    echo ""
    echo "Next steps:"
    echo "1. Upload files to EC2 (exclude venv, __pycache__, .git)"
    echo "2. SSH into EC2 instance"
    echo "3. Run: chmod +x start.sh"
    echo "4. Run: ./start.sh"
    echo ""
    echo "For detailed instructions, see EC2_DEPLOYMENT.md"
    exit 0
else
    echo "✗ Found $ERRORS critical error(s)"
    echo "Please fix the errors before deploying to EC2"
    exit 1
fi
