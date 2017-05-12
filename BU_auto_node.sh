#!/bin/bash
#
# v0.0.1
# Installing BU on a new machine, configuring it, make it persistan to reboot
# Tested on Ubuntu 14.04 and 16.04 x86_64
# inspired by https://raw.githubusercontent.com/XertroV/BitcoinAutoNode/master/bitcoinAutoNode.sh
#
# WARN if run by sudo we need to input the password from stdin on disable password prompt for sudoers
#
# -d download instead of compiling
# -n avoid to create swap partition
# -r reboot at the end
# -s enable the sync of the blockchain from trusted source
# -p disable prune mode
#
# TODO
# - add a conf file instead of using all these variables
# - fetch a list of BU node to connect to
# - check if there's enough space to store the blockchain

set -eu

#TODO read these pars from a conf file, ideally the JSON used in release signature.
BU_BRANCH="1.0.1.3bu"
BU_TAG="bu1.0.1.3"
USR="testme"
BU_REPO="https://github.com/BitcoinUnlimited/BitcoinUnlimited.git"
BU_URL64="https://www.bitcoinunlimited.info/downloads/bitcoinUnlimited-1.0.1.3-linux64.tar.gz"
BU_URL32="https://www.bitcoinunlimited.info/downloads/bitcoinUnlimited-1.0.1.3-linux32.tar.gz"
BU_SUM64="864908c88d6b9d08c64e46b12acb5c1f8418b0737dfbeffdb8b1c03907892b02"
BU_SUM32="bb5088b8dfb2be930534f1b174279299eec090542fa62fd04fe05eb9d43f14ba"
BU_HOME="/home/$USR"

SSH_KEY_PATH=$BU_HOME/.ssh/id_rsa
REMOTE_USR=auser
REMOTE_HOST=trusted_host
REMOTE_BLOCKCHAIN_PATH=path_to_the_blockchain


sync_chain() {
  echo "Start syncing the chain ..."

  sudo -u $USR bash <<-EOH
  rsync --progress -a -e "ssh -i $SSH_KEY_PATH" $REMOTE_USR@$REMOTE_HOST:$REMOTE_BLOCKCHAIN_PATH/blocks $BU_HOME/.bitcoin
  rsync --progress -a -e "ssh -i $SSH_KEY_PATH" $REMOTE_USR@$REMOTE_HOST:$REMOTE_BLOCKCHAIN_PATH/chainstate $BU_HOME/.bitcoin
EOH
  chown $USR.$USR -R $BU_HOME/.bitcoin
  echo "Synced!"
}

# default value for variuois mode
DW_MODE=0
CR_SWAP=1
REBOOT=0
SYNC=0
PRUNE=1

# add getopts parsing
while getopts "dnrsp" Opts; do
  case $Opts in
    d)
      #Download mode activated
      DW_MODE=1
      ;;
    n)
      #Disable swap creation
      CR_SWAP=0
      ;;
    r)
      #reboot the machien at the end
      REBOOT=1
      ;;
    s)
      #sync the chain
      SYNC=1
      ;;
    p)
      #toggle prune mode
      PRUNE=0
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done

### helper functions

check_root_sudo () {
  if [ "$(whoami)" != "root" ]; then
    echo "Please run as root, or use sudo"
    exit 1
  fi;
}

check_tmux_screen () {
  if [[ -v TERM && "$TERM" != "screen" ]]; then
    echo "Please run the script inside a terminal multiplexer (e.g. tmux, screen, ...)";
    echo "To install tmux use sudo apt-get install tmux"
    exit 1;
  else
    echo "Tmux/Screen detected"
  fi
}

check_user_exists() {
  user_exists=$(id -u $USR > /dev/null 2>&1; echo $?)
  if [ "$user_exists" == "1" ]; then
    echo "User $USR does not exist, create the account via adduser(8) before proceeding";
    exit 1;
  fi
}

#### main functions

install_prereq_comp () {
  echo -n "Updating Ubuntu ... "
  # removed ppa bitcon rep since wei don't need berkeley db

  apt-get -y -qq update
  echo "done."
  echo -n "Installing BU prereq via apt-get ..."
  echo -en " done.\nInstalling git ..."
  sudo apt-get -qq -y install git > /dev/null
  echo -en " done.\nInstalling build-essentials and friends ..."
  sudo apt-get -qq -y install build-essential libtool autotools-dev automake pkg-config > /dev/null
  echo -en " done.\nInstalling helper libs ..."
  sudo apt-get -qq -y install libssl-dev libevent-dev bsdmainutils libboost-all-dev > /dev/null
  echo -n " done."
}

install_prereq_down () {
  echo -n "Updating Ubuntu ... "
  # removed ppa bitcon rep since wei don't need berkeley db

  apt-get -y -qq update
  echo "done."
  echo -n "Installing BU prereq via apt-get ..."
  sudo apt-get -qq -y install curl > /dev/null
  echo " done."
}

