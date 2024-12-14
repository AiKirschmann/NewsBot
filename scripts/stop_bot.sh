#!/bin/bash

# Находим PID процесса бота
BOT_PID=$(ps aux | grep "python.*main.py" | grep -v grep | awk '{print $2}')

if [ ! -z "$BOT_PID" ]; then
    echo "Stopping bot process (PID: $BOT_PID)..."
    kill $BOT_PID
    sleep 2
    
    # Проверяем, остановился ли процесс
    if ps -p $BOT_PID > /dev/null; then
        echo "Force stopping bot process..."
        kill -9 $BOT_PID
    fi
    
    echo "Bot stopped successfully"
else
    echo "Bot process not found"
fi

# Удаляем PID файл если он существует
if [ -f "bot.pid" ]; then
    rm bot.pid
    echo "Removed PID file"
fi
