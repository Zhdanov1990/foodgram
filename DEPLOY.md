# Инструкция по развертыванию проекта

## Подготовка сервера

1. Подключитесь к серверу:
```bash
ssh yc-user@158.160.26.203
```

2. Установите Docker и Docker Compose:
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
```

3. Создайте директорию для проекта:
```bash
mkdir -p ~/foodgram
```

## Настройка GitHub Actions

1. Добавьте следующие секреты в настройках репозитория:
- `DOCKER_USERNAME` - имя пользователя Docker Hub
- `DOCKER_PASSWORD` - пароль Docker Hub
- `HOST` - IP-адрес сервера
- `USERNAME` - имя пользователя на сервере
- `SSH_KEY` - приватный SSH-ключ
- `SSH_PASSPHRASE` - пароль от SSH-ключа

2. Создайте файл `.env` на сервере:
```bash
cd ~/foodgram
nano .env
```

Содержимое файла:
```
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

3. Скопируйте файлы проекта на сервер:
```bash
scp docker-compose.yml yc-user@158.160.26.203:~/foodgram/
scp -r infra/ yc-user@158.160.26.203:~/foodgram/
```

## Развертывание

1. Запустите проект:
```bash
cd ~/foodgram
docker compose up -d
```

2. Примените миграции:
```bash
docker compose exec backend python manage.py migrate
```

3. Создайте суперпользователя:
```bash
docker compose exec backend python manage.py createsuperuser
```

4. Соберите статические файлы:
```bash
docker compose exec backend python manage.py collectstatic --noinput
```

## Проверка работоспособности

1. Проверьте статус контейнеров:
```bash
docker compose ps
```

2. Проверьте логи:
```bash
docker compose logs
```

3. Откройте сайт в браузере:
```
http://158.160.26.203
``` 