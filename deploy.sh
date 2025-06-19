#!/bin/bash

# Остановка и удаление старых контейнеров
docker compose down

# Удаление старых образов
docker rmi foodgram_backend foodgram_frontend

# Получение последних изменений
git pull

# Сборка и запуск новых контейнеров
docker compose up -d --build

# Очистка неиспользуемых образов
docker image prune -f

