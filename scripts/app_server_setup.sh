
#!/bin/bash

# initial server setup

sudo apt-get update
sudo apt-get -y upgrade

USR="bu"
adduser $USR
# TODO: create user without having to type in password
# could use: adduser --disabled-password --gecos "" $USR
# but there's a problem – how to do sudo later without having a password

usermod -aG sudo $USR
# TODO: to automate next commands, need to allow $USR to run sudo without typing password
# refer to this: https://askubuntu.com/questions/192050/how-to-run-sudo-command-with-no-password

su - $USR
mkdir ~/.ssh
chmod 700 ~/.ssh  # set the permissions to only this user into it
vim ~/.ssh/authorized_keys  #TODO: automate this: vim and paste in my public key.
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
sudo apt-get install build-essential tcl
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
sudo apt-get install python3-pip python3-dev nginx

sudo pip3 install virtualenv
sudo pip3 install virtualenvwrapper
export WORKON_HOME=~/Envs
source /usr/local/bin/virtualenvwrapper.sh

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

# create a systemd unit file
sudo vim /etc/systemd/system/adopt-a-node.service
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
ExecStart=/home/bu/Envs/adopt-a-node/bin/gunicorn --workers 3 --bind unix:adopt-a-node.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
# ----

# start the gunicorn service
sudo systemctl start adopt-a-node
sudo systemctl enable adopt-a-node

# setup nginx
sudo vim /etc/nginx/sites-available/default
# comment out existing config and add the following:
# ----
server {
    listen 80 default_server;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/bu/adopt-a-node/adopt-a-node.sock;
    }
}
# ----

sudo nginx -t  # check for syntax errors
sudo systemctl restart nginx
