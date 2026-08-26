#!/bin/bash
# Production deploy, executed on the EC2 host as root.
#
# The workflow (.github/workflows/deploy.yml) syncs the checkout to origin/main
# and then runs a *copy* of this file from /tmp — a script must not run from a
# path that `git reset --hard` is rewriting underneath it, because bash reads
# scripts lazily and would execute the tail of the new file.
#
# Manual rollback to any previously built image:
#   sudo /home/ubuntu/AndresAI-Agent/scripts/deploy.sh <account>.dkr.ecr.us-east-1.amazonaws.com/andres-ai-api:sha-1a2b3c4
set -euo pipefail

ECR_IMAGE="${1:?usage: deploy.sh <full-ecr-image-uri>}"
export ECR_IMAGE

APP_DIR=/home/ubuntu/AndresAI-Agent
AWS_REGION=us-east-1
REGISTRY="${ECR_IMAGE%%/*}" # registry host is everything before the first slash

cd "$APP_DIR"

# ECR authorization tokens expire after 12h, so log in on every deploy rather
# than relying on a login done once at provisioning time.
aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$REGISTRY"

docker pull "$ECR_IMAGE"

COMPOSE="docker compose -f docker-compose.prod.yml"

# Bring dependencies to the current config and wait for the db healthcheck
# before migrating. Without this, `compose run` evaluates backend's
# service_healthy condition against a db container that may predate the
# healthcheck being declared, and stalls.
$COMPOSE up -d --wait db redis

# Migrate using the new image before it serves traffic. `set -e` means a failed
# migration aborts the deploy here, leaving the previous container running.
$COMPOSE run --rm backend uv run alembic upgrade head

$COMPOSE up -d --remove-orphans

# Record what is actually running, and keep the root volume from filling up.
# `prune -f` alone only drops dangling layers; each deploy also leaves a
# sha-tagged image behind. Images backing a running container are never removed.
echo "$ECR_IMAGE" > .deployed-image
docker image prune -af --filter "until=168h" >/dev/null

echo "--- deployed: $ECR_IMAGE"
$COMPOSE ps
