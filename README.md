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