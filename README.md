# zabbix-simple

This is meant to be a quick and simple setup of [zabbix](https://zabbix.com) v4.2 that can be used for testing purposes.

It's assumed that you run it on a Ubuntu 18.04 LTS server.

## Prerequirements

Install pip and ansible.

```
sudo apt install python3-pip && sudo pip3 install ansible
```

## Install zabbix

Run the ansible playbook to install zabbix. Change the password to something else. The password is used for the database and zabbix users.

Add the `-K` parameter if you need to provide sudo password.

```
ansible-playbook playbook.yml -e password=something
```

## Connect

http://localhost/zabbix

There are three enabled users:

* Admin: "Zabbix Super Admin". Password is the one set above
* User: "Zabbix Admin". Password is the one set above
* Guest: "Zabbix User". The normal guest user without password

## Quick flush of zabbix application

Drop the database and run the ansible playbook once more.

```
echo "DROP DATABASE zabbix;" | sudo mysql
```
