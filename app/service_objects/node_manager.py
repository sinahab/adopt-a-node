
from abc import ABC, abstractmethod
from flask import current_app
from ..utils.ssh import ssh_scope

class NodeManager(ABC):
    @abstractmethod
    def create_droplet_from_latest_snapshot(self):
        """
        Clones a new server from the latest template snapshot
        """
        pass

    @abstractmethod
    def get_provider_attributes(self):
        """
        Queries the provider and updates the node's data in the db accordingly
        """
        pass

    @abstractmethod
    def take_snapshot(self):
        """
        Creates a snapshot from the given server.
        """
        pass

    @abstractmethod
    def power_on(self):
        """
        Boots up the node
        """
        pass

    def power_off(self):
        """
        Powers off the node.
        """
        with ssh_scope(self.node.ipv4_address, current_app.config['OS_USER']) as client:
            client.exec_command('sudo poweroff;')
        return

    def stop_bitcoind(self):
        """
        Stops bitcoind on the node.
        """
        with ssh_scope(self.node.ipv4_address, current_app.config['OS_USER']) as client:
            client.exec_command('bitcoin-cli stop')
        return

    def start_bitcoind(self):
        """
        Starts bitcoind on the node.
        """
        with ssh_scope(self.node.ipv4_address, current_app.config['OS_USER']) as client:
            client.exec_command('bitcoind -daemon; exit')
        return

    def restart_bitcoind(self):
        """
        Restarts bitcoind on the node.
        """
        with ssh_scope(self.node.ipv4_address, current_app.config['OS_USER']) as client:
            client.exec_command('bitcoin-cli stop; sleep 20; bitcoind -daemon; exit')
        return

    def update_bitcoin_conf(self):
        """
        Updates .bitcoin/bitcoin.conf values to match the node record in the db.
        """
        # updating eb
        eb = str(int(self.node.bu_eb * 1000000))
        eb_sed_params = "s/excessiveblocksize.*/excessiveblocksize={eb}/".format(eb=eb)
        eb_command = "sed -i -e '{sed_params}' .bitcoin/bitcoin.conf".format(sed_params=eb_sed_params)

        # updating ad
        ad = str(self.node.bu_ad)
        ad_sed_params = "s/excessiveacceptdepth.*/excessiveacceptdepth={ad}/".format(ad=ad)
        ad_command = "sed -i -e '{sed_params}' .bitcoin/bitcoin.conf".format(sed_params=ad_sed_params)

        # updating net.subversionOverride
        eb = str(int(self.node.bu_eb))
        ad = str(self.node.bu_ad)
        name = self.node.name
        version = self.node.bu_version
        subversion_sed_params = "s/net.subversionOverride.*/net.subversionOverride=\/BitcoinUnlimited:{version}(EB{eb}; AD{ad}) {name}\//".format(version=version, eb=eb, ad=ad, name=name)
        subversion_command = "sed -i -e '{sed_params}' .bitcoin/bitcoin.conf".format(sed_params=subversion_sed_params)

        with ssh_scope(self.node.ipv4_address, current_app.config['OS_USER']) as client:
            client.exec_command(eb_command)
            client.exec_command(ad_command)
            client.exec_command(subversion_command)

        return
