#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
cp .env.example .env.local
echo "✅ Ambiente local configurado"