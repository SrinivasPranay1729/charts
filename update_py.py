import paramiko

def ssh_to_instance(host_ip, username, key_path, commands):
    # Load the private key
    key = paramiko.RSAKey.from_private_key_file(key_path)

    # Create the SSH client
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the instance
    try:
        ssh_client.connect(host_ip, username=username, pkey=key)
        print(f"Connected to {host_ip}")

        # Run each command in the list of commands
        for command in commands:
            stdin, stdout, stderr = ssh_client.exec_command(command)
            output = stdout.read().decode()
            print(f"Output of {command}:\n{output}")
    
    except Exception as e:
        print(f"Failed to connect: {e}")
    
    finally:
        ssh_client.close()

# Define the host, username, and key
host_ip = "YOUR_EC2_IP_ADDRESS"
username = "ec2-user"
key_path = "/path/to/your/private_key.pem"

# List of commands to run for backup
commands = [
    "sudo mount -o remount,exec /tmp/",
    "sudo mkdir -p /tmp/instance_backup/",
    "sudo chmod -R 777 /tmp/instance_backup/",
    # ... (rest of the commands you want to run)
    "aws s3 cp /tmp/instance_backup-backup.tar.gz s3://your-s3-bucket-name/b2c/"
]

ssh_to_instance(host_ip, username, key_path, commands)