#!/bin/bash
# Script para configurar el entorno virtual
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Entorno virtual configurado correctamente"
echo "Para activarlo: source venv/bin/activate"
