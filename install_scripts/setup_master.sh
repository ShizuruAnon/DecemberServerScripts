#!/bin/bash

SERVER_UNAME = 'bkt'

# cd to file dir
cd "$(dirname "$0")"

# install stuff
sudo apt install wget vim rsync ssh git python3 python3-pip cron -y
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Copy the ssh key over
SSH_PUB_KEY = "/home/${SERVER_UNAME}/.ssh/id_rsa.pub"
if [ -f "~/.ssh/id_rsa.pub"]; then
    echo "Using the public key in `${SSH_PUB_KEY}`"
else
    echo "Public key for ssh not found in `${SSH_PUB_KEY}`. Generating new public ssh key. Use the default path."
    ssh-keygen
echo "IMPORTANT: COPY THE PUBLIC KEY TO ALL SERVERS FOR USER `${SERVER_UNAME}`. PUBLIC KEY IS"
cat  ${SSH_PUB_KEY}

# copy the config
sudo su ${SERVER_UNAME}
mkdir -p ~/config
cp example_server_config.json ~/config/server_config.json

# crontab -e
# ```
# */20 0-2 * * *  python3 /home/bkt/update_links.py >> /home/bkt/logs/cronlog.txt 2>&1
# */5 2-12 * * *  python3 /home/bkt/update_links.py >> /home/bkt/logs/cronlog.txt 2>&1
# * 12    * * *   python3 /home/bkt/randomize_links.py >> /home/bkt/logs/cronlog.txt 2>&1
# 20,40 12 * * *  python3 /home/bkt/update_links.py >> /home/bkt/logs/cronlog.txt 2>&1
# */20 12-23 * * * python3 /home/bkt/ >> /home/bkt/logs/cronlog.txt 2>&1
# ```