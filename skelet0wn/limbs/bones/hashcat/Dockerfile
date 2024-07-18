# Dockerfile describing the image to run the tool in
FROM kalilinux/kali-rolling:latest

WORKDIR /

# Install dependencies
RUN apt -y update && DEBIAN_FRONTEND=noninteractive apt -y dist-upgrade && apt -y autoremove && apt clean
RUN apt install -y wordlists hashcat
RUN cd /usr/share/wordlists; gunzip rockyou.txt.gz

# Copy the entrypoint script into the container
COPY entrypoint.sh entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entrypoint to the script
ENTRYPOINT ["/entrypoint.sh"]