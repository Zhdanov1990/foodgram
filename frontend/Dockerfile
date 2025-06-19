# build env
FROM node:16-alpine AS builder
WORKDIR /app
COPY package.json .
RUN npm install --legacy-peer-deps
COPY . .
RUN npm run build

FROM alpine
WORKDIR /app
COPY --from=builder /app/build /build
CMD ["sh", "-c", "cp -r /build/* /static_frontend_build/ && echo 'Frontend build copied successfully'"]
