
#!/bin/bash

# NOTE: This is not an automated script.
# Rather, it's a sequence of commands that can be executed by user to set up a server.
# They will occasionally require provide prompts for input.

# initial server setup

sudo apt-get update
sudo apt-get -y upgrade

USR="bu"
adduser $USR
usermod -aG sudo $USR
# To automate above, need to allow $USR to run sudo without typing password
# refer to this: https://askubuntu.com/questions/192050/how-to-run-sudo-command-with-no-password

su - $USR
mkdir ~/.ssh
chmod 700 ~/.ssh  # set the permissions to only this user into it
vim ~/.ssh/authorized_keys
# step 1 – vim and paste in your public key.
# step 2 – paste in the public key of the app server.
# automate the above.

chmod 600 ~/.ssh/authorized_keys  # set the permissions so only this user is allowed to access it
# check that you can ssh into server with $USR account

sudo sed -i -e "s/PermitRootLogin yes/PermitRootLogin no/" /etc/ssh/sshd_config
sudo sed -i -e "s/PasswordAuthentication yes/PasswordAuthentication no/" /etc/ssh/sshd_config
sudo service ssh restart

# enable firewall
sudo ufw app list  # to view list of available applications
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status

#-------------------------------------

# install redis
# inspired by: https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-redis-on-ubuntu-16-04

sudo apt-get update
sudo apt-get install build-essential tcl libssl-dev libffi-dev python-dev
cd /tmp
curl -O http://download.redis.io/redis-stable.tar.gz
tar xzvf redis-stable.tar.gz

# install redis
cd redis-stable
make
make test
sudo make install

# configure redis
sudo mkdir /etc/redis
sudo cp /tmp/redis-stable/redis.conf /etc/redis
sudo vim /etc/redis/redis.conf
# change 'supervised no' to 'supervised systemd'
# change 'dir ./' to '/var/lib/redis'

# create a Redis systemd unit file
sudo vim /etc/systemd/system/redis.service
#---- add the following ----
[Unit]
Description=Redis In-Memory Data Store
After=network.target

[Service]
User=redis
Group=redis
ExecStart=/usr/local/bin/redis-server /etc/redis/redis.conf
ExecStop=/usr/local/bin/redis-cli shutdown
Restart=always

[Install]
WantedBy=multi-user.target
#-------------------------

# create the redis user, group, and directories
sudo adduser --system --group --no-create-home redis
sudo mkdir /var/lib/redis
sudo chown redis:redis /var/lib/redis
sudo chmod 770 /var/lib/redis

# to start redis
sudo systemctl start redis
sudo systemctl status redis

# test the redis connection
redis-cli
ping
set test "It's working!"
get test
exit
sudo systemctl restart redis

# enable Redis to Start at Boot
sudo systemctl enable redis

#-------------------------------------

# install tmux
sudo apt-get install tmux
tmux new -s bu

#-------------------------------------

# install git
sudo apt-get install git

# create ssh key
ssh-keygen -t rsa -b 4096 -C "bu.adoptanode@gmail.com"

# add ssh key to github bu-adoptanode accounbt via gui

# add ssh-key to ssh-agent so you don't have to type password every time.
eval `ssh-agent -s`   # starts ssh-agent
ssh-add ~/.ssh/id_rsa

#-------------------------------------

# setting up the Python app server
sudo apt-get install python-pip python3-pip python3-dev nginx

sudo pip3 install virtualenv
sudo pip install virtualenvwrapper
echo 'export WORKON_HOME=~/Envs' >> ~/.bash_profile
echo 'source /usr/local/bin/virtualenvwrapper.sh' >> ~/.bash_profile

# don't create .pyc files
echo 'export PYTHONDONTWRITEBYTECODE=1' >> ~/.bash_profile

#-------------------------------------

# install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# as postgres user
sudo su - postgres

# createuser
createuser -P -s -E -e -d bu    # is superuser, can create db's, prompts for password, and encrypts password

exit # become bu user again

#-------------------------------------

# setting up the adopt-a-node repo
git clone git@github.com:sinahab/adopt-a-node.git

cd adopt-a-node

mkvirtualenv adopt-a-node
workon adopt-a-node

pip install -r requirements

# setup instance/config.py file
cp instance/config.py.example instance/config.py
# fill in with real values

