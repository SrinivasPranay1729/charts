import paramiko

def ssh_to_instance(host_ip, username, password):
    # Create the SSH client
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the instance
    try:
        ssh_client.connect(host_ip, username=username, password=password)
        print(f"Connected to {host_ip}")

        # Execute commands (example: list files)
        stdin, stdout, stderr = ssh_client.exec_command('ls -l')
        output = stdout.read().decode()
        print(output)

    except Exception as e:
        print(f"Failed to connect: {e}")

    finally:
        ssh_client.close()

# Usage example
host_ip = "YOUR_EC2_IP_ADDRESS"
username = "YOUR_USERNAME"
password = "YOUR_PASSWORD_OR_TOKEN"

ssh_to_instance(host_ip, username, password)