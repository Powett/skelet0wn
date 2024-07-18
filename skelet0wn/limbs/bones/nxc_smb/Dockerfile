# Dockerfile describing the image to run the tool in
FROM rust:1.67

# Set environment variables
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PIP_NO_CACHE_DIR=off \
    PATH=/root/.local/bin:$PATH

# Set the working directory
WORKDIR /

# Install dependencies and NetExec in a single RUN command
RUN apt-get update && \
    apt-get install -y python3 python3-dev python3-pip python3-venv curl git && \
    pip install pipx && \
    pipx ensurepath && \
    pipx install git+https://github.com/Pennyw0rth/NetExec && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the entrypoint script into the container
COPY entrypoint.sh entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entrypoint to the script
ENTRYPOINT ["/entrypoint.sh"]
