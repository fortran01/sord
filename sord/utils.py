import socket
import os


def check_local_port_availability(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("", port))
            return True
        except socket.error as e:
            print(f"Port {port} is already in use by another process. Error: {e}")
            return False

def create_rdp_file(instance_id, local_port, file_name="connection.rdp"):
    """
    Creates an RDP file for connecting to an EC2 instance and returns the file path.

    :param instance_id: The ID of the EC2 instance to connect to.
    :param local_port: The local port on which the RDP session is established.
    :param file_name: The name of the RDP file to be saved. Defaults to 'connection.rdp'.
    :return: The path to the created RDP file.
    """
    file_path = os.path.join(os.path.expanduser("~"), "Downloads", file_name)
    rdp_content = f"""
    auto connect:i:1
    full address:s:localhost:{local_port}
    prompt for credentials:i:1
    username:s:Administrator
    """

    try:
        with open(file_path, "w") as rdp_file:
            rdp_file.write(rdp_content.strip())
        print(
            f"RDP file created successfully at {file_path} for instance {instance_id}."
        )
        return file_path
    except Exception as e:
        print(f"Failed to create RDP file: {e}")
        return None
