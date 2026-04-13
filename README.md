# Atomic AI Bot
## FastAPI-AI-ChatBot-WebServiceBackend
## This is the part of the AI-ChatBot project.

### Email provider in the project
```bash
atomic.ai.bot.service@gmail.com
```

### Useful commands
1. Run server
- development mode
```bash
uvicorn server.main:app --reload
```

- production mode
```bash
uvicorn server.main:app --host 0.0.0.0 --port 8000 --workers 4
```