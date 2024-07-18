# Dockerfile describing the image to run the tool in
FROM alpine:latest

WORKDIR /
RUN apk add go
RUN go install github.com/ropnop/kerbrute@latest
WORKDIR /root/go/bin/
# Copy the entrypoint script into the container
COPY entrypoint.sh entrypoint.sh
RUN chmod +x ./entrypoint.sh

# Set the entrypoint to the script
ENTRYPOINT ["./entrypoint.sh"]