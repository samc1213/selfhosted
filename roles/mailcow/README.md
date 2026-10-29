Role Name
=========

mailcow

Requirements
------------

Docker and docker compose must already be installed (see `docker_setup.yml`). Assumes `/blkstg` is a mounted, writable data volume so mailcow's data lives on the disk covered by `backup.yml`.

Runs mailcow-dockerized with its own nginx/ACME disabled (`SKIP_LETS_ENCRYPT=y`, bound to `127.0.0.1:8290`), intended to sit behind the host nginx + certbot setup used for every other service. Outbound mail is routed through Mailgun via a Postfix `relayhost` override in `data/conf/postfix/extra.cf`.

Role Variables
--------------

* `mailcow_version`: mailcow-dockerized release tag to check out (e.g. `2026-10`). Upgrades happen only when this is bumped; the role does not use mailcow's `update.sh`, which always jumps to the latest release
* `mailcow_hostname`: FQDN of the mail server itself (e.g. `mail.samacohen.com`), used as `MAILCOW_HOSTNAME`
* `mailgun_smtp_user`: SMTP username from Mailgun, used as the Postfix relay auth user
* `mailgun_smtp_password`: SMTP password from Mailgun, used as the Postfix relay auth password

Example Playbook
----------------

```yaml
- hosts: production
  vars:
    mailcow_hostname: mail.samacohen.com
    mailcow_version: "2026-10"
  roles:
    - role: mailcow
```

License
-------

MIT
