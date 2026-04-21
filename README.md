# Atomic AI Bot

## FastAPI-AI-ChatBot-WebServiceBackend
## This is the part of the AI-ChatBot project.

### Email provider
```bash
atomic.ai.bot.service@gmail.com
```

### Commands
1. Install dependencies
```bash
pip install -r requirements.txt
```
2. Run backend project
- development mode
```bash
uvicorn server.main:app --reload
```
- production mode
```bash
uvicorn server.main:app --host 0.0.0.0 --port 8000
```
3. Aider commands
- choose AI model
```bash
aider --model openrouter/anthropic/claude-sonnet-4.6
```
- run command
```bash
aider --no-show-model-warnings --no-pretty --yes --no-stream
```
