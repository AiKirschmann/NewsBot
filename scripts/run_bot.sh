#!/bin/bash
cd ~/newsbot
source ~/myenv/bin/activate
nohup python main.py > bot.log 2>&1 &
echo $! > bot.pid
echo "Bot started in background. PID: $(cat bot.pid)"
echo "Check bot.log for output"
