#!/usr/bin/python3
import argparse
import getpass
import time

import pyzabbix

def delete_stuff():
    for script in zapi.script.get():
        print("Deleting script: {} ({})".format(script["name"], script["scriptid"]))
        zapi.script.delete(script["scriptid"])
    
    for mediatype in zapi.mediatype.get():
        print("Deleting mediatype: {} ({})".format(mediatype["description"], mediatype["mediatypeid"]))
        zapi.mediatype.delete(mediatype["mediatypeid"])
    
    for host in zapi.host.get():
        print("Deleting host: {} ({})".format(host["host"], host["hostid"]))
        zapi.host.delete(host["hostid"])
    
    for template in zapi.template.get():
        print("Deleting template: {} ({})".format(template["host"], template["templateid"]))
        zapi.template.delete(template["templateid"])
    
    for hostgroup in zapi.hostgroup.get():
        print("Deleting hostgroup: {} ({})".format(hostgroup["name"], hostgroup["groupid"]))
        try:
            zapi.hostgroup.delete(hostgroup["groupid"])
        except pyzabbix.ZabbixAPIException as e:
            # Some hostgroups are internal and can't be deleted
            print("ERROR", str(e))
    
    for action in zapi.action.get():
        print("Deleting action: {} ({})".format(action["name"], action["actionid"]))
        zapi.action.delete(action["actionid"])
    
    for drule in zapi.drule.get():
        print("Deleting drule: {} ({})".format(drule["name"], drule["druleid"]))
        zapi.drule.delete(drule["druleid"])
    
    for user in zapi.user.get():
        print("Deleting user: {} ({})".format(user["alias"], user["userid"]))
        try:
            zapi.user.delete(user["userid"])
        except pyzabbix.ZabbixAPIException as e:
            # Can't delete self or internal users
            print("ERROR", str(e))
    
    for usergroup in zapi.usergroup.get():
        print("Deleting usergroup: {} ({})".format(usergroup["name"], usergroup["usrgrpid"]))
        try:
            zapi.usergroup.delete(usergroup["usrgrpid"])
        except pyzabbix.ZabbixAPIException as e:
            # Can't delete internal usergroups or only/last usergroup of user
            print("ERROR", str(e))

def create_stuff(version, new_password):
    groupid = zapi.hostgroup.create(name="Hostgroup")["groupids"][0]
    zapi.host.create(host="Host", groups=[{"groupid": groupid}], interfaces=[{"type": 1, "main": 1, "useip": 1, "ip": "127.0.0.1", "dns": "", "port": 10050}])
    usergroupid = zapi.usergroup.create(name="Usergroup", rights=[{"permission": 3, "id": groupid}])["usrgrpids"][0]
    if version >= (5,2,0):
        userid = zapi.user.create(alias="User", passwd=new_password, roleid=2, usrgrps=[{"usrgrpid": usergroupid}])["userids"][0]
    else:
        userid = zapi.user.create(alias="User", passwd=new_password, type=2, usrgrps=[{"usrgrpid": usergroupid}])["userids"][0]
def update_stuff(new_password):
    userid = zapi.user.get(filter={"alias": "Admin"})[0]["userid"]
    zapi.user.update(userid=userid, passwd=new_password)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("username")
    parser.add_argument("--password")
    parser.add_argument("--new-password")
    args = parser.parse_args()

    if args.password is None:
        args.password = getpass.getpass("Current password: ")
    if args.new_password is None:
        args.new_password = getpass.getpass("New password: ")

    zapi = pyzabbix.ZabbixAPI(args.url)
    zapi.login(args.username, args.password)
    version_string = zapi.api_version()
    version = tuple(map(int, version_string.split(".")))
    print("Connected to Zabbix API Version {}".format(version_string))

    delete_stuff()
    create_stuff(version, args.new_password)
    update_stuff(args.new_password)
