#!/bin/bash

# Instala dependências
pip install -r requirements/analytics.txt

# Executa testes
pytest tests/analytics/ -v --asyncio-mode=strict

# Verifica cobertura
pytest tests/analytics/ --cov=src/analytics --cov-report=term-missing 