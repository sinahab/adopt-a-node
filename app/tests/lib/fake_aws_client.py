
class FakeAwsClient:
    def __init__(self, resource, aws_access_key_id, aws_secret_access_key, region_name):
        return

    def describe_images(*args, **kwargs):
        images = {'Images':
            [
                {
                    'Architecture': 'x86_64', 'CreationDate': '2017-07-01T18:52:24.000Z', 'ImageId': 'ami-test1',
                    'ImageLocation': '870168114151/1498935133', 'ImageType': 'machine', 'Public': False,
                    'OwnerId': '870168114151', 'State': 'pending', 'BlockDeviceMappings': [
                            {'DeviceName': '/dev/sda1', 'Ebs': {'Encrypted': False, 'DeleteOnTermination': True, 'SnapshotId': 'snap-00044c6fa130b6938', 'VolumeSize': 40, 'VolumeType': 'gp2'}}
                    ],
                    'Description': 'template', 'EnaSupport': True, 'Hypervisor': 'xen', 'Name': '1498935133',
                    'RootDeviceName': '/dev/sda1', 'RootDeviceType': 'ebs', 'SriovNetSupport': 'simple', 'VirtualizationType': 'hvm'
                 },
                 {
                    'Architecture': 'x86_64', 'CreationDate': '2017-07-01T19:20:53.000Z', 'ImageId': 'ami-test2',
                    'ImageLocation': '870168114151/1498936843', 'ImageType': 'machine', 'Public': False,
                    'OwnerId': '870168114151', 'State': 'available', 'BlockDeviceMappings': [
                        {'DeviceName': '/dev/sda1', 'Ebs': {'Encrypted': False, 'DeleteOnTermination': True, 'SnapshotId': 'snap-058ea42e563570ee6', 'VolumeSize': 40, 'VolumeType': 'gp2'}}
                    ],
                    'Description': 'template', 'EnaSupport': True, 'Hypervisor': 'xen', 'Name': '1498936843',
                    'RootDeviceName': '/dev/sda1', 'RootDeviceType': 'ebs', 'SriovNetSupport': 'simple', 'VirtualizationType': 'hvm'
                  }
            ],
            'ResponseMetadata': {
                'RequestId': '0ae03a55-8cf1-46ae-ad5f-32bb20614cd2', 'HTTPStatusCode': 200,
                'HTTPHeaders': {
                    'content-type': 'text/xml;charset=UTF-8', 'transfer-encoding': 'chunked',
                    'vary': 'Accept-Encoding', 'date': 'Sat, 01 Jul 2017 19:21:28 GMT', 'server': 'AmazonEC2'
                },
                'RetryAttempts': 0
            }
        }

        return(images)
