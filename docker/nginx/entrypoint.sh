SSL_DIR="/etc/nginx/ssl"
SSL_KEY="${SSL_DIR}/nginx.key"
SSL_CRT="${SSL_DIR}/nginx.crt"

# Create directory if it doesn't exist
mkdir -p "${SSL_DIR}"

# Check if certificates exist, if not generate them
if [ ! -f "${SSL_KEY}" ] || [ ! -f "${SSL_CRT}" ]; then
    echo "SSL Certificate not found. Generating a self-signed certificate..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "${SSL_KEY}" \
        -out "${SSL_CRT}" \
        -subj "/C=BR/ST=Santa Catarina/L=Itajai/O=narada/OU=Dev/CN=localhost"
    echo "Self-signed certificate generated."
else
    echo "Existing SSL Certificate found. Skipping generation."
fi

# Execute Nginx CMD
exec "$@"
