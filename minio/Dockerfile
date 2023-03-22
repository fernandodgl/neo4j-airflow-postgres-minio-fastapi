FROM minio/minio:latest


COPY setup.sh /setup.sh
RUN chmod +x /setup.sh

RUN curl https://dl.min.io/client/mc/release/linux-amd64/mc -o /usr/local/bin/mc && \
chmod +x /usr/local/bin/mc

ENTRYPOINT ["/setup.sh"]

# CMD [bin/bash -c "/usr/bin/minio server /data"]

