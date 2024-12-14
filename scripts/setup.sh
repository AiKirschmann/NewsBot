#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода статуса
print_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[✓] $1${NC}"
    else
        echo -e "${RED}[✗] $1${NC}"
        exit 1
    fi
}

echo -e "${YELLOW}Starting setup...${NC}"

# Проверка наличия Python 3.10+
echo -e "${YELLOW}Checking Python version...${NC}"
python3 --version || {
    echo -e "${RED}Error: Python 3.10+ required${NC}"
    exit 1
}
print_status "Python version check"

# Активация виртуального окружения
echo -e "${YELLOW}Activating virtual environment...${NC}"
source myenv/bin/activate || {
    echo -e "${RED}Error: Could not activate virtual environment${NC}"
    exit 1
}
print_status "Virtual environment activated"

# Обновление pip
echo -e "${YELLOW}Updating pip...${NC}"
python -m pip install --upgrade pip
print_status "Pip updated"

# Установка зависимостей
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt
print_status "Dependencies installed"

# Проверка конфигурации
echo -e "${YELLOW}Checking configuration...${NC}"
if [ ! -f "config/settings.py" ]; then
    echo -e "${RED}Error: config/settings.py not found${NC}"
    exit 1
fi
print_status "Configuration check"

# Создание необходимых директорий
echo -e "${YELLOW}Creating required directories...${NC}"
mkdir -p logs
mkdir -p database
print_status "Directories created"

# Запуск бота
echo -e "${YELLOW}Starting bot...${NC}"
python main.py

# Проверка статуса
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Bot started successfully${NC}"
else
    echo -e "${RED}Error starting bot${NC}"
    exit 1
fi
