#!/bin/bash
set -e

if [[ "$RENEWED_LINEAGE" != *"mail.samacohen.com"* ]]; then
  exit 0
fi

cp "$RENEWED_LINEAGE/fullchain.pem" /blkstg/mailcow-dockerized/data/assets/ssl/cert.pem
cp "$RENEWED_LINEAGE/privkey.pem" /blkstg/mailcow-dockerized/data/assets/ssl/key.pem
chown sam:sam /blkstg/mailcow-dockerized/data/assets/ssl/cert.pem /blkstg/mailcow-dockerized/data/assets/ssl/key.pem
chmod 664 /blkstg/mailcow-dockerized/data/assets/ssl/cert.pem /blkstg/mailcow-dockerized/data/assets/ssl/key.pem

cd /blkstg/mailcow-dockerized
docker compose restart postfix-mailcow dovecot-mailcow nginx-mailcow
