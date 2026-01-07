#!/bin/bash

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."

while ! python -c "
import socket
import os
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex((os.environ.get('DB_HOST', 'db'), int(os.environ.get('DB_PORT', 5432))))
sock.close()
exit(result)
" 2>/dev/null; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done

echo "PostgreSQL is up - continuing..."

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Start server
echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000
