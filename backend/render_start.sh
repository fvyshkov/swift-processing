#!/usr/bin/env bash
# Render start script for backend

set -o errexit

cd backend
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

