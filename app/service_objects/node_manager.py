
from abc import ABC, abstractmethod
from flask import current_app
from app.utils.ssh import ssh_scope
from scp import SCPClient

class NodeManager(ABC):
    @abstractmethod
    def create_server_from_latest_snapshot(self):
        """
        Clones a new server from the latest template snapshot
        """
        pass

    @abstractmethod
    def create_server(self):
        """
        Creates a new instance.
        NOTE: Does not update the db.
        """

    @abstractmethod
    def update_provider_attributes(self):
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

    @abstractmethod
    def open_bitcoind_port(self):
        """
        Open port 8333 for bitcoind
        """
        pass

    @abstractmethod
    def destroy_server(self):
        """
        Destroys the node
        """
        pass

    def install_bitcoind(self):
        """
        Installs Bitcoind on the node
        """
        # use the default user on each provider for setup
        if self.node.provider == 'digital_ocean':
            os_user = 'root'
        elif self.node.provider == 'aws':
            os_user = 'ubuntu'
        else:
            raise Exception('Error: provider not supported')

        with ssh_scope(self.node.ipv4_address, os_user) as client:
            with SCPClient(client.get_transport()) as scp:
                scp.put('scripts/bu.sh', '/tmp/')

            client.exec_command('chmod 744 /tmp/bu.sh')

            command = "tmux new-session -d -s bu 'sudo "
            command += "ADOPTANODE_USER={adoptanode_user} ".format(adoptanode_user=current_app.config['ADOPTANODE_USER'])
            command += "ADOPTANODE_PASSWORD={adoptanode_password} ".format(adoptanode_password=current_app.config['ADOPTANODE_PASSWORD'])
            command += "ADOPTANODE_SMTP_EMAIL={adoptanode_smtp_email} ".format(adoptanode_smtp_email=current_app.config['ADOPTANODE_SMTP_EMAIL'])
            command += "ADOPTANODE_SMTP_PASSWORD={adoptanode_smtp_password} ".format(adoptanode_smtp_password=current_app.config['ADOPTANODE_SMTP_PASSWORD'])
            command +=  "/tmp/bu.sh'"
            client.exec_command(command)

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
            client.exec_command('sudo service bitcoind stop;')
        return

    def start_bitcoind(self):
        """
        Starts bitcoind on the node.
        """
        with ssh_scope(self.node.ipv4_address, current_app.config['OS_USER']) as client:
            client.exec_command('sudo service bitcoind start;')
        return

    def restart_bitcoind(self):
        """
        Restarts bitcoind on the node.
        """
        with ssh_scope(self.node.ipv4_address, current_app.config['OS_USER']) as client:
            client.exec_command('sudo service bitcoind restart;')
        return

    def update_bitcoin_conf(self):
        """
        Updates .bitcoin/bitcoin.conf values to match the node record in the db.
        """
        # updating eb
        eb = str(int(self.node.bu_eb * 1000000))
        eb_sed_params = "s/excessiveblocksize.*/excessiveblocksize={eb}/".format(eb=eb)
        eb_command = "sudo sed -i -e '{sed_params}' /var/lib/bitcoind/bitcoin.conf".format(sed_params=eb_sed_params)

        # updating ad
        ad = str(self.node.bu_ad)
        ad_sed_params = "s/excessiveacceptdepth.*/excessiveacceptdepth={ad}/".format(ad=ad)
        ad_command = "sudo sed -i -e '{sed_params}' /var/lib/bitcoind/bitcoin.conf".format(sed_params=ad_sed_params)

        # updating net.subversionOverride
        eb = str(int(self.node.bu_eb))
        ad = str(self.node.bu_ad)
        name = self.node.name
        version = self.node.bu_version
        subversion_sed_params = "s/net.subversionOverride.*/net.subversionOverride=\/BitcoinUnlimited:{version}(EB{eb}; AD{ad}) {name}\//".format(version=version, eb=eb, ad=ad, name=name)
        subversion_command = "sudo sed -i -e '{sed_params}' /var/lib/bitcoind/bitcoin.conf".format(sed_params=subversion_sed_params)

        with ssh_scope(self.node.ipv4_address, current_app.config['OS_USER']) as client:
            client.exec_command(eb_command)
            client.exec_command(ad_command)
            client.exec_command(subversion_command)

        return

    def update_server(self):
        with ssh_scope(self.node.ipv4_address, current_app.config['OS_USER']) as client:
            client.exec_command('sudo apt-get -y update & sudo apt-get -y -f upgrade & sudo reboot')
