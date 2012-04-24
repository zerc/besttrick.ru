#!/bin/bash
echo '>> Starting ...'
. venv/bin/activate
mongod -f /etc/mongodb.conf &