create_swap () {
  echo -n "Creating Swap ... "
  SWAP_SIZE=`free -m | grep Mem | awk '{print $2}'`
  rm -f /swapfile
  fallocate -l ${SWAP_SIZE}M /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo "/swapfile swap swap defaults 0 0" >> /etc/fstab
  echo "done."
}


cloning () {
  echo "Cloning Bitcoin BU ... "
  sudo -u $USR bash <<-EOH
  cd $BU_HOME
  mkdir -p ./src && cd ./src
  git clone $BU_REPO BU > /dev/null
  cd BU
  git checkout $BU_BRANCH
EOH
  echo "done."
}

compiling () {
  echo -n "Compiling ... "
  sudo -u $USR bash <<-EOH
  cd $BU_HOME/src/BU
  ./autogen.sh
  ./configure --without-gui --without-upnp --disable-tests --disable-wallet --disable-zmq
  make -j$(grep -c '^processor' /proc/cpuinfo)
EOH
  cd $BU_HOME/src/BU
  make install
  echo " done."
}


downloading () {
  echo -n "Downloading BU ... "
  tmp_dir="/tmp/`< /dev/urandom tr -dc A-Za-z0-9 | head -c10`"
  mkdir $tmp_dir
  cd $tmp_dir
  # TODO use a switch to explictly list all support arch
  if [ "$(uname -m)" == "x86_64" ]; then
    bu_name="bu64.tar.gz"
    bu_url=$BU_URL64
    bu_sum=$BU_SUM64
  else
    bu_name="bu32.tar.gz"
    bu_url=$BU_URL32
    bu_sum=$BU_SUM32
  fi;
  curl -s -L --max-redirs 2 -o $bu_name $bu_url
  echo " done."
  echo -n "Verify check sum ... "
  bu_real_sum=`sha256sum $bu_name | awk '{print $1}'`
  if [ "$bu_real_sum" != "$bu_sum" ]; then
    echo "SHA256 mismatch! Aborting!"
    echo "Expected archive sha256 checksum is $bu_sum, whereas this what we got: $bu_real_sum"
  fi;
  echo " done."

  echo -n "Installing in /usr/local/bin ... "
  tmp_path=`tar tf $bu_name | head -n1 | awk -F '/' '{print $1}'`
  tar xf $bu_name
  cp $tmp_path/bin/* /usr/local/bin
  rm -rf $tmp_path
  echo " done."
}

setting_up () {

  echo -n "Setting up bitcoind datadir and conf file ..."
  echo " done."
  echo -n "Creating config ... "
  su $USR -c "mkdir -p ${BU_HOME}/.bitcoin"

  config="${BU_HOME}/.bitcoin/bitcoin.conf"
  su $USR -c "touch $config"
  echo "server=1" > $config
  echo "daemon=1" >> $config
  echo "checkblocks=7" >> $config
  echo "logtimemicros=1" >> $config
  echo "connections=40" >> $config
  echo "dbcache=200" >> $config

  # rpc credentials
  randUser=`< /dev/urandom tr -dc A-Za-z0-9 | head -c30`
  randPass=`< /dev/urandom tr -dc A-Za-z0-9 | head -c30`
  echo "rpcuser=$randUser" >> $config
  echo "rpcpassword=$randPass" >> $config

  # set prune amount to size of `/` 70% free space (and then by /1000 to turn KB to MB) => ~ /1429
  if [ "$PRUNE" == "1" ]; then
    echo "prune="$(expr $(df | grep '/$' | tr -s ' ' | cut -d ' ' -f 4) / 1429) >> $config # safe enough for now
  fi;

  chown $USR.$USR -R $BU_HOME/.bitcoin
  echo "done."
}


start_at_boot () {
  echo -n "Setting bitcoind to start at boot ... "
  LN=`wc -l /etc/rc.local | awk '{print $1}'`
  BU_INIT="su ${USR} -c '/usr/local/bin/bitcoind -datadir=${BU_HOME}/.bitcoin -daemon'"
  sed -i "${LN}i $BU_INIT" /etc/rc.local
  echo "done."
}

### main
# mandatory checks

check_root_sudo
check_tmux_screen
check_user_exists

# main
if [ "$CR_SWAP" == "1" ]; then
  create_swap
fi;

if [ "$DW_MODE" == "0" ]; then
  install_prereq_comp
  cloning
  compiling
else
  install_prereq_down
  downloading
fi;

# starting box configuration
setting_up
start_at_boot

# sync the blockchain this will take a long while
if [ "$SYNC" == "1" ]; then
  sync_chain
fi;

echo "Finished."

if [ "$REBOOT" == "1" ]; then
  echo "Rebooting now ..."
  reboot
else
  echo "To start your bitcoind: sudo su ${USR} -c '/usr/local/bin/bitcoind -datadir=${BU_HOME}/.bitcoin -daemon'"
fi
