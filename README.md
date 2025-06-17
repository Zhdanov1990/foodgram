# Foodgram

Сервис для публикации рецептов. Пользователи могут создавать рецепты, подписываться на публикации других авторов, добавлять понравившиеся рецепты в список избранного, а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Технологии

- Python 3.9
- Django 3.2
- Django REST Framework
- PostgreSQL
- Docker
- Nginx
- React
- Node.js

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/foodgram.git
cd foodgram
```

2. Создайте файл `.env` в корневой директории проекта:
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

3. Запустите проект с помощью Docker Compose:
```bash
docker compose up -d
```

4. Примените миграции:
```bash
docker compose exec backend python manage.py migrate
```

5. Создайте суперпользователя:
```bash
docker compose exec backend python manage.py createsuperuser
```

6. Соберите статические файлы:
```bash
docker compose exec backend python manage.py collectstatic --noinput
```

## API Endpoints

- `/api/users/` - управление пользователями
- `/api/auth/token/login/` - получение токена
- `/api/auth/token/logout/` - выход из системы
- `/api/recipes/` - управление рецептами
- `/api/tags/` - управление тегами
- `/api/ingredients/` - управление ингредиентами

## Автор

- [Ваше имя](https://github.com/your-username)

Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.

