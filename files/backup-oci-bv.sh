#!/bin/bash
set -e
# Inspired by https://blogs.oracle.com/developers/post/backing-up-your-always-free-vms-in-the-oracle-cloud

PROFILE_NAME=DEFAULT
TMP_BACKUP_NAME=$(date +%Y-%m-%d_%H-%M-%S)

echo "Running at ${TMP_BACKUP_NAME}."
echo "Getting previous backup..."

BLOCK_VOLUMES=$(/home/sam/bin/oci bv volume list)
BLOCK_VOLUMES_COUNT=$(echo "${BLOCK_VOLUMES}" | jq '.data | length')
if [ $BLOCK_VOLUMES_COUNT != 1 ]; then
    echo "Expected exactly one block volume. Given ${BLOCK_VOLUMES_COUNT}"
    exit 1
fi
BLOCK_VOLUME_ID=$(echo "${BLOCK_VOLUMES}" | jq -r '.data[0].id')

echo "Creating new backup..."
NEW_BACKUP_ID=$(/home/sam/bin/oci bv backup create --volume-id ${BLOCK_VOLUME_ID} --type FULL --display-name ${TMP_BACKUP_NAME} --wait-for-state AVAILABLE --query "data.id")

if [ -z "$NEW_BACKUP_ID" ]; then
    echo "New backup creation failed...Exiting script!"
    exit 2
else
    echo "New backup id: $NEW_BACKUP_ID"
fi

NUM_BACKUPS=$(/home/sam/bin/oci bv backup list --lifecycle-state AVAILABLE | jq '.data | length')
if [ -z "$NUM_BACKUPS" ]; then
    NUM_BACKUPS="0"
fi

if [ $NUM_BACKUPS -lt 5 ]; then
    echo "Don't need to delete old backup. Only $NUM_BACKUPS exist."
else
    echo "Deleting old backup..."
    OLDEST_BACKUP_ID=$(/home/sam/bin/oci bv backup list --lifecycle-state AVAILABLE | jq --arg block_volume_id ${BLOCK_VOLUME_ID} -r '[ .data[] | select(."volume-id" == $block_volume_id) ] | sort_by(."time-created") | .[0].id')
    /home/sam/bin/oci bv backup delete --force --volume-backup-id ${OLDEST_BACKUP_ID} --wait-for-state TERMINATED
fi

echo "Backup process complete! Goodbye!"
