
import paramiko

from abc import ABC, abstractmethod

class NodeManager(ABC):
    @abstractmethod
    def create_droplet_from_template(self):
        pass

    @abstractmethod
    def get_provider_attributes(self):
        pass

    @abstractmethod
    def take_snapshot(self):
        pass

    def poweroff(self):
        """
        Powers off the node.
        """
        self._execute_command_via_ssh('bitcoin-cli stop; sleep 20; sudo poweroff;')
        return

    def stop_bitcoind(self):
        """
        Stops bitcoind on the node.
        """
        self._execute_command_via_ssh('bitcoin-cli stop')
        return

    def start_bitcoind(self):
        """
        Starts bitcoind on the node.
        """
        # TODO: doesn't work. bu user needs password-less sudo privileges.
        self._execute_command_via_ssh('bitcoind -daemon; exit')
        return

    def restart_bitcoind(self):
        """
        Restarts bitcoind on the node.
        """
        self._execute_command_via_ssh('bitcoin-cli stop; sleep 20; bitcoind -daemon; exit')
        return

    def update_bitcoin_conf(self):
        """
        Updates .bitcoin/bitcoin.conf values to match the node record in the db.
        """
        # updating eb
        eb = str(self.node.bu_eb * 1000000)
        sed_params = "s/excessiveblocksize=[[:digit:]]*/excessiveblocksize={eb}/".format(eb=eb)
        command = "sed -i -e '{sed_params}' .bitcoin/bitcoin.conf".format(sed_params=sed_params)
        self._execute_command_via_ssh(command)

        # updating ad
        ad = str(self.node.bu_ad)
        sed_params = "s/excessiveacceptdepth=[[:digit:]]*/excessiveacceptdepth={ad}/".format(ad=ad)
        command = "sed -i -e '{sed_params}' .bitcoin/bitcoin.conf".format(sed_params=sed_params)
        self._execute_command_via_ssh(command)

        # updating net.subversionOverride
        eb = str(int(self.node.bu_eb))
        ad = str(self.node.bu_ad)
        name = self.node.name
        version = self.node.bu_version
        sed_params = "s/net.subversionOverride.*/net.subversionOverride=\/BitcoinUnlimited:{version}(EB{eb}; AD{ad}) {name}\//".format(version=version, eb=eb, ad=ad, name=name)
        command = "sed -i -e '{sed_params}' .bitcoin/bitcoin.conf".format(sed_params=sed_params)
        self._execute_command_via_ssh(command)

        return

    def _execute_command_via_ssh(self, command):
        """
        Executes the provided shell command on the node via SSH.
        """
        client = paramiko.SSHClient()

        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(self.node.ipv4_address, username='bu')

        stdin, stdout, stderr = client.exec_command(command)

        client.close()
        return
