# Foodgram

Сервис для публикации рецептов. Пользователи могут создавать рецепты, подписываться на публикации других авторов, добавлять понравившиеся рецепты в список избранного, а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

**Проект доступен по адресу: [https://foodgram-menu.zapto.org/recipes](https://foodgram-menu.zapto.org/recipes)**

## Функциональность

### Для авторизованных пользователей:
- Создание, редактирование и удаление рецептов
- Добавление рецептов в избранное
- Подписка на других авторов
- Добавление рецептов в список покупок
- Скачивание списка покупок
- Загрузка и изменение аватара
- Изменение пароля

### Для всех пользователей:
- Просмотр рецептов
- Фильтрация по тегам
- Поиск рецептов
- Просмотр профилей авторов
- Регистрация и авторизация

## Технологии

### Backend:
- Python 3.9
- Django 4.2.23
- Django REST Framework 3.16.0
- Djoser 2.3.1 (аутентификация)
- Django Filter 25.1
- Django CORS Headers 4.7.0
- DRF Simple JWT 5.5.0
- Gunicorn 23.0.0
- PostgreSQL 13
- Pillow 11.2.1 (работа с изображениями)

### Frontend:
- React 17.0.1
- React Router DOM 5.2.0
- React Meta Tags 1.0.1
- React Tooltip 5.21.6
- CSS Modules
- Classnames 2.2.6

### DevOps:
- Docker & Docker Compose
- Nginx
- GitHub Actions

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Zhdanov1990/foodgram.git
cd foodgram
```

2. Создайте файл `.env` в корневой директории проекта:
```
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.postgresql
DB_NAME=foodgram
DB_USER=foodgram_user
DB_PASSWORD=foodgram_password
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

### Аутентификация:
- `POST /api/auth/token/login/` - получение токена
- `POST /api/auth/token/logout/` - выход из системы

### Пользователи:
- `GET /api/users/` - список пользователей
- `GET /api/users/{id}/` - профиль пользователя
- `GET /api/users/me/` - текущий пользователь
- `POST /api/users/` - регистрация

### Рецепты:
- `GET /api/recipes/` - список рецептов
- `POST /api/recipes/` - создание рецепта
- `GET /api/recipes/{id}/` - детали рецепта
- `PATCH /api/recipes/{id}/` - редактирование рецепта
- `DELETE /api/recipes/{id}/` - удаление рецепта
- `GET /api/recipes/download_shopping_cart/` - скачать список покупок

### Подписки:
- `GET /api/users/subscriptions/` - мои подписки
- `POST /api/users/{id}/subscribe/` - подписаться на автора
- `DELETE /api/users/{id}/subscribe/` - отписаться от автора

### Избранное:
- `GET /api/recipes/favorite/` - избранные рецепты
- `POST /api/recipes/{id}/favorite/` - добавить в избранное
- `DELETE /api/recipes/{id}/favorite/` - убрать из избранного

### Список покупок:
- `GET /api/recipes/shopping_cart/` - список покупок
- `POST /api/recipes/{id}/shopping_cart/` - добавить в список покупок
- `DELETE /api/recipes/{id}/shopping_cart/` - убрать из списка покупок

### Теги и ингредиенты:
- `GET /api/tags/` - список тегов
- `GET /api/ingredients/` - список ингредиентов

## Документация API

API документация доступна по адресу: `http://localhost/api/docs/` (Swagger UI)

## Автор

- [Сергей Жданов](https://github.com/Zhdanov1990)



