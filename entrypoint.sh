#!/bin/sh

# Keluar segera jika ada perintah yang gagal
set -e

# Cek argumen pertama yang diberikan
case "$1" in
    api)
        echo "Starting API server..."
        # Ganti main:app dengan nama file dan instance FastAPI Anda
        exec python main.py
        ;;
    worker)
        echo "Starting RabbitMQ worker..."
        # Hapus argumen pertama ('worker') dan jalankan sisanya
        shift
        # Jalankan consumer sebagai modul dengan sisa argumennya
        exec python -m baseapp.services.consumer "$@"
        ;;
    *)
        # Jalankan perintah apa pun yang diberikan
        exec "$@"
        ;;
esac