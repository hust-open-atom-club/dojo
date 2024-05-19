#! /bin/bash
set -eux

# Default image name and ports
IMAGE_NAME="pwnhustcollege/dojo"
MAP_HTTP_PORT=8880
MAP_HTTPS_PORT=44443
MAP_SSH_PORT=22222

curl -fsSL https://get.docker.com | /bin/sh
git clone https://github.com/hust-open-atom-club/dojo
docker build  -t "$IMAGE_NAME" dojo
docker run --privileged -d -v "dojo:/opt/pwn.college:shared" -p "${MAP_SSH_PORT}:22" -p "${MAP_HTTP_PORT}:80" -p "${MAP_HTTPS_PORT}:443" --name dojo "${IMAGE_NAME}"