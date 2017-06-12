#!/usr/bin/env bash

# Create virtualenv
if [ $(dpkg-query -W -f='${Status}' virtualenv 2>/dev/null | grep -c "ok installed") -eq 0 ];
then
  apt-get install virtualenv;
fi
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt

# Copy and start systemd service
sudo cp pi-lcd-weather.service /etc/systemd/system/pi-lcd-weather.service
sudo sed -i 's,pi-lcd-weather-location,$(pwd),g' /etc/systemd/system/pi-lcd-weather.service
sudo systemctl daemon-reload
sudo systemctl enable pi-lcd-weather.service
sudo systemctl start pi-lcd-weather.service
