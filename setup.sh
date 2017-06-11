#!/usr/bin/env bash

# Create virtualenv
if [ $(dpkg-query -W -f='${Status}' virtualenv 2>/dev/null | grep -c "ok installed") -eq 0 ];
then
  apt-get install virtualenv;
fi
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt

# Copy systemd init file


# Start service

