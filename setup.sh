#! /bin/bash
set -eux

# Default paths, image name and ports
DOJO_PATH="./dojo"
CONTAINER_DOJO_PATH="/opt/pwn.college:shared"
IMAGE_NAME="pwncollege/dojo"
MAP_HTTP_PORT=18080
MAP_HTTPS_PORT=10443
MAP_SSH_PORT=22222

curl -fsSL https://get.docker.com | /bin/sh
git clone https://github.com/HUSTSeclab/dojo.git "$DOJO_PATH"
docker buildx install
docker build --load -t "$IMAGE_NAME" "$DOJO_PATH"
docker run --privileged -d -v "${DOJO_PATH}:${CONTAINER_DOJO_PATH}" -p "${MAP_SSH_PORT}:22" -p "${MAP_HTTP_PORT}:80" -p "${MAP_HTTPS_PORT}:443" --name dojo "${IMAGE_NAME}"

# Default variables
YOUR_HTTP_PORT="80" 
# HTTPS_PORT="443"
# CERT_FILE="/path/to/your.cert.pem"
# CERT_KEY="/path/to/your.key.pem"
# DOMAIN="yourdomain.com"
IP="192.168.1.1" 
CONFIG_FILE="${IP}.conf"
# Creating Configuration Files
cat > “$CONFIG_FILE” <<EOF
server {
    listen $YOUR_HTTP_PORT;
    listen [::]:$YOUR_HTTP_PORT;

    #listen $HTTPS_PORT ssl;
    #listen [::]:$HTTPS_PORT ssl;
    #ssl_certificate $CERT_FILE;
    #ssl_certificate_key $CERT_KEY;

    #server_name $DOMAIN;
    location / {
        proxy_http_version 1.1;
        proxy_set_header Host $IP:$MAP_HTTP_PORT;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Accept-Encoding gzip;
        proxy_set_header Origin "http://$IP:$MAP_HTTP_PORT";
        proxy_buffering off;

        proxy_pass http://127.0.0.1:$MAP_HTTP_PORT;
    }
}
EOF
