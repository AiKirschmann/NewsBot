#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Starting bot setup...${NC}"

# Проверка на уже запущенный процесс
if [ -f "bot.pid" ]; then
    PID=$(cat bot.pid)
    if ps -p $PID > /dev/null; then
        echo -e "${RED}Bot is already running with PID: $PID${NC}"
        echo "Use ./stop_bot.sh to stop it first"
        exit 1
    else
        rm bot.pid
    fi
fi

# Убиваем все процессы Python, содержащие main.py
pkill -f "python.*main.py"
sleep 2

# Очищаем webhook
echo "Clearing webhook..."
curl -s "https://api.telegram.org/bot$(grep TELEGRAM_TOKEN .env | cut -d '=' -f2)/deleteWebhook?drop_pending_updates=true"
sleep 2

# Проверка наличия Python
python3 --version || {
    echo -e "${RED}Python 3.10+ required${NC}"
    exit 1
}

# Активация виртуального окружения
source myenv/bin/activate

# Установка зависимостей
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}[✓] Dependencies installed${NC}"

# Проверка конфигурации
echo "Checking configuration..."
if [ ! -f "config/settings.py" ]; then
    echo -e "${RED}Error: config/settings.py not found${NC}"
    exit 1
fi
echo -e "${GREEN}[✓] Configuration check${NC}"

# Создание необходимых директорий
echo "Creating required directories..."
mkdir -p logs
mkdir -p database
echo -e "${GREEN}[✓] Directories created${NC}"

# Запуск бота
echo "Starting bot..."
python3 main.py & echo $! > bot.pid

# Проверка запуска
sleep 2
if [ -f "bot.pid" ]; then
    PID=$(cat bot.pid)
    if ps -p $PID > /dev/null; then
        echo -e "${GREEN}Bot started successfully with PID: $PID${NC}"
    else
        echo -e "${RED}Failed to start bot${NC}"
        rm bot.pid
        exit 1
    fi
else
    echo -e "${RED}Failed to create PID file${NC}"
    exit 1
fi
