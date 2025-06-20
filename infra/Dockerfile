FROM nginx:1.25.4-alpine

# Копируем наш Nginx конфиг
COPY nginx.conf /etc/nginx/nginx.conf

# Создаем директории для статики и медиа
RUN mkdir -p /usr/share/nginx/static /usr/share/nginx/media
