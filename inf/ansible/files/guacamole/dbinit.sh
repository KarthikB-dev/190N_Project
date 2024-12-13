#!/bin/bash
cat /initdb.sql | mysql -u root --password=MariaDBRootPass guacamole_db
