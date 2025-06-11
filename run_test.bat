@echo off
set OPENAI_API_KEY=your_openai_api_key_here
cd /d %~dp0
python test_chat_api.py
pause 