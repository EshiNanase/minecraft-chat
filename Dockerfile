FROM ubuntu
RUN apt-get update && \
    apt-get install -y netcat

CMD ["nc", "minechat.dvmn.org", "5000"]
