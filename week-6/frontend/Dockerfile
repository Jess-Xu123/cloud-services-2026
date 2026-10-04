# syntax=docker/dockerfile:1
FROM nginx:1.27-alpine
RUN rm -rf /etc/nginx/conf.d/*
# Copy Nginx config and static assets
COPY frontend/nginx.conf /etc/nginx/nginx.conf
COPY frontend/index.html /usr/share/nginx/html/index.html
EXPOSE 8080