#! /bin/bash
set -eux

# Default image name and ports
IMAGE_NAME="pwnhustcollege/dojo"

echo "Checking if docker is installed on the system"
if command -v docker &> /dev/null
then
    echo "Docker is installed"
else
    curl -fsSL https://get.docker.com | /bin/sh
fi

docker build  -t "$IMAGE_NAME" dojo
docker run --privileged -d -v "dojo:/opt/pwn.college:shared" -p "22:22" -p "80:80" -p "443:443" --name dojo "${IMAGE_NAME}"
