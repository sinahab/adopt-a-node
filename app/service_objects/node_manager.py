
from abc import ABC, abstractmethod

class NodeManager(ABC):
    @abstractmethod
    def create_droplet_from_template(self):
        pass

    @abstractmethod
    def update_provider_attributes(self):
        pass

    @abstractmethod
    def take_snapshot(self):
        pass

    def run_bitcoind(self):
        pass

    def poweroff(self):
        # bitcoin-cli stop
        # sudo poweroff
        return
