Role Name
=========

mailcow

Requirements
------------

Docker and docker compose must already be installed (see `docker_setup.yml`). Assumes `/blkstg` is a mounted, writable data volume so mailcow's data lives on the disk covered by `backup.yml`.

Runs mailcow-dockerized with its own nginx/ACME disabled (`SKIP_LETS_ENCRYPT=y`, bound to `127.0.0.1:8290`), intended to sit behind the host nginx + certbot setup used for every other service. Outbound mail is routed through Mailgun via a Postfix `relayhost` override in `data/conf/postfix/extra.cf`.

Role Variables
--------------

* `mailcow_hostname`: FQDN of the mail server itself (e.g. `mail.samacohen.com`), used as `MAILCOW_HOSTNAME`
* `mailgun_smtp_user`: SMTP username from Mailgun, used as the Postfix relay auth user
* `mailgun_smtp_password`: SMTP password from Mailgun, used as the Postfix relay auth password

Example Playbook
----------------

```yaml
- hosts: production
  vars:
    mailcow_hostname: mail.samacohen.com
  roles:
    - role: mailcow
```

License
-------

MIT
