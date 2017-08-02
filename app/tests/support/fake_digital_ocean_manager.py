
from app.utils.misc import DotDict

def rebuild(*args, **kwargs):
    return

class FakeDigitalOceanManager:
    def __init__(self, token):
        return

    def get_droplet_snapshots(self):
        snapshot_one = DotDict({
            'id': '123',
            'name': 'asd123',
            'created_at': '2017-07-12T15:50:50Z',
            'regions': ['sfo2'],
            'resource_id': '123',
            'resource_type': 'droplet',
            'min_disk_size': 30,
            'size_gigabytes': 26.37,
            'token': 'asdfasdf',
            'end_point': 'https://api.digitalocean.com/v2/'
        })

        snapshot_two = DotDict({
            'id': '456',
            'name': 'asd123',
            'created_at': '2018-07-12T15:50:50Z',
            'regions': ['sfo2'],
            'resource_id': '456',
            'resource_type': 'droplet',
            'min_disk_size': 30,
            'size_gigabytes': 26.37,
            'token': 'asdfasdf',
            'end_point': 'https://api.digitalocean.com/v2/'
        })

        snapshots = [snapshot_one, snapshot_two]
        return(snapshots)

    def get_droplet(self):
        droplet = DotDict({
            'name' : 'mylilnode',
            'ip_address' : '127.0.0.4',
            'status': 'exploding',
            'log': 'bla'
        })

        droplet.rebuild = rebuild

        return(droplet)
