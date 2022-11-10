ARG ERIGON_TAG=latest
FROM thorax/erigon:$ERIGON_TAG

ARG UID=1000
ARG GID=1000

# Create a user and necessary directories.
# If ERIGON_TAG=latest there is no user "erigon" yet (because thorax/erigon:latest is built using Dockerfile.release).
# Otherwise, the user "erigon" is already exists (because thorax/erigon:devel is built using Dockerfile)
USER root
RUN adduser -D -u $UID -g $GID erigon || echo "User already exists"
USER erigon
RUN mkdir -p ~/.local/share/erigon
