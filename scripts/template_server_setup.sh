
#!/bin/bash

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

sudo apt-get install tmux
tmux new -s bu

#--------------------------------------

# scp BU_auto_node.sh to the server
scp BU_auto_node.sh bu@remotehost.edu:/home/bu/

# run in tmux
chmod 744 BU_auto_node.sh
sudo ./BU_auto_node.sh

# sudo su testme -c '/usr/local/bin/bitcoind -datadir=/home/testme/.bitcoin -daemon'

#---------------------------------

# ONLY IF you need to mount a volume

# format the volume with ext4
sudo mkfs.ext4 -F /dev/disk/by-id/scsi-0DO_Volume_volume-sfo2-01

# create mount point under /mnt
sudo mkdir -p /mnt/volume-sfo2-01

# mount the volume
sudo mount -o discard,defaults /dev/disk/by-id/scsi-0DO_Volume_volume-sfo2-01 /mnt/volume-sfo2-01;

# change fstab so volume will be mounted after a reboot
echo /dev/disk/by-id/scsi-0DO_Volume_volume-sfo2-01 /mnt/volume-sfo2-01 ext4 defaults,nofail,discard 0 0 | sudo tee -a /etc/fstab

# TODO: don't know if this is secure, but needed to be able to write files / dirs.
sudo chmod 747 /mnt/volume-sfo2-01/
mkdir /mnt/volume-sfo2-01/.bitcoin
