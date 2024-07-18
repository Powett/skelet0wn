# Template Dockerfile provided to ease integration of new skelet0wn tools
FROM alpine:latest

WORKDIR /

# Install dependencies

# Copy the entrypoint script into the container
COPY entrypoint.sh entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entrypoint to the script
ENTRYPOINT ["/entrypoint.sh"]