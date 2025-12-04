#!/bin/bash

echo "🔍 Running pre-commit checks..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar si estamos en la raíz del proyecto
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Error: Debe ejecutarse desde la raíz del proyecto${NC}"
    exit 1
fi

# Variable para rastrear si hubo errores CRÍTICOS (solo tests)
has_critical_errors=0
has_warnings=0

# ============================================
# BACKEND CHECKS
# ============================================
echo -e "\n${YELLOW}📦 Verificando Backend...${NC}"

cd backend

# Activar entorno virtual si existe (compatible con Windows y Unix)
if [ -d "venv" ]; then
    if [ -f "venv/Scripts/activate" ]; then
        # Windows
        source venv/Scripts/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
        PYTHON_CMD="venv/Scripts/python.exe"
    elif [ -f "venv/bin/activate" ]; then
        # Unix/Linux/Mac
        source venv/bin/activate
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python"
fi

# Pylint
echo "  → Ejecutando Pylint..."
$PYTHON_CMD -m pylint user/ userInfo/ raffle/ raffleInfo/ tickets/ interactions/ location/ permissions/ --fail-under=9.0 --reports=n
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}  ⚠ Pylint encontró problemas (advertencia)${NC}"
    has_warnings=1
else
    echo -e "${GREEN}  ✓ Pylint OK${NC}"
fi

# Black (verificar formato)
echo "  → Verificando formato con Black..."
$PYTHON_CMD -m black --check user/ userInfo/ raffle/ raffleInfo/ tickets/ interactions/ location/ permissions/ tests/ --quiet
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}  ⚠ Código no formateado. Ejecuta: cd backend && black .${NC}"
    has_warnings=1
else
    echo -e "${GREEN}  ✓ Formato OK${NC}"
fi

# Bandit (seguridad)
echo "  → Verificando seguridad con Bandit..."
$PYTHON_CMD -m bandit -r user/ userInfo/ raffle/ raffleInfo/ tickets/ interactions/ location/ permissions/ -ll --quiet
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}  ⚠ Bandit encontró problemas de seguridad (advertencia)${NC}"
    has_warnings=1
else
    echo -e "${GREEN}  ✓ Seguridad OK${NC}"
fi

# Tests (CRÍTICO - bloquea commit)
echo "  → Ejecutando tests..."
$PYTHON_CMD -m pytest --quiet --tb=no
if [ $? -ne 0 ]; then
    echo -e "${RED}  ✗ Tests fallaron (CRÍTICO - bloquea commit)${NC}"
    has_critical_errors=1
else
    echo -e "${GREEN}  ✓ Tests OK${NC}"
fi

cd ..

# ============================================
# FRONTEND CHECKS
# ============================================
echo -e "\n${YELLOW}🎨 Verificando Frontend...${NC}"

cd frontend

# ESLint
echo "  → Ejecutando ESLint..."
npm run lint -- --quiet
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}  ⚠ ESLint encontró problemas (advertencia)${NC}"
    has_warnings=1
else
    echo -e "${GREEN}  ✓ ESLint OK${NC}"
fi

# Prettier (verificar formato)
echo "  → Verificando formato con Prettier..."
npm run format:check -- --log-level error
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}  ⚠ Código no formateado. Ejecuta: cd frontend && npm run format${NC}"
    has_warnings=1
else
    echo -e "${GREEN}  ✓ Formato OK${NC}"
fi

cd ..

# ============================================
# RESULTADO FINAL
# ============================================
echo ""
if [ $has_critical_errors -eq 1 ]; then
    echo -e "${RED}❌ Pre-commit checks fallaron: Los tests tienen errores.${NC}"
    echo -e "${RED}   Por favor corrige los errores de tests antes de hacer commit.${NC}"
    exit 1
elif [ $has_warnings -eq 1 ]; then
    echo -e "${YELLOW}⚠️  Advertencias encontradas (no bloquean el commit):${NC}"
    echo -e "${YELLOW}   - Revisa los problemas de linting/formato cuando puedas${NC}"
    echo -e "${GREEN}✅ Commit permitido (los tests pasaron)${NC}"
    exit 0
else
    echo -e "${GREEN}✅ Todos los checks pasaron correctamente!${NC}"
    exit 0
fi
