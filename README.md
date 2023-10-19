# Usage
1. Create a hosts file in `inventory/hosts`. It should look like:

```
[production]
<some ip or FQDN>
```
2. To run commands, use `ansible-playbook -e @secrets_file.enc --ask-vault-pass -i inventory/hosts <playbook_name>`
