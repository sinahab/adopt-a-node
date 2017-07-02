
#!/bin/bash

# NOTE: This is not an automated script.
# Rather, it's a sequence of commands that can be executed by user to set up a server.
# They will occasionally require provide prompts for input.

sudo apt-get update
sudo apt-get -y -f upgrade

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

#--------------------------------------

# do not require sudo for poweroff, as this is required for automation in the app
sudo visudo
# then type in:
bu ALL = NOPASSWD: /sbin/poweroff

#--------------------------------------

sudo apt-get install tmux
tmux new -s bu

#--------------------------------------

# scp BU_auto_node.sh to the server
scp BU_auto_node.sh bu@remotehost.edu:/home/bu/

# run in tmux
chmod 744 BU_auto_node.sh
sudo ./BU_auto_node.sh

# sudo su testme -c '/usr/local/bin/bitcoind -datadir=/home/testme/.bitcoin -daemon'

#-------------------------------------

# add these to the bottom of .bitcoin/bitcoin.conf
# the app replaces them with the user-chosen values.
excessiveblocksize=16000000
excessiveacceptdepth=12
net.subversionOverride=/BitcoinUnlimited:v1.0.2.0(EB16; AD12) template/
