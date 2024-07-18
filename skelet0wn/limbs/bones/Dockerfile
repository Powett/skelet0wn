FROM kalilinux/kali-rolling

WORKDIR /root

# Update
RUN apt-get update && apt -y update && DEBIAN_FRONTEND=noninteractive apt -y dist-upgrade && apt -y autoremove && apt clean