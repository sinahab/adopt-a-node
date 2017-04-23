#!/bin/bash

USR="testme"

#--------------------------------

sudo apt-get update
sudo apt-get -y upgrade

#--------------------------------

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

sudo sed -i -e "s/PermitRootLogin yes/PermitRootLogin no/" /etc/ssh/sshd_config
sudo sed -i -e "s/PasswordAuthentication yes/PasswordAuthentication no/" /etc/ssh/sshd_config
sudo service ssh restart

#-----------------------------------
