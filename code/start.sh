#!/bin/bash
# Build the image and (re)start the e-sight container with camera and LED access.
# See docker-compose.yml for the device mappings.

set -e
cd "$(dirname "$0")"

docker compose up -d --build
docker compose logs -f
