## Step 0: make sure there is a user `bkt` on all servers and that you can install packages as root

## Step 1: install stuff
sudo apt install wget vim rsync ssh git python3 python3-pip cron -y

# AS BKT USER
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

## Step 2: add master's ssh pub key into slave `/home/bkt/.ssh/authorized_keys`

## Step 3: download this git repo into the bkt home dir
You should then have `/home/bkt/DecemberServerScripts`

# Step 4: make sure bkt user owns all of this
`chown -R bkt:bkt /home/bkt/DecemberServerScripts`
`chown -R bkt:bkt /home/bkt/config`

# Step 5: edit crontab AS BKT USER with `crontab -e` and add this at the bottom of the file
```
*/1 * * * * python3 /home/bkt/DecemberServerScripts/python_scripts/fix_links.py >> /home/bkt/logs/cronlog.txt 2>&1
```

# Step 6: you MUST do this
mkdir /home/bkt/logs