#!/bin/bash
set -e
set -o pipefail
# Inspired by https://blogs.oracle.com/developers/post/backing-up-your-always-free-vms-in-the-oracle-cloud
TMP_BACKUP_NAME=$(date +%Y-%m-%d_%H-%M-%S)

echo "Running at ${TMP_BACKUP_NAME}."

BLOCK_VOLUMES=$(/home/sam/bin/oci bv volume list --lifecycle-state AVAILABLE)
BLOCK_VOLUMES_COUNT=$(echo "${BLOCK_VOLUMES}" | jq '.data | length')
if [ $BLOCK_VOLUMES_COUNT != 1 ]; then
    echo "Expected exactly one block volume. Given ${BLOCK_VOLUMES_COUNT}"
    exit 1
fi
BLOCK_VOLUME_ID=$(echo "${BLOCK_VOLUMES}" | jq -r '.data[0].id')

echo "Creating new backup..."
NEW_BACKUP_VOLUME_ID=$(/home/sam/bin/oci bv backup create --volume-id ${BLOCK_VOLUME_ID} --type FULL --display-name ${TMP_BACKUP_NAME} --wait-for-state AVAILABLE --query "data.id" | tr -d '"')
echo "New backup volume id: $NEW_BACKUP_VOLUME_ID"

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

echo "Backup process complete! Will mount backup and transfer to BackBlaze"

NEW_VOLUME_ID=$(/home/sam/bin/oci bv volume create --volume-backup-id "$NEW_BACKUP_VOLUME_ID" --availability-domain "qyou:US-ASHBURN-AD-3" --wait-for-state AVAILABLE --query "data.id" | tr -d '"')

NUM_INSTANCES=$(/home/sam/bin/oci compute instance list | jq '.data | length')
if [ $NUM_INSTANCES -ne 1 ]; then
    echo "Cannot find this instance. Expected 1, given $NUM_INSTANCES"
    exit 3
fi
THIS_INSTANCE=$(/home/sam/bin/oci compute instance list | jq -r '.data[0].id')

NEW_VOLUME_ATTACHMENT_DATA=$(/home/sam/bin/oci compute volume-attachment attach-iscsi-volume  --instance-id "$THIS_INSTANCE" --volume-id "$NEW_VOLUME_ID" --is-agent-auto-iscsi-login-enabled true --wait-for-state ATTACHED)
NEW_VOLUME_ATTACHMENT_IQN=$(echo $NEW_VOLUME_ATTACHMENT_DATA  | jq -r '.data.iqn')
# TODO: Can you force the OS to refresh this?
while ! sudo ls /dev/disk/by-path/*${NEW_VOLUME_ATTACHMENT_IQN}* > /dev/null; do
    echo "Disk still not attached. Waiting...";
    sleep 5
done

echo "Disk attached for $NEW_VOLUME_ATTACHMENT_IQN"

sudo mkdir -p /blkstgbak
sudo mount -t auto /dev/disk/by-path/*${NEW_VOLUME_ATTACHMENT_IQN}* /blkstgbak

echo "Copying via rclone..."
sudo rclone copy --fast-list --no-check-dest --ignore-size --transfers 24 --b2-chunk-size 256M /blkstgbak backblaze_oci_backup:oci-backup/${TMP_BACKUP_NAME} -v
echo "Done copying"

sudo umount /dev/disk/by-path/*${NEW_VOLUME_ATTACHMENT_IQN}*

NEW_VOLUME_ATTACHMENT_ID=$(echo $NEW_VOLUME_ATTACHMENT_DATA | jq -r '.data.id')
/home/sam/bin/oci compute volume-attachment detach --volume-attachment-id $NEW_VOLUME_ATTACHMENT_ID --wait-for-state DETACHED --force
/home/sam/bin/oci bv volume delete --volume-id $NEW_VOLUME_ID --wait-for-state TERMINATED --force

echo "Done with backup"
