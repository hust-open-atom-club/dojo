#! /bin/bash
curl -fsSL https://get.docker.com | /bin/sh

DOJO_PATH="./dojo"
CONTAINER_DOJO_PATH="/opt/pwn.college:shared"
IMAGE_NAME="pwncollege/dojo"
# Do not edit this port!!!
HTTP_PORT=80
HTTPS_PORT=443
SSH_PORT=22
# You can edit this MAP_XXX to change the corresponding ports on the Docker host
MAP_HTTP_PORT=8080
MAP_HTTPS_PORT=10443
MAP_SSH_PORT=22222
git clone https://github.com/HUSTSeclab/dojo.git "$DOJO_PATH"
docker build -t "$IMAGE_NAME" "$DOJO_PATH"
docker run --privileged -d -v "${DOJO_PATH}:${CONTAINER_DOJO_PATH}" -p ${MAP_SSH_PORT}:${SSH_PORT} -p ${MAP_HTTP_PORT}:${HTTP_PORT} -p ${MAP_HTTPS_PORT}:${HTTPS_PORT} --name dojo ${IMAGE_NAME}