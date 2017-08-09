
## To update Bitcoind in nodes

Follow these steps:

1. In `/app/models/node.py`, update the `BU_VERSION` contant.

2. In `/scripts/update.sh`, update the `BITCOIN_URL`.
3. In `/scripts/update.sh`, update the default subversionOverride version in bitcoin.conf. It starts with: `net.subversionOverride=/BitcoinUnlimited`

4. Update bitcoind on the node, as follows:
```
node = Node.query.get(10)
node.update_bitcoind()
```

Or, if you want to do it for all nodes:
```
nodes = Node.query.filter_by(status='up')

for node in nodes:
    node.update_bitcoind()
```
