import boto3
import paramiko

client = boto3.client('ec2',)

# This method get all instance with Tag Name Backup
reservations = client.describe_instances(Filters=[{
    'Name': 'tag:Backup',
    'Values': ['Yes']
}]).get('Reservations', [])

instances = sum([[i for i in r['Instances']] for r in reservations], [])

totalNumberofInstance = len(instances)
print(f'Total Number of Instance to Backup {totalNumberofInstance}')

# Initialised Paramiko SSH Client
keySSH = paramiko.RSAKey.from_private_key_file(
    "Path to your Pem Key or SSH Key")
connectParmiko = paramiko.SSHClient()
connectParmiko.set_missing_host_key_policy(paramiko.AutoAddPolicy())

for instance in instances:
    # This Loop will get Username of Instance Database by looping over EC2 Tags
    for tag in instance['Tags']:
        if tag['Key'] == 'Username':
            username = tag.get('Value')    

    privateIpAddress = instance['PrivateIpAddress'] # Store Private IP Address for SSH to Server
    publicpAddress = instance['PublicIpAddress'] # Store Public IP Address for SSH to Server

    # Connect to Instance to put database in backup mode
    connectParmiko.connect(
        hostname=privateIpAddress, username=username, pkey=keySSH)
    stdin, stdout, stderr = connectParmiko.exec_command('echo "Hello World"')

    # Get volume id of all attached volume to ec2 machine of instance
    for volume in instance['BlockDeviceMappings']:
        if volume.get('Ebs', None) is None:
            continue
        vol_id = volume['Ebs']['VolumeId']
        # Calls Aws Snapshot API
        snapshot = client.create_snapshot(
         VolumeId=vol_id, Description='Sample Snapshot') 
    stdin, stdout, stderr = connectParmiko.exec_command()
    connectParmiko.close()