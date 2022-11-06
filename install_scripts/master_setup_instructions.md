## Step 0: make sure there is a user `bkt` on all servers and that you can install packages as root

## Step 1: install stuff
sudo apt install wget vim rsync ssh git python3 python3-pip cron -y
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

## Step 2: Fix ssh keys. Generate one or have one on the master server. Then add master ssh pub key into `/home/bkt/.ssh/authroized_keys` on all slave servers

## Step 3: download this git repo into the bkt home dir
You should then have `/home/bkt/DecemberServerScripts`

# Step 4: copy the config
mkdir -p ~/config
cp example_server_config.json ~/config/server_config.json

# Step 5: make sure bkt user owns all of this
`chown -R bkt:bkt /home/bkt/DecemberServerScripts`
`chown -R bkt:bkt /home/bkt/config`

# Step 6: edit crontab with `crontab -e` and add this at the bottom of the file

```
*/20 0-2 * * *  python3 /home/bkt/DecemberServerScripts/python_scripts/update_links.py >> /home/bkt/logs/cronlog.txt 2>&1
*/5 2-12 * * *  python3 /home/bkt/DecemberServerScripts/python_scripts/update_links.py >> /home/bkt/logs/cronlog.txt 2>&1
* 12    * * *   python3 /home/bkt/DecemberServerScripts/python_scripts/randomize_links.py >> /home/bkt/logs/cronlog.txt 2>&1
20,40 12 * * *  python3 /home/bkt/DecemberServerScripts/python_scripts/update_links.py >> /home/bkt/logs/cronlog.txt 2>&1
*/20 12-23 * * * python3 /home/bkt/DecemberServerScripts/python_scripts/update_links.py >> /home/bkt/logs/cronlog.txt 2>&1
```

# Step 7: add the `google_api_credentials.json` to `~/config`. You will have to figure out how to get that

# Step 8: edit the `~/config/server_config.json` file if needed. If you add a server you will need to add it to the `"slave-server-urls'` array in the file