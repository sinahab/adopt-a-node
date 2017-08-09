#!/bin/bash

## redirect stdout to a log file

exec > /tmp/deploy_log.txt

systemctl stop bitcoind

## UPDATE THE SYSTEM

BITCOIN_URL="https://github.com/BitcoinUnlimited/BitcoinUnlimitedWebDownloads/raw/master/bitcoinUnlimited-1.0.3.0-linux64.tar.gz"

DEBIAN_FRONTEND=noninteractive apt-get -y update
DEBIAN_FRONTEND=noninteractive apt-get -y upgrade

wget "$BITCOIN_URL" -O bitcoin.tar.gz
tar -xzf bitcoin.tar.gz

install bitcoin*-*.*.*/bin/* /usr/local/bin/

rm -rf bitcoin*

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

systemctl daemon-reload
systemctl restart bitcoind
