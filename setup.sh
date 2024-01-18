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