# LDAP Authentication Backend

The `ldap` provider MUST be activated in webserver.

## Open configuration form

Click on the *LDAP* menu entry:

![image](../../img/ldap/menu.png)

This will open the following form:

![image](../../img/ldap/form0.png)

Detailed form:

- **Default role:** default role used for user when he logs in for the first time.

----

![image](../../img/ldap/form1.png)

Detailed form:

- **Host:** LDAP server host ;
- **Port:** LDAP server port ;
- **Admin DN:** identifier for LDAP admin account ;
- **Admin password:** password for LDAP admin account ;
- **User filter:** LDAP filter for users, a `%s` MUST be present
  (will be replaced with wanted username) ;
- **User DN:** LDAP base directory to look for users.

----

![image](../../img/ldap/form2.png)

Detailed form:

- Map `attribute -> LDAP attribute` ;
- used to fill the Canopsis account with LDAP informations.
