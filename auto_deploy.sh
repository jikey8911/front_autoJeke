#!/bin/bash
# Script de auto-despliegue para Cron / Webhook
# Ejecutar directamente en la VM (fuera del contenedor)

cd /root/.openclaw/workspace/front_autoJeke
echo "--- Iniciando Auto-Despliegue ---"
git pull origin main

echo "Reconstruyendo y reiniciando contenedores..."
docker compose up -d --build backend frontend

echo "--- Despliegue Completado ---"