# setup psql database
createdb adoptanode_production # create the database
export FLASK_APP=run.py
flask db upgrade

# create a systemd unit file for gunicorn
sudo vim /etc/systemd/system/adopt-web.service
# with the following contents:
# ----
[Unit]
Description=Gunicorn instance to serve adopt-a-node
After=network.target

[Service]
User=bu
Group=www-data
WorkingDirectory=/home/bu/adopt-a-node
Environment="PATH=/home/bu/Envs/adopt-a-node/bin"
Environment="FLASK_CONFIG=production"
ExecStart=/home/bu/Envs/adopt-a-node/bin/gunicorn --config /home/bu/adopt-a-node/gunicorn_config.py --bind unix:adopt-a-node.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
# ----

# start the gunicorn service
sudo systemctl start adopt-web
sudo systemctl enable adopt-web
service adopt-web start
#--------------------------------------

# create a systemd unit file for celery (our task queue)
sudo vim /etc/systemd/system/adopt-celery.service
# with the following contents:
# ----
[Unit]
Description=Celery instance to serve adopt-a-node
After=network.target

[Service]
User=bu
Group=www-data
WorkingDirectory=/home/bu/adopt-a-node
Environment="PATH=/home/bu/Envs/adopt-a-node/bin"
Environment="FLASK_CONFIG=production"
ExecStart=/home/bu/Envs/adopt-a-node/bin/celery -A app.tasks worker --loglevel=info &

[Install]
WantedBy=multi-user.target
# ----

# start the celery service
sudo systemctl start adopt-celery
sudo systemctl enable adopt-celery
service adopt-celery start
#--------------------------------------

# create a systemd unit file for celery beat (our task scheduler)
sudo vim /etc/systemd/system/adopt-celery-beat.service
# with the following contents:
# ----
[Unit]
Description=Celery beat to schedule tasks
After=network.target

[Service]
User=bu
Group=www-data
WorkingDirectory=/home/bu/adopt-a-node
Environment="PATH=/home/bu/Envs/adopt-a-node/bin"
Environment="FLASK_CONFIG=production"
ExecStart=/home/bu/Envs/adopt-a-node/bin/celery beat -A app.tasks

[Install]
WantedBy=multi-user.target
# ----

# start the celery service
sudo systemctl start adopt-celery-beat
sudo systemctl enable adopt-celery-beat
service adopt-celery-beat start

#--------------------------------------

# setup nginx
sudo vim /etc/nginx/sites-available/default
# comment out existing config and add the following:
# ----
server {
    listen 80 default_server;
    server_name adoptanode.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/bu/adopt-a-node/adopt-a-node.sock;
    }
}
# ----

sudo nginx -t  # check for syntax errors
sudo systemctl restart nginx

#--------

# Setting up HTTPS with Lets Encrypt
# Inspired by: https://certbot.eff.org/#ubuntuxenial-nginx
sudo apt-get update
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install python-certbot-nginx

sudo certbot --nginx

# schedule 'certbot renew' cronjob to run every day (it'll only actually update when it's within 3 months of expiry)
# schedule in root's crontab (so it has sudo privileges as required by certbot)
sudo su - root
crontab -e
# add the following line:
# 30 2 * * * /usr/bin/certbot renew

#--------

# add swap space
# basically following this structure: https://www.digitalocean.com/community/tutorials/how-to-add-swap-on-ubuntu-14-04

# check current setup
sudo swapon -s
free -m
df -h

# create swap file
sudo fallocate -l 4G /swapfile
ls -lh /swapfile # verify
sudo chmod 600 /swapfile
ls -lh /swapfile # verify
sudo mkswap /swapfile
sudo swapon /swapfile
sudo swapon -s # verify
free -m

# make the swap file permanent
sudo vim /etc/fstab
# add this line to bottom of file:
/swapfile   none    swap    sw    0   0

# upate swap configs
sudo sysctl vm.swappiness=10
sudo sysctl vm.vfs_cache_pressure=50

sudo vim /etc/sysctl.conf
# at the bottom add:
vm.swappiness=10
vm.vfs_cache_pressure = 50

#--------

# do not require sudo for these commands, as this is required for automation in the app
sudo visudo
# then type in:
bu ALL=(ALL) NOPASSWD:ALL
