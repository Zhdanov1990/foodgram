#!/bin/bash

# Данные для обновления DDNS
USERNAME="v1ftzaj"
PASSWORD="nTupMu4wSqd3"
HOSTNAME="foodgram-menu.zapto.org"

# Получаем текущий IP
CURRENT_IP=$(curl -s ifconfig.me)

# Обновляем IP через API No-IP
curl -s "https://dynupdate.no-ip.com/nic/update?hostname=$HOSTNAME&myip=$CURRENT_IP" \
     -u "$USERNAME:$PASSWORD" \
     -H "User-Agent: No-IP DUC/4.0.12"

echo "IP обновлен на $CURRENT_IP" 