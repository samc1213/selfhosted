# Usage
1. Create a hosts file in `inventory/hosts`. It should look like:

```
[production]
<some ip or FQDN>
```
2. Install docker: `ansible-galaxy collection install community.docker`


To run commands, use `ansible-playbook -e @secrets_file.enc --ask-vault-pass -i inventory/hosts <playbook_name>.yml`


```mermaid
graph
    compute[OCI Compute Instance]
    bv[OCI Block Volume]
    bb[BackBlaze B2 Object Storage]
    pc[Laptop]
    pc --> |ssh| compute
    subgraph Oracle Cloud
        bv <--> |data storage| compute
    end
        compute --> |backups| bb
```

## Secrets
To add a new secret, run `ansible-vault edit secrets_file.enc`.

## Dependencies

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install --include-deps ansible --force
ansible-galaxy collection install community.docker
```

## Backup Failures
If backup-oci-block fails due to an OCI issue or other issue, there may be an extra block volume lying around. To find it, run 

```bash
/home/sam/bin/oci bv volume list --lifecycle-state AVAILABLE
```

Find the temporary one (look at `time-created`, it's probably recent), and delete:

```bash
/home/sam/bin/oci bv volume delete --volume-id <volume-ocid> --force
```
