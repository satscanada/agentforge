# AgentForge Backend

FastAPI + Jinja2 backend for the AgentForge scaffold generator.

This directory is intentionally a checkpoint-1 stub. Future checkpoints add:

- `app/main.py` with `/health`
- Pydantic request/response models
- Jinja2 generator engine and templates
- ZIP generation and download endpoints

## Local Python

Use the repo-level `pyenv` environment before running the backend:

```bash
cd ..
pyenv local 3.12.12
cd backend
pyenv version
python --version
pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload --port 8000
```

## Tests

Run the backend tests with the dev requirements installed:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests/test_e2e.py -q
```
