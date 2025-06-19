# Initial Setup

This document captures the initial directory structure and setup commands for the Validia project.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
``` 