# build env
FROM node:16-alpine AS builder
WORKDIR /app
COPY package.json .
RUN npm install --legacy-peer-deps
COPY . .
RUN npm run build

FROM node:16-alpine
WORKDIR /app
COPY --from=builder /app/build /app/build
CMD ["sh", "-c", "cp -r /app/build/* /usr/share/nginx/html/ && echo 'Frontend build copied successfully'"]
