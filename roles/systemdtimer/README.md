Role Name
=========

systemdtimer

Requirements
------------

This role assumes the system already has systemd installed

Role Variables
--------------

* `systemdtimer_servicename`: What to name the service / timer
* `systemdtimer_oncalendar`: The schedule for the systemd timer. E.g.,  `"*-*-* *:*:00"`
* `systemdtimer_command`: What command to run. For example, a bash script


Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

```yaml
  vars:
    samtestdest: /usr/local/bin/samtest.sh
  roles:
    - role: systemdtimer
      vars:
        systemdtimer_servicename: testtimer
        systemdtimer_oncalendar: "*-*-* *:*:00"
        systemdtimer_command: "{{ samtestdest }}"
```

License
-------

MIT
