# zabbix-simple

This is meant to be a quick and simple setup of [zabbix](https://zabbix.com) v5.0 that can be used for testing purposes.

It's assumed that you run it on a Ubuntu 20.10 or CentOS 8 server.

## Containers

### Prerequirements

We're going to use [podman](https://podman.io/getting-started/).

#### Ubuntu

```
sudo apt install -y python3-pip podman
# Depending on the package you might be missing a dependency. Install runc
sudo apt install runc
pip3 install --user pyzabbix
```

#### CentOS
```
sudo dnf install -y podman
pip3 install --user pyzabbix
```

### Create zabbix/create pod

Change the password to something else. The password is used for the database.

```
ZABBIX_PASSWORD=something envsubst < container/zabbix.yaml.tmpl > container/zabbix.yaml
podman play kube container/zabbix.yaml
```

Run post-init. This will change the default password in Zabbix.

```
python3 post-init.py http://localhost:8080 Admin --password zabbix --new-password something-secret
```

### Connect

http://localhost:8080 (you could use a Nginx proxy in front of this).

There are three enabled users:

* Admin: "Zabbix Super Admin". Password is the one set above
* User: "Zabbix Admin". Password is the one set above
* Guest: "Zabbix User". The normal guest user without password

## Ansible

You probably want to use containers instead. Use this if you really want to use ansible.

### Prerequirements

Install pip and ansible.

#### Ubuntu

```
sudo apt install -y python3-pip ansible
```

#### CentOS
```
sudo dnf install -y epel-release && sudo dnf install -y ansible
```

### Install zabbix

Run the ansible playbook to install zabbix. Change the password to something else. The password is used for the database.

Add the `-K` parameter if you need to provide sudo password.

```
cd ansible
ansible-playbook playbook.yml -e password=something
```

Run post-init. This will change the default password in Zabbix.

```
pip3 install --user pyzabbix
python3 post-init.py http://localhost/zabbix Admin --password zabbix --new-password something-secret
```

### Connect

http://localhost/zabbix

There are three enabled users:

* Admin: "Zabbix Super Admin". Password is the one set above
* User: "Zabbix Admin". Password is the one set above
* Guest: "Zabbix User". The normal guest user without password

### Quick flush of zabbix application

Drop the database and run the ansible playbook once more.

```
echo "DROP DATABASE zabbix;" | sudo mysql
```
