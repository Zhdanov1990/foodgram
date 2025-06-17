# Инструкция по деплою проекта Foodgram

## Подготовка сервера

1. Создать директорию для проекта:
```bash
mkdir -p ~/foodgram
```

2. Скопировать файлы на сервер:
```bash
scp -i ~/.ssh/kikki1/yc-auto27parts docker-compose.yml .env deploy.sh update_ddns.sh yc-user@158.160.26.203:~/foodgram/
```

3. Подключиться к серверу:
```bash
ssh -i ~/.ssh/kikki1/yc-auto27parts yc-user@158.160.26.203
```

4. Перейти в директорию проекта:
```bash
cd ~/foodgram
```

5. Сделать скрипты исполняемыми:
```bash
chmod +x deploy.sh update_ddns.sh
```

6. Запустить деплой:
```bash
./deploy.sh
```

## Настройка GitHub Actions

1. Добавить секреты в настройках репозитория:
   - `HOST`: 158.160.26.203
   - `USERNAME`: yc-user
   - `SSH_KEY`: приватный ключ

2. После настройки секретов, каждый push в ветку main будет автоматически запускать деплой.

## Проверка работы

1. Проверить статус контейнеров:
```bash
docker compose ps
```

2. Проверить логи:
```bash
docker compose logs
```

3. Проверить доступность сайта:
```bash
curl http://localhost
```

## Обновление IP-адреса

IP-адрес обновляется автоматически при каждом деплое через скрипт `update_ddns.sh`.
Для ручного обновления IP-адреса:
```bash
./update_ddns.sh
``` 