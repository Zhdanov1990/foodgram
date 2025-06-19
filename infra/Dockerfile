FROM nginx:1.25.4-alpine

COPY nginx.conf /etc/nginx/nginx.conf

# Создаем директории для static и media
RUN mkdir -p /usr/share/nginx/static /usr/share/nginx/media

# Frontend build будет скопирован сюда при сборке образа
# (нужно будет добавить COPY build/ /usr/share/nginx/html/ после сборки frontend) 