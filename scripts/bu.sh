#!/bin/bash

## redirect stdout to a log file

exec > /tmp/deploy_log.txt

## UPDATE THE SYSTEM

NODE_TYPE=pruned
BITCOIN_URL="https://github.com/BitcoinUnlimited/BitcoinUnlimitedWebDownloads/raw/master/bitcoinUnlimited-1.0.3.0-linux64.tar.gz"
BLK_URL="http://5.189.177.233/~sickpig/blk.tgz"
NODE_USER=$ADOPTANODE_USER
NODE_PASSWORD=$ADOPTANODE_PASSWORD
NODE_SMTP_EMAIL=$ADOPTANODE_SMTP_EMAIL
NODE_SMTP_PASSWORD=$ADOPTANODE_SMTP_PASSWORD

DEBIAN_FRONTEND=noninteractive apt-get -y update
DEBIAN_FRONTEND=noninteractive apt-get -y upgrade

DEBIAN_FRONTEND=noninteractive apt-get -y install vim htop
DEBIAN_FRONTEND=noninteractive apt-get -y autoremove

## PREPARE BU INSTALLATION

adduser --disabled-password --gecos "" --home /var/lib/bitcoind bitcoind

adduser --disabled-password --gecos "" $NODE_USER

# disable ssh root login

echo "$NODE_USER:$NODE_PASSWORD" | chpasswd
echo "bitcoind:$NODE_PASSWORD" | chpasswd
usermod -aG sudo $NODE_USER
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
service ssh reload

## No pwd for sudo

cp /etc/sudoers /etc/sudoers.bak
cp /etc/sudoers /etc/sudoers.tmp

chmod 0640 /etc/sudoers.tmp
echo "bitcoind ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.tmp
echo "bu ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.tmp
chmod 0440 /etc/sudoers.tmp
cp /etc/sudoers.tmp /etc/sudoers

# ssh key exchange
mkdir /home/bu/.ssh
cat << EOF > /home/bu/.ssh/authorized_keys
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSZjAx/X6Awq6JhMLvnfg0FvZr3BZtbAsLOrBQBPQ3GjhcS/KONRERmHjo3XHIH3eBJ/IqlnP3pNHoOAohQL5PJVmDTg6u7EmERyLYdtx25tVaDf3JnnLuHNDAehpJF4z3GV6ROwh5Bxmk6+Mvi/W1zyrC/FNuw38g4hTgA/sb4DMbjvxP4xl98CzPLlvV5m2SPfyqGXhPW7ip2fj6kIpdGcM9Iyz9A5MVq7qDZKsbYdDf4UiLXpj1NnXgRqoPnQtjauzeln4s2g8W1k1tiXWwOAV9EC7dsvB2+WVhECFhMf8Mk+pMOdAVfyCmyOSpSdweRfLDDDMPOQUN9wRYn/Bh sickpig@lenovo

ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQD8iDtzcaRQxecg2nuKJCwHjnhxzs/40/fQm6z3cw8NI+clMfrluvlTNXiyPk5JCWrJIGpTMSB+gmMQoIYTNohbkPdNM7x5I9BAIgOqwJfvIr8d2UmNxGSKhtlKPW1xP5fb/oyT7GA0UjsZyXJNNVINrmuQM5zpokbZ00fQVRYyaMe9Lw8YdppVHS/Z48qO/45mLRyB77FKHaKStp60XSAgVg/6jW7H/GTLauVIDKHtwJyhhEZjwJPTgPxG5DoT7PVrAH4vnYzgmQi+eZxTokGEmWMRapQIgDmCD7qwf3LGfPhccmMxrsUoQYxgrQB/IP3cZS0EQ1unwzoK1AWXxQzJt7bBUIFJUBtLrflCTzdx6/i/GUSbTtG8hOXuoNSLaqu67xqNDIbaOnw5tZZdRzQDSwJChc4Ok0iURT/88FC/qo+e0tyv+FI/aqtXvlZPeN7qV5G4bExTRm+ExxKjDTdkFNr6JzB5im0MkkZanPEYeLvrrPi1aVslMU/R45Q6IS3gNYLXOYTx/Ihc7fhmR7xRVzevUqtWiuQlHNurpJiVeYjkJTV3rZUALVZTF97z1jxNR6Bqp5oBvjiyze6JL+AyOsS3lMpIvCY+eaoOe9SnGyliwHk8t1KI0W+pl783JUKC2H+KR3mQVAWmv5a1vmeXr+CcR3KuZIbmtOC9vjBM/Q== bu.adoptanode@gmail.com
EOF
chown bu.bu -R /home/bu/.ssh/
chmod 600 /home/bu/.ssh/authorized_keys

# install BU

wget "$BITCOIN_URL" -O bitcoin.tar.gz
tar -xzf bitcoin.tar.gz

