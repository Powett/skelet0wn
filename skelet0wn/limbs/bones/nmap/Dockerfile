FROM alpine:latest

WORKDIR /

# Install nmap
RUN apk add nmap nmap-scripts

# Copy the entrypoint script into the container
COPY entrypoint.sh entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entrypoint to the script
ENTRYPOINT ["./entrypoint.sh"]