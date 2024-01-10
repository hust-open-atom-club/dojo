#! /bin/bash
set -eux

# Do not edit this port!!!
HTTP_PORT=80
HTTPS_PORT=443
SSH_PORT=22
# Feel free to modify the following MAP_XXX_PORT
MAP_HTTP_PORT=8080
MAP_HTTPS_PORT=10443
MAP_SSH_PORT=22222
# Default paths and image name
DOJO_PATH="./dojo"
CONTAINER_DOJO_PATH="/opt/pwn.college:shared"
IMAGE_NAME="pwncollege/dojo"

curl -fsSL https://get.docker.com | /bin/sh
git clone https://github.com/HUSTSeclab/dojo.git "$DOJO_PATH"
docker build -t "$IMAGE_NAME" "$DOJO_PATH"
docker run --privileged -d -v "${DOJO_PATH}:${CONTAINER_DOJO_PATH}" -p "${MAP_SSH_PORT}:${SSH_PORT}" -p "${MAP_HTTP_PORT}:${HTTP_PORT}" -p "${MAP_HTTPS_PORT}:${HTTPS_PORT}" --name dojo "${IMAGE_NAME}"
