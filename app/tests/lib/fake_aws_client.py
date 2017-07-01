
class FakeAwsClient:
    def __init__(self, resource, aws_access_key_id, aws_secret_access_key, region_name):
        return

    def describe_images(*args, **kwargs):
        """
        Returns a list of AWS images
        """
        response = {'Images':
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

        return(response)

    def run_instances(*args, **kwargs):
        """
        Launches new instances on AWS
        """
        response = {
            'Groups': [],
            'Instances': [{
                'AmiLaunchIndex': 0, 'ImageId': 'ami-35e0f14c', 'InstanceId': 'i-test123',
                'InstanceType': 't2.micro', 'KeyName': 'bu-keypair-uswest2',
                'Monitoring': {'State': 'disabled'},
                'Placement': {'AvailabilityZone': 'us-west-2a', 'GroupName': '', 'Tenancy': 'default'},
                'PrivateDnsName': 'ip-10-0-0-71.us-west-2.compute.internal', 'PrivateIpAddress': '10.0.0.71',
                'ProductCodes': [], 'PublicDnsName': '',
                'State': {'Code': 0, 'Name': 'pending'},
                'StateTransitionReason': '', 'SubnetId': 'subnet-0b33196c',
                'VpcId': 'vpc-e5889682', 'Architecture': 'x86_64',
                'BlockDeviceMappings': [], 'ClientToken': '', 'EbsOptimized': False, 'Hypervisor': 'xen',
                'NetworkInterfaces': [{
                    'Attachment': {
                        'AttachmentId': 'eni-attach-b4c08d5c',
                        'DeleteOnTermination': True, 'DeviceIndex': 0,
                        'Status': 'attaching'
                    },
                    'Description': '',
                    'Groups': [{
                        'GroupName': 'bu_SG_uswest2', 'GroupId': 'sg-841e33ff'
                    }], 'Ipv6Addresses': [], 'MacAddress': '02:c9:ab:7b:ac:b8',
                    'NetworkInterfaceId': 'eni-a65c2a8b', 'OwnerId': '870168114151',
                    'PrivateDnsName': 'ip-10-0-0-71.us-west-2.compute.internal',
                    'PrivateIpAddress': '10.0.0.71', 'PrivateIpAddresses': [{
                        'Primary': True, 'PrivateDnsName': 'ip-10-0-0-71.us-west-2.compute.internal',
                        'PrivateIpAddress': '10.0.0.71'
                    }], 'SourceDestCheck': True, 'Status': 'in-use',
                    'SubnetId': 'subnet-0b33196c', 'VpcId': 'vpc-e5889682'
                }],
                'RootDeviceName': '/dev/sda1', 'RootDeviceType': 'ebs',
                'SecurityGroups': [{'GroupName': 'bu_SG_uswest2', 'GroupId': 'sg-841e33ff'}],
                'SourceDestCheck': True,
                'StateReason': {'Code': 'pending', 'Message': 'pending'}, 'VirtualizationType': 'hvm'
            }],
            'OwnerId': '870168114151', 'ReservationId': 'r-0073b0ad807ed0204',
            'ResponseMetadata': {
                'RequestId': '620c1a65-08eb-4840-bd4c-417c0d28d344', 'HTTPStatusCode': 200,
                'HTTPHeaders': {
                    'content-type': 'text/xml;charset=UTF-8', 'transfer-encoding': 'chunked',
                    'vary': 'Accept-Encoding', 'date': 'Sat, 01 Jul 2017 21:13:10 GMT',
                    'server': 'AmazonEC2'
                },
                'RetryAttempts': 0
            }
        }

        return(response)

    def describe_instances(*args, **kwargs):
        """
        Returns a list of AWS instances
        """
        response = {
            'Reservations': [{
                'Groups': [],
                'Instances': [{
                    'AmiLaunchIndex': 0, 'ImageId': 'ami-35e0f14c', 'InstanceId': 'i-test-instance',
                    'InstanceType': 't2.micro', 'KeyName': 'bu-keypair-uswest2',
                    'Monitoring': {'State': 'disabled'},
                    'Placement': {'AvailabilityZone': 'us-west-2a', 'GroupName': '', 'Tenancy': 'default'},
                    'PrivateDnsName': 'ip-10-0-0-220.us-west-2.compute.internal',
                    'PrivateIpAddress': '10.0.0.220', 'ProductCodes': [],
                    'PublicDnsName': '',
                    'State': {'Code': 80, 'Name': 'stopped'},
                    'StateTransitionReason': 'User initiated (2017-07-01 22:53:08 GMT)',
                    'SubnetId': 'subnet-0b33196c', 'VpcId': 'vpc-e5889682',
                    'Architecture': 'x86_64', 'BlockDeviceMappings': [{
                        'DeviceName': '/dev/sda1', 'Ebs': {
                            'DeleteOnTermination': True, 'Status': 'attached',
                            'VolumeId': 'vol-0d5ab0d9de3dbb261'
                        }
                    }],
                    'ClientToken': '', 'EbsOptimized': False, 'EnaSupport': True,
                    'Hypervisor': 'xen', 'NetworkInterfaces': [{
                        'Attachment': {
                            'AttachmentId': 'eni-attach-22c68bca', 'DeleteOnTermination': True,
                            'DeviceIndex': 0, 'Status': 'attached'
                        },
                        'Description': '',
                        'Groups': [{
                            'GroupName': 'bu_SG_uswest2', 'GroupId': 'sg-841e33ff'
                        }],
                        'Ipv6Addresses': [], 'MacAddress': '02:49:0d:19:8c:82',
                        'NetworkInterfaceId': 'eni-0e502623', 'OwnerId': '870168114151',
                        'PrivateDnsName': 'ip-10-0-0-220.us-west-2.compute.internal',
                        'PrivateIpAddress': '10.0.0.220', 'PrivateIpAddresses': [{
                            'Primary': True, 'PrivateDnsName': 'ip-10-0-0-220.us-west-2.compute.internal',
                            'PrivateIpAddress': '10.0.0.220'
                        }],
                        'SourceDestCheck': True, 'Status': 'in-use',
                        'SubnetId': 'subnet-0b33196c', 'VpcId': 'vpc-e5889682'
                    }],
                    'RootDeviceName': '/dev/sda1', 'RootDeviceType': 'ebs',
                    'SecurityGroups': [{
                        'GroupName': 'bu_SG_uswest2', 'GroupId': 'sg-841e33ff'
                    }],
                    'SourceDestCheck': True,
                    'StateReason': {
                        'Code': 'Client.UserInitiatedShutdown',
                        'Message': 'Client.UserInitiatedShutdown: User initiated shutdown'
                    }, 'VirtualizationType': 'hvm'
                }],
                'OwnerId': '870168114151', 'ReservationId': 'r-01beabb7681060c8b'
            }],
            'ResponseMetadata': {}
        }

        return(response)