install bitcoin*-*.*.*/bin/* /usr/local/bin/

rm -rf bitcoin*

wget "$BLK_URL" -O blk.tgz
tar xzf blk.tgz
chown bitcoind.bitcoind -R blk
cp -a blk/* /var/lib/bitcoind/
chown bitcoind.bitcoind -R  /var/lib/bitcoind/
rm -rf blk
rm -rf blk.tgz

# Configuring BU

cat << EOF > /var/lib/bitcoind/bitcoin.conf
rpcuser=bitcoinrpc
rpcpassword=$(dd if=/dev/urandom bs=1 count=32 2>/dev/null | base64 -w 0 | rev | cut -b 2- | rev)
pid=/var/lib/bitcoind/bitcoind.pid
datadir=/var/lib/bitcoind
prune=550
excessiveblocksize=16000000
excessiveacceptdepth=12
net.subversionOverride=/BitcoinUnlimited:v1.0.3(EB16; AD12) template/
maxoutconnections=20
maxconnections=100
checkblocks=7
bitnodes=0
debug=thin
dbcache=100
forcednsseed=1
usednsseed=seed.bitcoinunlimited.info

onion=127.0.0.1:9050
listen=1
listenonion=1
discover=1
torcontrol=127.0.0.1:9051
torpassword=16:BDFD53721E63DFDB6028616C543779F454B574D63FA92B800C941B90A4


mempoolexpiry=216
maxlimitertxfee=1
maxmempool=1500
maxorphantx=10000
maxlimitertxfee=1
EOF

chown bitcoind:bitcoind /var/lib/bitcoind/bitcoin.conf

mkdir -p /usr/local/lib/systemd/system/

# Installing TOR

DEBIAN_FRONTEND=noninteractive apt-get install tor -y

adduser bu debian-tor
adduser bitcoind debian-tor

echo "ControlPort 9051" >> /etc/tor/torrc
echo "CookieAuthentication 1" >> /etc/tor/torrc
echo "HashedControlPassword 16:BDFD53721E63DFDB6028616C543779F454B574D63FA92B800C941B90A4" >> /etc/tor/torrc

systemctl restart tor

# install Postfix and set up relay system

DEBIAN_FRONTEND=noninteractive apt-get install postfix -y

cat << EOF > /etc/postfix/main.cf
relayhost = [smtp.gmail.com]:587
smtp_use_tls = yes
smtp_sasl_auth_enable = yes
smtp_sasl_security_options =
smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd
smtp_tls_CAfile = /etc/ssl/certs/ca-certificates.crt
EOF

cat << EOF > /etc/postfix/sasl_passwd
[smtp.gmail.com]:587    bu.adoptanode@gmail.com:bEvcYY2PEyfHNQgaZeimCURTx2Z3fzz
EOF

postmap /etc/postfix/sasl_passwd
sudo service postfix reload


# Setting up systemd for BU

cat << EOF > /etc/systemd/system/unit-status-mail@.service
[Unit]
Description=Unit Status Mailer Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/unit-status-mail.sh %i "Hostname: %H" "Machine ID: %m" "Boot ID: %b"
EOF

# Need to fixed due to variable interpolation and mixing of E O F
cat <<-'EOF' > /usr/local/bin/unit-status-mail.sh
#!/bin/bash
MAILTO="sickpig@gmail.com"
MAILFROM="unit-status-mailer"
UNIT=$1

EXTRA=""
for e in "${@:2}"; do
EXTRA+="$e"$'\n'
done

UNITSTATUS=$(systemctl status $UNIT)

sendmail $MAILTO <<EOHH
From:$MAILFROM
To:$MAILTO
Subject: [BU CRASHED] $2

Status report for unit: $UNIT
$EXTRA

$UNITSTATUS
EOHH

echo -e "Status mail sent to: $MAILTO for unit: $UNIT"
EOF

chmod +x /usr/local/bin/unit-status-mail.sh

cat << EOF > /lib/systemd/system/bitcoind.service
[Unit]
Description=Bitcoin BU Node / bitcoind
After=network.target
OnFailure=unit-status-mail@%n

[Service]
Type=forking
User=bitcoind
ExecStart=/usr/local/bin/bitcoind -conf=/var/lib/bitcoind/bitcoin.conf -disablewallet -daemon
ExecStop=/usr/local/bin/bitcoin-cli -conf=/var/lib/bitcoind/bitcoin.conf stop
PIDFile=/var/lib/bitcoind/bitcoind.pid

Restart=always
PrivateTmp=true
TimeoutStopSec=60s
TimeoutStartSec=2s
StartLimitInterval=120s
StartLimitBurst=5


[Install]
WantedBy=multi-user.target
EOF

echo -n "Creating Swap ... "
SWAP_SIZE=`free -m | grep Mem | awk '{print $2}'`
rm -f /swapfile
fallocate -l ${SWAP_SIZE}M /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo "/swapfile swap swap defaults 0 0" >> /etc/fstab
echo "done."

systemctl daemon-reload
systemctl enable bitcoind
systemctl start bitcoind
